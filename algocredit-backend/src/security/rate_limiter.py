"""
Advanced Rate Limiting and DDoS Protection
Enterprise-grade rate limiting with adaptive algorithms
"""

import time
import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import redis
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    PER_API_KEY = "api_key"
    PER_IP = "ip_address"
    PER_WALLET = "wallet_address"
    PER_ENDPOINT = "endpoint"
    GLOBAL = "global"

class RateLimitAction(Enum):
    ALLOW = "allow"
    THROTTLE = "throttle"
    BLOCK = "block"
    CAPTCHA = "captcha"

@dataclass
class RateLimitResult:
    action: RateLimitAction
    remaining_requests: int
    reset_time: int
    retry_after: Optional[int] = None
    threat_level: float = 0.0

class AdaptiveRateLimiter:
    """
    Advanced rate limiter with adaptive algorithms and threat-based adjustments
    """
    
    def __init__(self, redis_client: redis.Redis = None):
        self.redis = redis_client or redis.Redis(host='localhost', port=6379, db=3)
        
        # Default rate limits (per minute)
        self.default_limits = {
            "free": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "burst_capacity": 10
            },
            "pro": {
                "requests_per_minute": 300,
                "requests_per_hour": 10000,
                "burst_capacity": 50
            },
            "enterprise": {
                "requests_per_minute": 1000,
                "requests_per_hour": 50000,
                "burst_capacity": 200
            }
        }
    
    def check_rate_limit(self, 
                        identifier: str, 
                        limit_type: RateLimitType,
                        tier: str = "free",
                        endpoint: str = None,
                        threat_score: float = 0.0) -> RateLimitResult:
        """
        Check rate limit using token bucket algorithm with threat-based adjustment
        """
        try:
            current_time = time.time()
            
            # Get base limits for tier
            base_limits = self.default_limits.get(tier, self.default_limits["free"])
            
            # Adjust limits based on threat score
            adjusted_limits = self._adjust_limits_for_threat(base_limits, threat_score)
            
            # Create Redis keys
            bucket_key = f"bucket:{limit_type.value}:{identifier}"
            if endpoint:
                bucket_key += f":{endpoint}"
            
            # Token bucket algorithm
            return self._token_bucket_check(bucket_key, adjusted_limits, current_time)
            
        except Exception as e:
            logger.error(f"Error in rate limit check: {e}")
            # Fail-safe: allow request but log error
            return RateLimitResult(
                action=RateLimitAction.ALLOW,
                remaining_requests=100,
                reset_time=int(time.time() + 60)
            )
    
    def _token_bucket_check(self, bucket_key: str, limits: Dict, current_time: float) -> RateLimitResult:
        """Token bucket algorithm implementation"""
        try:
            # Get current bucket state
            bucket_data = self.redis.hgetall(bucket_key)
            
            if bucket_data:
                tokens = float(bucket_data.get(b"tokens", b"0"))
                last_refill = float(bucket_data.get(b"last_refill", b"0"))
            else:
                tokens = float(limits["burst_capacity"])
                last_refill = current_time
            
            # Calculate tokens to add based on time elapsed
            time_elapsed = current_time - last_refill
            tokens_to_add = time_elapsed * (limits["requests_per_minute"] / 60.0)
            
            # Add tokens but don't exceed capacity
            tokens = min(limits["burst_capacity"], tokens + tokens_to_add)
            
            # Check if request can be served
            if tokens >= 1.0:
                # Allow request, consume token
                tokens -= 1.0
                action = RateLimitAction.ALLOW
                remaining = int(tokens)
            else:
                # Rate limited
                action = RateLimitAction.THROTTLE if tokens > 0.1 else RateLimitAction.BLOCK
                remaining = 0
            
            # Update bucket state
            bucket_state = {
                "tokens": str(tokens),
                "last_refill": str(current_time),
                "last_request": str(current_time)
            }
            self.redis.hset(bucket_key, mapping=bucket_state)
            self.redis.expire(bucket_key, 3600)  # Expire after 1 hour
            
            # Calculate reset time
            if tokens < limits["burst_capacity"]:
                tokens_needed = limits["burst_capacity"] - tokens
                reset_time = int(current_time + (tokens_needed * 60 / limits["requests_per_minute"]))
            else:
                reset_time = int(current_time + 60)
            
            return RateLimitResult(
                action=action,
                remaining_requests=remaining,
                reset_time=reset_time,
                retry_after=int(60 - (tokens * 60 / limits["requests_per_minute"])) if action != RateLimitAction.ALLOW else None
            )
            
        except Exception as e:
            logger.error(f"Error in token bucket check: {e}")
            return RateLimitResult(
                action=RateLimitAction.ALLOW,
                remaining_requests=100,
                reset_time=int(current_time + 60)
            )
    
    def _adjust_limits_for_threat(self, base_limits: Dict, threat_score: float) -> Dict:
        """Adjust rate limits based on threat score"""
        # Higher threat score = lower limits
        threat_multiplier = max(0.1, 1.0 - (threat_score / 10.0))
        
        return {
            "requests_per_minute": int(base_limits["requests_per_minute"] * threat_multiplier),
            "requests_per_hour": int(base_limits["requests_per_hour"] * threat_multiplier),
            "burst_capacity": int(base_limits["burst_capacity"] * threat_multiplier)
        }
    
    def check_ddos_protection(self, ip_address: str, endpoint: str = None) -> RateLimitResult:
        """Advanced DDoS protection with pattern detection"""
        try:
            current_time = time.time()
            
            # Check requests in last minute from this IP
            minute_key = f"ddos_minute:{ip_address}"
            minute_count = self.redis.incr(minute_key)
            self.redis.expire(minute_key, 60)
            
            # Check requests in last hour from this IP
            hour_key = f"ddos_hour:{ip_address}"
            hour_count = self.redis.incr(hour_key)
            self.redis.expire(hour_key, 3600)
            
            # Adaptive thresholds
            minute_threshold = 120  # Base threshold
            hour_threshold = 5000
            
            # Check for burst patterns
            burst_key = f"ddos_burst:{ip_address}"
            burst_window = 10  # 10 second window
            burst_count = self.redis.incr(burst_key)
            self.redis.expire(burst_key, burst_window)
            
            # Determine action
            if burst_count > 50:  # > 50 requests in 10 seconds
                action = RateLimitAction.BLOCK
                retry_after = 300  # 5 minutes
            elif minute_count > minute_threshold:
                action = RateLimitAction.THROTTLE
                retry_after = 60
            elif hour_count > hour_threshold:
                action = RateLimitAction.CAPTCHA
                retry_after = 30
            else:
                action = RateLimitAction.ALLOW
                retry_after = None
            
            # Log suspicious activity
            if action != RateLimitAction.ALLOW:
                logger.warning(f"DDoS protection triggered for IP {ip_address}: {action.value}")
                self._log_ddos_event(ip_address, minute_count, hour_count, burst_count)
            
            return RateLimitResult(
                action=action,
                remaining_requests=max(0, minute_threshold - minute_count),
                reset_time=int(current_time + 60),
                retry_after=retry_after,
                threat_level=min(10.0, (minute_count / minute_threshold) * 5.0)
            )
            
        except Exception as e:
            logger.error(f"Error in DDoS protection: {e}")
            return RateLimitResult(
                action=RateLimitAction.ALLOW,
                remaining_requests=100,
                reset_time=int(time.time() + 60)
            )
    
    def _log_ddos_event(self, ip_address: str, minute_count: int, hour_count: int, burst_count: int):
        """Log DDoS event for monitoring"""
        event_data = {
            "ip_address": ip_address,
            "minute_count": str(minute_count),
            "hour_count": str(hour_count),
            "burst_count": str(burst_count),
            "timestamp": str(time.time()),
            "event_type": "ddos_protection"
        }
        
        event_key = f"ddos_event:{int(time.time())}:{ip_address}"
        self.redis.hset(event_key, mapping=event_data)
        self.redis.expire(event_key, 86400)  # Keep for 24 hours
    
    def get_rate_limit_stats(self, identifier: str, limit_type: RateLimitType) -> Dict:
        """Get current rate limit statistics"""
        try:
            bucket_key = f"bucket:{limit_type.value}:{identifier}"
            bucket_data = self.redis.hgetall(bucket_key)
            
            if not bucket_data:
                return {"tokens": 0, "last_refill": 0, "status": "not_found"}
            
            return {
                "tokens": float(bucket_data.get(b"tokens", b"0")),
                "last_refill": float(bucket_data.get(b"last_refill", b"0")),
                "last_request": float(bucket_data.get(b"last_request", b"0")),
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit stats: {e}")
            return {"error": str(e)}
