"""
Web3 Threat Detection Engine
Detects various Web3-specific threats and attacks
"""

import time
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import redis
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 8
    CRITICAL = 10

class ThreatType(Enum):
    REPLAY_ATTACK = "replay_attack"
    FLASH_LOAN_EXPLOIT = "flash_loan_exploit"
    MEV_MANIPULATION = "mev_manipulation"
    RATE_LIMIT_ABUSE = "rate_limit_abuse"
    API_SCRAPING = "api_scraping"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    ANOMALOUS_AMOUNT = "anomalous_amount"

@dataclass
class ThreatAlert:
    threat_type: ThreatType
    threat_level: ThreatLevel
    description: str
    metadata: Dict
    timestamp: float
    api_key: str
    ip_address: Optional[str] = None

class ThreatDetector:
    """
    Detects Web3-specific threats and security issues
    """
    
    def __init__(self, redis_client: redis.Redis = None):
        self.redis = redis_client or redis.Redis(host='localhost', port=6379, db=2)
        
    def analyze_transaction_request(self, 
                                  api_key: str, 
                                  wallet_address: str, 
                                  transaction_data: Dict,
                                  ip_address: str = None) -> List[ThreatAlert]:
        """Analyze a transaction request for threats"""
        threats = []
        
        # 1. Replay Attack Detection
        replay_threat = self._detect_replay_attack(api_key, transaction_data)
        if replay_threat:
            threats.append(replay_threat)
        
        # 2. Flash Loan Detection
        flash_loan_threat = self._detect_flash_loan_pattern(wallet_address, transaction_data)
        if flash_loan_threat:
            threats.append(flash_loan_threat)
        
        # 3. Anomalous Amount Detection
        amount_threat = self._detect_anomalous_amount(wallet_address, transaction_data)
        if amount_threat:
            threats.append(amount_threat)
        
        # 4. Rate Limit Abuse
        if ip_address:
            rate_threat = self._detect_rate_abuse(api_key, ip_address)
            if rate_threat:
                threats.append(rate_threat)
        
        # 5. MEV/Sandwich Attack Detection
        mev_threat = self._detect_mev_pattern(wallet_address, transaction_data)
        if mev_threat:
            threats.append(mev_threat)
        
        # Log threats
        for threat in threats:
            self._log_threat(threat)
        
        return threats
    
    def _detect_replay_attack(self, api_key: str, transaction_data: Dict) -> Optional[ThreatAlert]:
        """Detect replay attacks using transaction signatures/hashes"""
        try:
            # Create transaction fingerprint
            tx_fingerprint = self._create_transaction_fingerprint(transaction_data)
            key = f"tx_fingerprint:{api_key}:{tx_fingerprint}"
            
            # Check if we've seen this exact transaction before
            if self.redis.exists(key):
                last_seen = self.redis.get(key).decode()
                time_diff = time.time() - float(last_seen)
                
                # If same transaction within 5 minutes = potential replay
                if time_diff < 300:  # 5 minutes
                    return ThreatAlert(
                        threat_type=ThreatType.REPLAY_ATTACK,
                        threat_level=ThreatLevel.HIGH,
                        description=f"Potential replay attack detected - identical transaction seen {time_diff:.1f}s ago",
                        metadata={
                            "tx_fingerprint": tx_fingerprint,
                            "time_diff": time_diff,
                            "last_seen": last_seen
                        },
                        timestamp=time.time(),
                        api_key=api_key
                    )
            
            # Store transaction fingerprint
            self.redis.setex(key, 3600, str(time.time()))  # Store for 1 hour
            
        except Exception as e:
            logger.error(f"Error in replay attack detection: {e}")
        
        return None
    
    def _detect_flash_loan_pattern(self, wallet_address: str, transaction_data: Dict) -> Optional[ThreatAlert]:
        """Detect potential flash loan exploitation patterns"""
        try:
            amount = transaction_data.get("amount", 0)
            
            # Flash loans typically involve very large amounts
            if amount > 1000000 * 1000000:  # > 1M ALGO in microAlgos
                # Check transaction frequency
                recent_tx_key = f"recent_tx:{wallet_address}"
                tx_count = self.redis.incr(recent_tx_key)
                self.redis.expire(recent_tx_key, 60)  # 1 minute window
                
                # Multiple large transactions in short time = suspicious
                if tx_count > 3:
                    return ThreatAlert(
                        threat_type=ThreatType.FLASH_LOAN_EXPLOIT,
                        threat_level=ThreatLevel.HIGH,
                        description=f"Potential flash loan exploit - {tx_count} large transactions in 1 minute",
                        metadata={
                            "amount": amount,
                            "tx_count": tx_count,
                            "wallet": wallet_address
                        },
                        timestamp=time.time(),
                        api_key=""
                    )
        
        except Exception as e:
            logger.error(f"Error in flash loan detection: {e}")
        
        return None
    
    def _detect_anomalous_amount(self, wallet_address: str, transaction_data: Dict) -> Optional[ThreatAlert]:
        """Detect anomalously large transaction amounts"""
        try:
            amount = transaction_data.get("amount", 0)
            
            # Get historical average for this wallet
            avg_key = f"avg_amount:{wallet_address}"
            historical_data = self.redis.get(avg_key)
            
            if historical_data:
                avg_amount = float(historical_data.decode())
                
                # If current amount is 100x larger than average = suspicious
                if amount > avg_amount * 100 and amount > 10 * 1000000:  # > 10 ALGO minimum
                    return ThreatAlert(
                        threat_type=ThreatType.ANOMALOUS_AMOUNT,
                        threat_level=ThreatLevel.MEDIUM,
                        description=f"Anomalous transaction amount - {amount/1000000:.2f} ALGO vs avg {avg_amount/1000000:.2f} ALGO",
                        metadata={
                            "amount": amount,
                            "avg_amount": avg_amount,
                            "ratio": amount / avg_amount
                        },
                        timestamp=time.time(),
                        api_key=""
                    )
            
            # Update running average
            self._update_amount_average(wallet_address, amount)
            
        except Exception as e:
            logger.error(f"Error in anomalous amount detection: {e}")
        
        return None
    
    def _detect_rate_abuse(self, api_key: str, ip_address: str) -> Optional[ThreatAlert]:
        """Detect rate limit abuse and suspicious API usage patterns"""
        try:
            # Check requests per minute from this IP
            ip_key = f"rate_ip:{ip_address}"
            ip_count = self.redis.incr(ip_key)
            self.redis.expire(ip_key, 60)
            
            # Check requests per minute from this API key
            key_rate_key = f"rate_key:{api_key}"
            key_count = self.redis.incr(key_rate_key)
            self.redis.expire(key_rate_key, 60)
            
            # Suspicious if > 300 requests per minute from single IP
            if ip_count > 300:
                return ThreatAlert(
                    threat_type=ThreatType.RATE_LIMIT_ABUSE,
                    threat_level=ThreatLevel.MEDIUM,
                    description=f"Rate limit abuse detected - {ip_count} requests/min from IP {ip_address}",
                    metadata={
                        "ip_count": ip_count,
                        "key_count": key_count,
                        "ip_address": ip_address
                    },
                    timestamp=time.time(),
                    api_key=api_key,
                    ip_address=ip_address
                )
            
        except Exception as e:
            logger.error(f"Error in rate abuse detection: {e}")
        
        return None
    
    def _detect_mev_pattern(self, wallet_address: str, transaction_data: Dict) -> Optional[ThreatAlert]:
        """Detect MEV (Maximal Extractable Value) attack patterns"""
        try:
            # Look for sandwich attack patterns
            # Multiple transactions with same wallet in short timeframe
            mev_key = f"mev_pattern:{wallet_address}"
            tx_timestamps = self.redis.lrange(mev_key, 0, -1)
            
            current_time = time.time()
            self.redis.lpush(mev_key, str(current_time))
            self.redis.expire(mev_key, 300)  # 5 minute window
            
            # Check for rapid-fire transactions (potential sandwich attack)
            recent_count = 0
            for ts_bytes in tx_timestamps:
                ts = float(ts_bytes.decode())
                if current_time - ts < 30:  # Within 30 seconds
                    recent_count += 1
            
            if recent_count >= 3:  # 3+ transactions in 30 seconds
                return ThreatAlert(
                    threat_type=ThreatType.MEV_MANIPULATION,
                    threat_level=ThreatLevel.MEDIUM,
                    description=f"Potential MEV/sandwich attack - {recent_count} transactions in 30s",
                    metadata={
                        "recent_count": recent_count,
                        "wallet": wallet_address,
                        "timeframe": "30s"
                    },
                    timestamp=time.time(),
                    api_key=""
                )
            
        except Exception as e:
            logger.error(f"Error in MEV detection: {e}")
        
        return None
    
    def _create_transaction_fingerprint(self, transaction_data: Dict) -> str:
        """Create unique fingerprint for transaction"""
        # Use key transaction fields to create fingerprint
        fingerprint_data = {
            "to": transaction_data.get("to", ""),
            "amount": transaction_data.get("amount", 0),
            "note": transaction_data.get("note", ""),
            "type": transaction_data.get("type", "")
        }
        
        fingerprint_str = str(sorted(fingerprint_data.items()))
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def _update_amount_average(self, wallet_address: str, amount: int):
        """Update running average of transaction amounts for wallet"""
        try:
            avg_key = f"avg_amount:{wallet_address}"
            count_key = f"avg_count:{wallet_address}"
            
            current_avg = float(self.redis.get(avg_key) or 0)
            current_count = int(self.redis.get(count_key) or 0)
            
            # Calculate new running average
            new_count = current_count + 1
            new_avg = ((current_avg * current_count) + amount) / new_count
            
            # Store new values
            self.redis.setex(avg_key, 86400 * 7, str(new_avg))  # Store for 1 week
            self.redis.setex(count_key, 86400 * 7, str(new_count))
            
        except Exception as e:
            logger.error(f"Error updating amount average: {e}")
    
    def _log_threat(self, threat: ThreatAlert):
        """Log threat alert to Redis and system logs"""
        try:
            # Store in Redis for dashboard/monitoring
            threat_key = f"threat:{int(threat.timestamp)}:{threat.api_key}"
            threat_data = {
                "type": threat.threat_type.value,
                "level": threat.threat_level.value,
                "description": threat.description,
                "metadata": str(threat.metadata),
                "ip_address": threat.ip_address or ""
            }
            
            self.redis.hset(threat_key, mapping=threat_data)
            self.redis.expire(threat_key, 86400 * 7)  # Keep for 1 week
            
            # System log
            logger.warning(f"THREAT DETECTED: {threat.threat_type.value} - {threat.description}")
            
        except Exception as e:
            logger.error(f"Error logging threat: {e}")
    
    def get_threat_summary(self, api_key: str, hours: int = 24) -> Dict:
        """Get threat summary for API key"""
        try:
            start_time = time.time() - (hours * 3600)
            threat_keys = self.redis.keys(f"threat:*:{api_key}")
            
            threats_by_type = {}
            total_threats = 0
            
            for key in threat_keys:
                threat_data = self.redis.hgetall(key)
                if not threat_data:
                    continue
                
                # Extract timestamp from key
                timestamp = int(key.decode().split(':')[1])
                if timestamp < start_time:
                    continue
                
                threat_type = threat_data.get(b"type", b"unknown").decode()
                threats_by_type[threat_type] = threats_by_type.get(threat_type, 0) + 1
                total_threats += 1
            
            return {
                "total_threats": total_threats,
                "threats_by_type": threats_by_type,
                "time_period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting threat summary: {e}")
            return {"total_threats": 0, "threats_by_type": {}, "time_period_hours": hours}
