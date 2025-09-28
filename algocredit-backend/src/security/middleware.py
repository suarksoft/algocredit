"""
Security Middleware for FastAPI
Web3 Security Firewall integration
"""

import time
import json
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from .api_key_manager import APIKeyManager, SecurityContext
from .rate_limiter import AdaptiveRateLimiter, RateLimitType, RateLimitAction
from .threat_detector import ThreatDetector
from .transaction_validator import TransactionValidator, ValidationResult

logger = logging.getLogger(__name__)

class Web3SecurityMiddleware:
    """
    Comprehensive Web3 Security Middleware
    """
    
    def __init__(self):
        self.api_manager = APIKeyManager()
        self.rate_limiter = AdaptiveRateLimiter()
        self.threat_detector = ThreatDetector()
        self.transaction_validator = TransactionValidator()
        self.security_bearer = HTTPBearer(auto_error=False)
    
    async def authenticate_request(self, request: Request) -> SecurityContext:
        """Authenticate and validate incoming request"""
        try:
            # Extract API key from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                # For backward compatibility, check X-API-Key header
                api_key = request.headers.get("X-API-Key")
                if not api_key:
                    raise HTTPException(
                        status_code=401,
                        detail="Missing API key. Use Authorization: Bearer <api_key> or X-API-Key header"
                    )
            else:
                api_key = auth_header.replace("Bearer ", "")
            
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Validate API key
            security_context = self.api_manager.validate_api_key(api_key, client_ip)
            if not security_context.is_valid:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired API key"
                )
            
            # Check rate limits
            rate_result = self.rate_limiter.check_rate_limit(
                identifier=api_key,
                limit_type=RateLimitType.PER_API_KEY,
                tier=security_context.tier,
                endpoint=str(request.url.path),
                threat_score=security_context.threat_score
            )
            
            if rate_result.action == RateLimitAction.BLOCK:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {rate_result.retry_after}s",
                    headers={
                        "X-RateLimit-Remaining": str(rate_result.remaining_requests),
                        "X-RateLimit-Reset": str(rate_result.reset_time),
                        "Retry-After": str(rate_result.retry_after)
                    }
                )
            
            # DDoS protection
            ddos_result = self.rate_limiter.check_ddos_protection(client_ip, str(request.url.path))
            if ddos_result.action == RateLimitAction.BLOCK:
                logger.warning(f"DDoS protection blocked IP: {client_ip}")
                raise HTTPException(
                    status_code=429,
                    detail="DDoS protection activated. Please try again later.",
                    headers={"Retry-After": str(ddos_result.retry_after)}
                )
            
            # Add security headers to context
            security_context.client_ip = client_ip
            security_context.rate_limit_remaining = rate_result.remaining_requests
            security_context.ddos_threat_level = ddos_result.threat_level
            
            return security_context
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in request authentication: {e}")
            raise HTTPException(
                status_code=500,
                detail="Security validation error"
            )
    
    async def validate_transaction_request(self, 
                                         request: Request, 
                                         security_context: SecurityContext) -> Dict:
        """Validate transaction-related requests"""
        try:
            # Parse request body
            body = await request.body()
            if body:
                try:
                    request_data = json.loads(body.decode())
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid JSON in request body"
                    )
            else:
                request_data = {}
            
            # Extract wallet address from request
            wallet_address = (
                request_data.get("wallet_address") or
                request.query_params.get("wallet_address") or
                request.path_params.get("wallet_address")
            )
            
            if not wallet_address:
                # Not all endpoints require wallet address
                return {"validation_skipped": True}
            
            # Validate transaction if present
            if "transaction_data" in request_data or any(key in request_data for key in ["amount", "to", "from"]):
                # Extract transaction data
                transaction_data = request_data.get("transaction_data", request_data)
                
                # Run comprehensive validation
                validation_report = self.transaction_validator.validate_transaction(
                    wallet_address=wallet_address,
                    transaction_data=transaction_data,
                    api_key=security_context.api_key_id,
                    context={"tier": security_context.tier}
                )
                
                # Block malicious transactions
                if validation_report.result == ValidationResult.MALICIOUS:
                    logger.critical(f"MALICIOUS TRANSACTION BLOCKED: {validation_report.issues}")
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "Transaction blocked by security system",
                            "risk_score": validation_report.risk_score,
                            "issues": validation_report.issues,
                            "recommendations": validation_report.recommendations
                        }
                    )
                
                # Warn about suspicious transactions
                elif validation_report.result == ValidationResult.SUSPICIOUS:
                    logger.warning(f"SUSPICIOUS TRANSACTION: {validation_report.issues}")
                    # Continue but log for monitoring
                
                return {
                    "validation_result": validation_report.result.value,
                    "risk_score": validation_report.risk_score,
                    "issues": validation_report.issues,
                    "recommendations": validation_report.recommendations
                }
            
            return {"validation_skipped": True, "reason": "No transaction data"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in transaction validation: {e}")
            return {"validation_error": str(e)}
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP considering proxies"""
        # Check common proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in case of multiple proxies
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def create_security_headers(self, security_context: SecurityContext) -> Dict[str, str]:
        """Create security-related response headers"""
        headers = {
            "X-RateLimit-Tier": security_context.tier,
            "X-RateLimit-Remaining": str(security_context.rate_limit_remaining),
            "X-Security-Threat-Level": str(security_context.threat_score),
            "X-API-Version": "v1",
            "X-Security-Firewall": "AlgoCredit-Web3-Shield"
        }
        
        if hasattr(security_context, 'ddos_threat_level'):
            headers["X-DDoS-Threat-Level"] = str(security_context.ddos_threat_level)
        
        return headers
    
    async def log_request(self, 
                         request: Request, 
                         response: Response, 
                         security_context: SecurityContext,
                         processing_time: float):
        """Log request for security analytics"""
        try:
            log_data = {
                "timestamp": time.time(),
                "api_key": security_context.api_key_id,
                "user_id": security_context.user_id,
                "tier": security_context.tier,
                "ip_address": getattr(security_context, 'client_ip', 'unknown'),
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "processing_time": processing_time,
                "threat_score": security_context.threat_score,
                "user_agent": request.headers.get("User-Agent", "")
            }
            
            # Store in Redis for analytics
            log_key = f"request_log:{int(time.time())}:{security_context.api_key_id}"
            self.redis.hset(log_key, mapping=log_data)
            self.redis.expire(log_key, 86400 * 7)  # Keep for 1 week
            
            # Update API key usage statistics
            self.api_manager.update_threat_score(
                security_context.api_key_id, 
                security_context.threat_score
            )
            
        except Exception as e:
            logger.error(f"Error logging request: {e}")

# Global middleware instance
web3_security = Web3SecurityMiddleware()
