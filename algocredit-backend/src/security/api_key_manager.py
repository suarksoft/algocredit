"""
API Key Management and Authentication
Secure API key validation and usage tracking
"""

import hashlib
import hmac
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import redis
import logging

logger = logging.getLogger(__name__)

class APIKeyStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    RATE_LIMITED = "rate_limited"

@dataclass
class SecurityContext:
    api_key_id: str
    user_id: str
    tier: str  # free, pro, enterprise
    permissions: List[str]
    rate_limits: Dict[str, int]
    ip_whitelist: Optional[List[str]] = None
    is_valid: bool = True
    threat_score: float = 0.0

class APIKeyManager:
    """
    Manages API key authentication and security
    """
    
    def __init__(self, redis_client: redis.Redis = None):
        self.redis = redis_client or redis.Redis(host='localhost', port=6379, db=1)
        
    def generate_api_key(self, user_id: str, tier: str = "free") -> str:
        """Generate a new API key"""
        timestamp = str(int(time.time()))
        raw_key = f"{user_id}:{timestamp}:{tier}"
        api_key = f"ac_live_{hashlib.sha256(raw_key.encode()).hexdigest()[:32]}"
        
        # Store key metadata
        key_data = {
            "user_id": user_id,
            "tier": tier,
            "created_at": timestamp,
            "status": APIKeyStatus.ACTIVE.value,
            "last_used": None,
            "usage_count": 0,
            "threat_score": 0.0
        }
        
        # Store key data with proper Redis format
        for key, value in key_data.items():
            self.redis.hset(f"api_key:{api_key}", key, str(value))
        logger.info(f"Generated API key for user {user_id}, tier {tier}")
        
        return api_key
    
    def validate_api_key(self, api_key: str, ip_address: str = None) -> SecurityContext:
        """Validate API key and return security context"""
        try:
            # Check key format
            if not api_key.startswith("ac_live_") or len(api_key) != 40:
                return SecurityContext("", "", "", [], {}, is_valid=False)
            
            # Get key data from Redis
            key_data = self.redis.hgetall(f"api_key:{api_key}")
            if not key_data:
                logger.warning(f"Invalid API key attempted: {api_key[:20]}...")
                return SecurityContext("", "", "", [], {}, is_valid=False)
            
            # Check key status
            status = key_data.get(b"status", b"").decode()
            if status != APIKeyStatus.ACTIVE.value:
                logger.warning(f"Inactive API key attempted: {api_key[:20]}..., status: {status}")
                return SecurityContext("", "", "", [], {}, is_valid=False)
            
            # Update usage statistics
            self.redis.hincrby(f"api_key:{api_key}", "usage_count", 1)
            self.redis.hset(f"api_key:{api_key}", "last_used", str(int(time.time())))
            
            # IP whitelist check (if configured)
            if ip_address:
                whitelist_key = f"api_key_whitelist:{api_key}"
                if self.redis.exists(whitelist_key):
                    allowed_ips = self.redis.smembers(whitelist_key)
                    if ip_address.encode() not in allowed_ips:
                        logger.warning(f"IP not whitelisted: {ip_address} for key {api_key[:20]}...")
                        return SecurityContext("", "", "", [], {}, is_valid=False)
            
            # Build security context
            tier = key_data.get(b"tier", b"free").decode()
            user_id = key_data.get(b"user_id", b"").decode()
            threat_score = float(key_data.get(b"threat_score", b"0.0"))
            
            permissions = self._get_tier_permissions(tier)
            rate_limits = self._get_tier_rate_limits(tier)
            
            return SecurityContext(
                api_key_id=api_key,
                user_id=user_id,
                tier=tier,
                permissions=permissions,
                rate_limits=rate_limits,
                threat_score=threat_score
            )
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return SecurityContext("", "", "", [], {}, is_valid=False)
    
    def _get_tier_permissions(self, tier: str) -> List[str]:
        """Get permissions based on tier"""
        permissions_map = {
            "free": ["credit_score", "basic_validation"],
            "pro": ["credit_score", "transaction_validation", "threat_detection", "webhooks"],
            "enterprise": ["*"]  # All permissions
        }
        return permissions_map.get(tier, [])
    
    def _get_tier_rate_limits(self, tier: str) -> Dict[str, int]:
        """Get rate limits based on tier"""
        rate_limits_map = {
            "free": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "requests_per_day": 10000
            },
            "pro": {
                "requests_per_minute": 300,
                "requests_per_hour": 10000,
                "requests_per_day": 100000
            },
            "enterprise": {
                "requests_per_minute": 1000,
                "requests_per_hour": 50000,
                "requests_per_day": 1000000
            }
        }
        return rate_limits_map.get(tier, rate_limits_map["free"])
    
    def update_threat_score(self, api_key: str, threat_score: float):
        """Update threat score for API key"""
        self.redis.hset(f"api_key:{api_key}", "threat_score", str(threat_score))
        
        # Auto-suspend if threat score too high
        if threat_score > 8.0:
            self.redis.hset(f"api_key:{api_key}", "status", APIKeyStatus.SUSPENDED.value)
            logger.warning(f"API key auto-suspended due to high threat score: {api_key[:20]}...")
    
    def get_usage_stats(self, api_key: str) -> Dict:
        """Get usage statistics for API key"""
        key_data = self.redis.hgetall(f"api_key:{api_key}")
        if not key_data:
            return {}
        
        return {
            "usage_count": int(key_data.get(b"usage_count", b"0")),
            "last_used": key_data.get(b"last_used", b"").decode(),
            "threat_score": float(key_data.get(b"threat_score", b"0.0")),
            "status": key_data.get(b"status", b"").decode()
        }
