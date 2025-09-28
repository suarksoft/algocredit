"""
Advanced Transaction Validation and Security
Validates Algorand transactions for security threats
"""

import hashlib
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import redis
import logging
from algosdk import encoding, transaction
import base64

logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    VALID = "valid"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    INVALID = "invalid"

class TransactionRisk(Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 8
    CRITICAL = 10

@dataclass
class ValidationReport:
    result: ValidationResult
    risk_score: float
    issues: List[str]
    metadata: Dict[str, Any]
    timestamp: float
    recommendations: List[str]

class TransactionValidator:
    """
    Advanced transaction validation for Web3 security
    """
    
    def __init__(self, redis_client: redis.Redis = None):
        self.redis = redis_client or redis.Redis(host='localhost', port=6379, db=4)
        
        # Known malicious addresses (would be updated from threat intelligence)
        self.blacklisted_addresses = set()
        
        # Known good addresses (exchanges, verified contracts)
        self.whitelisted_addresses = set([
            # Algorand Foundation addresses
            "Y76M3MSY6DKBRHBL7C3NNDXGS5IIMQVQVUAB6MP4XEMMGVF2QWNPL226CA",
            # Add more verified addresses
        ])
    
    def validate_transaction(self, 
                           wallet_address: str,
                           transaction_data: Dict,
                           api_key: str,
                           context: Dict = None) -> ValidationReport:
        """
        Comprehensive transaction validation
        """
        issues = []
        risk_score = 0.0
        recommendations = []
        metadata = {}
        
        try:
            # 1. Basic validation
            basic_issues, basic_risk = self._validate_basic_structure(transaction_data)
            issues.extend(basic_issues)
            risk_score += basic_risk
            
            # 2. Address validation
            address_issues, address_risk = self._validate_addresses(transaction_data)
            issues.extend(address_issues)
            risk_score += address_risk
            
            # 3. Amount validation
            amount_issues, amount_risk = self._validate_amounts(wallet_address, transaction_data)
            issues.extend(amount_issues)
            risk_score += amount_risk
            
            # 4. Replay attack detection
            replay_issues, replay_risk = self._detect_replay_attack(api_key, transaction_data)
            issues.extend(replay_issues)
            risk_score += replay_risk
            
            # 5. MEV/Sandwich attack detection
            mev_issues, mev_risk = self._detect_mev_attack(wallet_address, transaction_data)
            issues.extend(mev_issues)
            risk_score += mev_risk
            
            # 6. Flash loan detection
            flash_issues, flash_risk = self._detect_flash_loan_attack(wallet_address, transaction_data)
            issues.extend(flash_issues)
            risk_score += flash_risk
            
            # 7. Smart contract interaction validation
            contract_issues, contract_risk = self._validate_contract_interaction(transaction_data)
            issues.extend(contract_issues)
            risk_score += contract_risk
            
            # 8. Temporal analysis
            temporal_issues, temporal_risk = self._analyze_temporal_patterns(wallet_address, api_key)
            issues.extend(temporal_issues)
            risk_score += temporal_risk
            
            # Determine overall result
            if risk_score >= 8.0:
                result = ValidationResult.MALICIOUS
                recommendations.extend([
                    "Block transaction immediately",
                    "Investigate wallet address",
                    "Consider suspending API key"
                ])
            elif risk_score >= 5.0:
                result = ValidationResult.SUSPICIOUS
                recommendations.extend([
                    "Require additional verification",
                    "Monitor closely",
                    "Consider rate limiting"
                ])
            elif risk_score >= 2.0:
                result = ValidationResult.SUSPICIOUS
                recommendations.extend([
                    "Monitor transaction",
                    "Log for analysis"
                ])
            else:
                result = ValidationResult.VALID
                recommendations.append("Transaction appears safe")
            
            # Store validation result for learning
            self._store_validation_result(wallet_address, api_key, result, risk_score)
            
            return ValidationReport(
                result=result,
                risk_score=risk_score,
                issues=issues,
                metadata=metadata,
                timestamp=time.time(),
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in transaction validation: {e}")
            return ValidationReport(
                result=ValidationResult.INVALID,
                risk_score=10.0,
                issues=[f"Validation error: {str(e)}"],
                metadata={"error": str(e)},
                timestamp=time.time(),
                recommendations=["Block due to validation error"]
            )
    
    def _validate_basic_structure(self, transaction_data: Dict) -> Tuple[List[str], float]:
        """Validate basic transaction structure"""
        issues = []
        risk_score = 0.0
        
        # Required fields
        required_fields = ["type", "sender", "fee"]
        for field in required_fields:
            if field not in transaction_data:
                issues.append(f"Missing required field: {field}")
                risk_score += 2.0
        
        # Transaction type validation
        valid_types = ["pay", "keyreg", "acfg", "axfer", "afrz", "appl"]
        tx_type = transaction_data.get("type")
        if tx_type and tx_type not in valid_types:
            issues.append(f"Invalid transaction type: {tx_type}")
            risk_score += 3.0
        
        # Fee validation
        fee = transaction_data.get("fee", 0)
        if fee < 1000:  # Minimum fee
            issues.append("Transaction fee too low")
            risk_score += 1.0
        elif fee > 10000:  # Suspiciously high fee
            issues.append("Transaction fee unusually high")
            risk_score += 2.0
        
        return issues, risk_score
    
    def _validate_addresses(self, transaction_data: Dict) -> Tuple[List[str], float]:
        """Validate wallet addresses in transaction"""
        issues = []
        risk_score = 0.0
        
        # Check sender address
        sender = transaction_data.get("sender")
        if sender:
            if sender in self.blacklisted_addresses:
                issues.append("Sender address is blacklisted")
                risk_score += 8.0
            elif not self._is_valid_algorand_address(sender):
                issues.append("Invalid sender address format")
                risk_score += 5.0
        
        # Check receiver address (for payment transactions)
        if transaction_data.get("type") == "pay":
            receiver = transaction_data.get("receiver")
            if receiver:
                if receiver in self.blacklisted_addresses:
                    issues.append("Receiver address is blacklisted")
                    risk_score += 6.0
                elif not self._is_valid_algorand_address(receiver):
                    issues.append("Invalid receiver address format")
                    risk_score += 3.0
        
        return issues, risk_score
    
    def _validate_amounts(self, wallet_address: str, transaction_data: Dict) -> Tuple[List[str], float]:
        """Validate transaction amounts for anomalies"""
        issues = []
        risk_score = 0.0
        
        amount = transaction_data.get("amount", 0)
        if amount <= 0:
            return issues, risk_score
        
        # Get historical average for this wallet
        avg_key = f"wallet_avg:{wallet_address}"
        historical_avg = self.redis.get(avg_key)
        
        if historical_avg:
            avg_amount = float(historical_avg.decode())
            
            # Check for unusually large amounts
            if amount > avg_amount * 100 and amount > 10 * 1000000:  # 10 ALGO threshold
                issues.append(f"Amount {amount/1000000:.2f} ALGO is {amount/avg_amount:.1f}x larger than average")
                risk_score += 3.0
            
            # Check for round number manipulation (common in attacks)
            if amount % 1000000 == 0 and amount > 100 * 1000000:  # Exact ALGO amounts > 100
                issues.append("Suspiciously round amount (potential automated attack)")
                risk_score += 1.0
        
        # Update running average
        self._update_wallet_average(wallet_address, amount)
        
        return issues, risk_score
    
    def _detect_replay_attack(self, api_key: str, transaction_data: Dict) -> Tuple[List[str], float]:
        """Advanced replay attack detection"""
        issues = []
        risk_score = 0.0
        
        try:
            # Create comprehensive transaction fingerprint
            fingerprint = self._create_advanced_fingerprint(transaction_data)
            
            # Check recent fingerprints
            replay_key = f"replay:{api_key}:{fingerprint}"
            if self.redis.exists(replay_key):
                last_seen = float(self.redis.get(replay_key).decode())
                time_diff = time.time() - last_seen
                
                if time_diff < 60:  # Same transaction within 1 minute
                    issues.append(f"Potential replay attack - identical transaction {time_diff:.1f}s ago")
                    risk_score += 7.0
                elif time_diff < 300:  # Same transaction within 5 minutes
                    issues.append(f"Suspicious duplicate transaction - {time_diff:.1f}s ago")
                    risk_score += 3.0
            
            # Store fingerprint
            self.redis.setex(replay_key, 3600, str(time.time()))
            
        except Exception as e:
            logger.error(f"Error in replay detection: {e}")
        
        return issues, risk_score
    
    def _detect_mev_attack(self, wallet_address: str, transaction_data: Dict) -> Tuple[List[str], float]:
        """Detect MEV/Sandwich attack patterns"""
        issues = []
        risk_score = 0.0
        
        try:
            current_time = time.time()
            
            # Track transaction timing for this wallet
            timing_key = f"mev_timing:{wallet_address}"
            self.redis.lpush(timing_key, str(current_time))
            self.redis.expire(timing_key, 300)  # 5 minute window
            
            # Get recent transactions
            recent_times = [float(t.decode()) for t in self.redis.lrange(timing_key, 0, 10)]
            
            if len(recent_times) >= 3:
                # Check for rapid-fire pattern (sandwich attack indicator)
                time_diffs = [recent_times[i] - recent_times[i+1] for i in range(len(recent_times)-1)]
                avg_interval = sum(time_diffs) / len(time_diffs)
                
                if avg_interval < 10:  # Average < 10 seconds between transactions
                    issues.append(f"Rapid transaction pattern detected - avg {avg_interval:.1f}s intervals")
                    risk_score += 4.0
                
                # Check for amount manipulation patterns
                amount = transaction_data.get("amount", 0)
                if amount > 1000000:  # > 1 ALGO
                    # Pattern: small, large, small (sandwich pattern)
                    if len(recent_times) >= 3:
                        issues.append("Potential sandwich attack pattern")
                        risk_score += 5.0
        
        except Exception as e:
            logger.error(f"Error in MEV detection: {e}")
        
        return issues, risk_score
    
    def _detect_flash_loan_attack(self, wallet_address: str, transaction_data: Dict) -> Tuple[List[str], float]:
        """Detect flash loan attack patterns"""
        issues = []
        risk_score = 0.0
        
        try:
            amount = transaction_data.get("amount", 0)
            
            # Flash loans involve very large amounts
            if amount > 100000 * 1000000:  # > 100K ALGO
                # Check if wallet normally handles such amounts
                balance_key = f"wallet_balance:{wallet_address}"
                typical_balance = self.redis.get(balance_key)
                
                if typical_balance:
                    balance = float(typical_balance.decode())
                    if amount > balance * 10:  # Amount > 10x typical balance
                        issues.append(f"Flash loan indicator - amount {amount/1000000:.0f} ALGO >> typical balance")
                        risk_score += 6.0
                
                # Check transaction sequence timing
                sequence_key = f"flash_sequence:{wallet_address}"
                self.redis.lpush(sequence_key, f"{amount}:{time.time()}")
                self.redis.expire(sequence_key, 60)  # 1 minute window
                
                sequence = self.redis.lrange(sequence_key, 0, 5)
                if len(sequence) >= 3:
                    issues.append("Multiple large transactions in short timeframe")
                    risk_score += 4.0
        
        except Exception as e:
            logger.error(f"Error in flash loan detection: {e}")
        
        return issues, risk_score
    
    def _validate_contract_interaction(self, transaction_data: Dict) -> Tuple[List[str], float]:
        """Validate smart contract interactions"""
        issues = []
        risk_score = 0.0
        
        if transaction_data.get("type") == "appl":
            app_id = transaction_data.get("application_id")
            
            # Check against known malicious contracts
            if app_id in self._get_malicious_contracts():
                issues.append(f"Interaction with known malicious contract: {app_id}")
                risk_score += 9.0
            
            # Check application call arguments
            app_args = transaction_data.get("application_args", [])
            if self._contains_suspicious_args(app_args):
                issues.append("Suspicious application call arguments detected")
                risk_score += 3.0
        
        return issues, risk_score
    
    def _analyze_temporal_patterns(self, wallet_address: str, api_key: str) -> Tuple[List[str], float]:
        """Analyze temporal patterns for bot detection"""
        issues = []
        risk_score = 0.0
        
        try:
            current_time = time.time()
            
            # Track request timing patterns
            pattern_key = f"temporal:{api_key}:{wallet_address}"
            self.redis.lpush(pattern_key, str(current_time))
            self.redis.expire(pattern_key, 3600)  # 1 hour window
            
            # Get recent request times
            recent_times = [float(t.decode()) for t in self.redis.lrange(pattern_key, 0, 20)]
            
            if len(recent_times) >= 5:
                # Check for bot-like regular intervals
                intervals = [recent_times[i] - recent_times[i+1] for i in range(len(recent_times)-1)]
                
                # Calculate interval variance
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
                    std_dev = variance ** 0.5
                    
                    # Very regular intervals = potential bot
                    if std_dev < 2.0 and avg_interval < 30:  # Very consistent < 30s intervals
                        issues.append(f"Bot-like regular intervals detected - avg {avg_interval:.1f}s ±{std_dev:.1f}")
                        risk_score += 2.0
                    
                    # Too frequent requests
                    if avg_interval < 5.0:  # < 5 seconds average
                        issues.append(f"Suspiciously frequent requests - avg {avg_interval:.1f}s intervals")
                        risk_score += 3.0
        
        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
        
        return issues, risk_score
    
    def _create_advanced_fingerprint(self, transaction_data: Dict) -> str:
        """Create advanced transaction fingerprint for replay detection"""
        # Include more fields for comprehensive fingerprinting
        fingerprint_fields = {
            "type": transaction_data.get("type"),
            "sender": transaction_data.get("sender"),
            "receiver": transaction_data.get("receiver"),
            "amount": transaction_data.get("amount"),
            "fee": transaction_data.get("fee"),
            "note": transaction_data.get("note"),
            "application_id": transaction_data.get("application_id"),
            "application_args": str(transaction_data.get("application_args", [])),
        }
        
        # Remove None values and sort for consistency
        clean_fields = {k: v for k, v in fingerprint_fields.items() if v is not None}
        fingerprint_str = json.dumps(clean_fields, sort_keys=True)
        
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    def _is_valid_algorand_address(self, address: str) -> bool:
        """Validate Algorand address format"""
        try:
            if not address or len(address) != 58:
                return False
            
            # Try to decode the address
            encoding.decode_address(address)
            return True
        except:
            return False
    
    def _get_malicious_contracts(self) -> set:
        """Get list of known malicious contract IDs"""
        # In production, this would be updated from threat intelligence feeds
        malicious_key = "malicious_contracts"
        malicious_contracts = self.redis.smembers(malicious_key)
        return {int(contract.decode()) for contract in malicious_contracts}
    
    def _contains_suspicious_args(self, app_args: List) -> bool:
        """Check for suspicious application call arguments"""
        try:
            for arg in app_args:
                if isinstance(arg, str):
                    # Check for common exploit patterns
                    suspicious_patterns = [
                        "reentrancy",
                        "overflow",
                        "underflow",
                        "drain",
                        "exploit"
                    ]
                    
                    arg_lower = arg.lower()
                    for pattern in suspicious_patterns:
                        if pattern in arg_lower:
                            return True
            
            return False
        except:
            return False
    
    def _update_wallet_average(self, wallet_address: str, amount: int):
        """Update running average for wallet amounts"""
        try:
            avg_key = f"wallet_avg:{wallet_address}"
            count_key = f"wallet_count:{wallet_address}"
            
            current_avg = float(self.redis.get(avg_key) or 0)
            current_count = int(self.redis.get(count_key) or 0)
            
            new_count = current_count + 1
            new_avg = ((current_avg * current_count) + amount) / new_count
            
            self.redis.setex(avg_key, 86400 * 7, str(new_avg))
            self.redis.setex(count_key, 86400 * 7, str(new_count))
            
        except Exception as e:
            logger.error(f"Error updating wallet average: {e}")
    
    def _store_validation_result(self, wallet_address: str, api_key: str, result: ValidationResult, risk_score: float):
        """Store validation result for machine learning and analytics"""
        try:
            result_key = f"validation:{int(time.time())}:{api_key}"
            result_data = {
                "wallet_address": wallet_address,
                "result": result.value,
                "risk_score": str(risk_score),
                "timestamp": str(time.time())
            }
            
            self.redis.hset(result_key, mapping=result_data)
            self.redis.expire(result_key, 86400 * 30)  # Keep for 30 days
            
        except Exception as e:
            logger.error(f"Error storing validation result: {e}")
    
    def get_wallet_risk_profile(self, wallet_address: str) -> Dict:
        """Get comprehensive risk profile for a wallet"""
        try:
            # Get recent validation results
            pattern = f"validation:*:*"
            validation_keys = self.redis.keys(pattern)
            
            wallet_validations = []
            for key in validation_keys[-100:]:  # Last 100 validations
                data = self.redis.hgetall(key)
                if data.get(b"wallet_address", b"").decode() == wallet_address:
                    wallet_validations.append({
                        "result": data.get(b"result", b"").decode(),
                        "risk_score": float(data.get(b"risk_score", b"0")),
                        "timestamp": float(data.get(b"timestamp", b"0"))
                    })
            
            if not wallet_validations:
                return {"risk_level": "unknown", "validation_count": 0}
            
            # Calculate aggregate risk metrics
            avg_risk = sum(v["risk_score"] for v in wallet_validations) / len(wallet_validations)
            max_risk = max(v["risk_score"] for v in wallet_validations)
            malicious_count = sum(1 for v in wallet_validations if v["result"] == "malicious")
            
            # Determine risk level
            if avg_risk >= 7.0 or malicious_count > 0:
                risk_level = "high"
            elif avg_risk >= 4.0:
                risk_level = "medium"
            elif avg_risk >= 2.0:
                risk_level = "low"
            else:
                risk_level = "minimal"
            
            return {
                "risk_level": risk_level,
                "avg_risk_score": avg_risk,
                "max_risk_score": max_risk,
                "validation_count": len(wallet_validations),
                "malicious_count": malicious_count,
                "last_validation": max(v["timestamp"] for v in wallet_validations)
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet risk profile: {e}")
            return {"risk_level": "error", "error": str(e)}
