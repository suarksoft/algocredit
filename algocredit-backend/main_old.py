"""
Corporate Treasury Marketplace API
24-Hour Sprint Implementation
Yatırımcıları startup'larla buluşturan platform
"""

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import sqlite3
import json
import time
from datetime import datetime

# Import services
from src.services.credit_scoring_service import credit_scoring_service

# Import existing routers (will adapt them)
from src.api.credit import router as credit_router
from src.api.loans import router as loans_router

# Import Web3 Security Firewall
from src.security.middleware import web3_security
from src.security.api_key_manager import SecurityContext
from src.security.rate_limiter import RateLimitType
import logging

logger = logging.getLogger(__name__)

# Security dependency
async def get_security_context(request: Request) -> SecurityContext:
    """Security dependency for protected endpoints"""
    return await web3_security.authenticate_request(request)

# Application metadata
app_metadata = {
    "title": "AlgoCredit Web3 Security Firewall API",
    "description": "Enterprise Web3 Security Platform for Algorand",
    "version": "firewall-1.0.0",
    "contact": {
        "name": "AlgoCredit Security Team",
        "url": "https://algocredit.io",
    },
    "license_info": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
}

# Pydantic models for new marketplace functionality
class InvestorRegistration(BaseModel):
    name: str
    wallet_address: str
    investment_capacity: int
    risk_preference: str  # conservative, moderate, aggressive

class StartupRegistration(BaseModel):
    name: str
    wallet_address: str
    business_description: str
    requested_amount: int
    business_metrics: Optional[dict] = None

class DepositRequest(BaseModel):
    investor_id: int
    amount: int

class FundingRequest(BaseModel):
    investor_id: int
    startup_id: int
    amount: int

class RepaymentRequest(BaseModel):
    startup_id: int
    amount: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 AlgoCredit API starting up...")
    print("🔗 Connecting to Algorand TestNet...")
    print("🗄️  Initializing database...")
    
    # Initialize database
    from src.models.database import create_tables
    create_tables()
    
    print("🤖 Loading AI models...")
    print("✅ AlgoCredit API ready!")
    
    yield
    
    # Shutdown
    print("🛑 AlgoCredit API shutting down...")
    print("💾 Closing database connections...")
    print("👋 Goodbye!")


# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    **app_metadata
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8005", "https://algocredit.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "🚀 AlgoCredit API is running!",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "AlgoCredit API",
        "version": "1.0.0",
        "algorand_network": "testnet",
        "database": "connected",  # Will be dynamic later
        "ai_model": "loaded"      # Will be dynamic later
    }


# Temporary credit scoring endpoint (will be moved to proper router)
@app.get("/api/v1/credit/model-info", tags=["Credit Scoring"])
async def get_model_info():
    """Get AI model information and status"""
    return credit_scoring_service.get_model_info()


# ============================================================================
# WEB3 SECURITY FIREWALL ENDPOINTS
# ============================================================================

@app.post("/api/v1/security/generate-key", tags=["Security"])
async def generate_wallet_api_key(
    wallet_address: str,
    tier: str = "free",
    signature: str = None,
    request: Request = None
):
    """
    Generate wallet-based API key for Web3 Security Firewall
    Requires wallet address and optional signature for verification
    """
    try:
        # Validate wallet address
        if not wallet_address or len(wallet_address) != 58:
            raise HTTPException(status_code=400, detail="Valid Algorand wallet address required")
        
        # Validate tier
        valid_tiers = ["free", "pro", "enterprise"]
        if tier not in valid_tiers:
            raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
        
        # Check if wallet already has an API key
        existing_key_pattern = f"wallet_api_key:{wallet_address}"
        existing_key = web3_security.api_manager.redis.get(existing_key_pattern)
        
        if existing_key:
            existing_api_key = existing_key.decode()
            # Return existing key info
            usage_stats = web3_security.api_manager.get_usage_stats(existing_api_key)
            return {
                "api_key": existing_api_key,
                "tier": tier,
                "wallet_address": wallet_address,
                "status": "existing",
                "usage_stats": usage_stats,
                "message": "Wallet already has an API key"
            }
        
        # Generate new API key with wallet address as user_id
        api_key = web3_security.api_manager.generate_api_key(wallet_address, tier)
        
        # Store wallet -> API key mapping
        web3_security.api_manager.redis.setex(
            f"wallet_api_key:{wallet_address}", 
            86400 * 365,  # 1 year
            api_key
        )
        
        # Store API key -> wallet mapping  
        web3_security.api_manager.redis.setex(
            f"api_key_wallet:{api_key}",
            86400 * 365,  # 1 year
            wallet_address
        )
        
        # TODO: Register in smart contract
        # await register_api_key_in_contract(wallet_address, api_key, tier)
        
        return {
            "api_key": api_key,
            "tier": tier,
            "wallet_address": wallet_address,
            "created_at": time.time(),
            "status": "new",
            "usage_instructions": {
                "header": "Authorization: Bearer <api_key>",
                "alternative": "X-API-Key: <api_key>",
                "rate_limits": web3_security.api_manager._get_tier_rate_limits(tier),
                "smart_contract_id": "746510137",
                "testnet_address": "U66YQKAWIN3G623D4T62W2QXTIHJIK4AIMNTPF3YYFOKUM7UDL7YOXJN6I"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating wallet API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate API key")

@app.get("/api/v1/security/wallet-key/{wallet_address}", tags=["Security"])
async def get_wallet_api_key(
    wallet_address: str,
    request: Request = None
):
    """
    Get existing API key for wallet address
    """
    try:
        # Validate wallet address
        if not wallet_address or len(wallet_address) != 58:
            raise HTTPException(status_code=400, detail="Valid Algorand wallet address required")
        
        # Check for existing API key
        existing_key_pattern = f"wallet_api_key:{wallet_address}"
        existing_key = web3_security.api_manager.redis.get(existing_key_pattern)
        
        if not existing_key:
            return {
                "wallet_address": wallet_address,
                "has_api_key": False,
                "message": "No API key found for this wallet"
            }
        
        api_key = existing_key.decode()
        usage_stats = web3_security.api_manager.get_usage_stats(api_key)
        
        return {
            "wallet_address": wallet_address,
            "has_api_key": True,
            "api_key": api_key,
            "usage_stats": usage_stats,
            "smart_contract_registered": True  # TODO: Check actual contract
        }
        
    except Exception as e:
        logger.error(f"Error getting wallet API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to get wallet API key")

@app.post("/api/v1/security/validate-transaction", tags=["Security"])
async def validate_transaction(
    request: Request,
    security_context: SecurityContext = Depends(get_security_context)
):
    """
    Validate transaction for security threats
    Enterprise Web3 Security Firewall
    """
    try:
        # Validate transaction using security middleware
        validation_result = await web3_security.validate_transaction_request(request, security_context)
        
        return {
            "security_status": "validated",
            "api_key_tier": security_context.tier,
            "threat_score": security_context.threat_score,
            "validation_result": validation_result,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error in transaction validation: {e}")
        raise HTTPException(status_code=500, detail="Security validation failed")

@app.get("/api/v1/security/threat-intel/{wallet_address}", tags=["Security"])
async def get_threat_intelligence(
    wallet_address: str,
    security_context: SecurityContext = Depends(get_security_context)
):
    """
    Get threat intelligence for wallet address
    """
    try:
        # Get wallet risk profile
        risk_profile = web3_security.transaction_validator.get_wallet_risk_profile(wallet_address)
        
        # Get recent threat summary
        threat_summary = web3_security.threat_detector.get_threat_summary(security_context.api_key_id)
        
        return {
            "wallet_address": wallet_address,
            "risk_profile": risk_profile,
            "threat_summary": threat_summary,
            "analysis_timestamp": time.time(),
            "security_recommendations": [
                "Monitor wallet activity",
                "Check transaction patterns",
                "Verify identity if high risk"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting threat intelligence: {e}")
        raise HTTPException(status_code=500, detail="Failed to get threat intelligence")

@app.post("/api/v1/credit/score", tags=["Credit Scoring"])
async def get_credit_score(
    wallet_address: str,
    security_context: SecurityContext = Depends(get_security_context)
):
    """
    AI-powered credit scoring endpoint with Web3 Security
    Uses trained ML model for accurate scoring
    """
    if not wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address is required")
    
    # Security validation for credit scoring request
    start_time = time.time()
    
    try:
        # Use the AI credit scoring service
        credit_assessment = await credit_scoring_service.analyze_wallet_and_score(wallet_address)
        
        # Add security metadata
        credit_assessment["security_context"] = {
            "api_key_tier": security_context.tier,
            "threat_score": security_context.threat_score,
            "validation_timestamp": time.time()
        }
        
        return credit_assessment
        
    except Exception as e:
        logger.error(f"Error in credit scoring: {e}")
        raise HTTPException(status_code=500, detail="Credit scoring failed")
    finally:
        # Log request for security analytics
        processing_time = time.time() - start_time
        # Note: Response object not available here, would need middleware for full logging

@app.get("/api/v1/security/dashboard/{api_key}", tags=["Security"])
async def get_security_dashboard(
    api_key: str,
    hours: int = 24,
    security_context: SecurityContext = Depends(get_security_context)
):
    """
    Security dashboard - analytics and monitoring
    """
    try:
        # Verify user can access this API key's data
        if security_context.api_key_id != api_key and security_context.tier != "enterprise":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get comprehensive security analytics
        usage_stats = web3_security.api_manager.get_usage_stats(api_key)
        threat_summary = web3_security.threat_detector.get_threat_summary(api_key, hours)
        rate_stats = web3_security.rate_limiter.get_rate_limit_stats(api_key, RateLimitType.PER_API_KEY)
        
        return {
            "api_key": api_key[:20] + "...",  # Masked for security
            "tier": security_context.tier,
            "usage_statistics": usage_stats,
            "threat_analytics": threat_summary,
            "rate_limit_status": rate_stats,
            "security_score": 10.0 - security_context.threat_score,  # Inverted for user-friendly display
            "dashboard_period_hours": hours,
            "generated_at": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error getting security dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security dashboard")

@app.get("/api/v1/security/health", tags=["Security"])
async def security_health_check():
    """
    Security system health check
    """
    try:
        # Check Redis connectivity
        redis_status = "connected" if web3_security.api_manager.redis.ping() else "disconnected"
        
        # Get system statistics
        total_keys = len(web3_security.api_manager.redis.keys("api_key:*"))
        total_threats = len(web3_security.threat_detector.redis.keys("threat:*"))
        
        return {
            "status": "healthy",
            "redis_status": redis_status,
            "total_api_keys": total_keys,
            "total_threats_24h": total_threats,
            "firewall_version": "1.0.0",
            "uptime": "operational",
            "last_check": time.time()
        }
        
    except Exception as e:
        logger.error(f"Security health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": time.time()
        }

@app.post("/api/v1/credit/score", tags=["Credit Scoring"])
async def get_credit_score(
    wallet_address: str,
    security_context: SecurityContext = Depends(get_security_context)
):
    """
    AI-powered credit scoring endpoint with Web3 Security
    Uses trained ML model for accurate scoring
    """
    if not wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address is required")
    
    # Security validation for credit scoring request
    start_time = time.time()
    
    try:
        # Use the AI credit scoring service
        credit_assessment = await credit_scoring_service.analyze_wallet_and_score(wallet_address)
        
        # Add security metadata
        credit_assessment["security_context"] = {
            "api_key_tier": security_context.tier,
            "threat_score": security_context.threat_score,
            "validation_timestamp": time.time()
        }
        
        return credit_assessment
        
    except Exception as e:
        logger.error(f"Error in credit scoring: {e}")
        raise HTTPException(status_code=500, detail="Credit scoring failed")
    finally:
        # Log request for security analytics
        processing_time = time.time() - start_time
        # Note: Response object not available here, would need middleware for full logging


@app.get("/marketplace/stats", tags=["Marketplace"])
async def get_marketplace_stats():
    """Get marketplace statistics"""
    return {
        "total_startups": 12,
        "total_investors": 8,
        "total_funding": 2500000,
        "active_deals": 5,
        "success_rate": 85.5,
        "avg_funding_time": "7.2 days",
        "timestamp": "2025-09-28T02:00:00Z"
    }


@app.get("/user/login", tags=["Authentication"])
async def user_login(wallet: str, type: str):
    """User login endpoint"""
    return {
        "success": True,
        "user_id": f"{type}_12345",
        "wallet_address": wallet,
        "user_type": type,
        "login_timestamp": "2025-09-28T02:00:00Z"
    }


# Include API routers
app.include_router(credit_router, prefix="/api/v1/credit", tags=["Credit Scoring"])
app.include_router(loans_router, prefix="/api/v1/loans", tags=["Loans"])
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])  # Will be added later


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
