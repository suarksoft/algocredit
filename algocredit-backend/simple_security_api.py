"""
AlgoCredit Web3 Security Firewall - Simple API
Real backend without complex dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import time
import redis
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AlgoCredit Web3 Security Firewall",
    description="Enterprise-Grade Security Platform for Algorand",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Redis connected successfully")
except:
    redis_client = None
    logger.warning("⚠️ Redis not available, using in-memory storage")

# In-memory storage as fallback
wallet_api_keys = {}

@app.get("/")
async def root():
    return {
        "message": "AlgoCredit Web3 Security Firewall API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/api/v1/security/health",
            "/api/v1/security/generate-key",
            "/api/v1/security/wallet-key/{wallet_address}",
            "/docs"
        ]
    }

@app.get("/api/v1/security/health")
async def security_health():
    """Security system health check"""
    return {
        "status": "healthy",
        "message": "AlgoCredit Security API operational",
        "version": "1.0.0",
        "redis_status": "connected" if redis_client else "unavailable",
        "total_api_keys": len(wallet_api_keys),
        "timestamp": time.time()
    }

@app.post("/api/v1/security/generate-key")
async def generate_wallet_api_key(wallet_address: str, tier: str = "pro"):
    """Generate wallet-based API key"""
    try:
        # Validate wallet address
        if not wallet_address or len(wallet_address) != 58:
            raise HTTPException(status_code=400, detail="Valid Algorand wallet address required")
        
        # Check for existing API key
        existing_key = None
        if redis_client:
            existing_key = redis_client.get(f"wallet_api_key:{wallet_address}")
        else:
            existing_key = wallet_api_keys.get(wallet_address)
        
        if existing_key:
            logger.info(f"Returning existing API key for wallet: {wallet_address[:8]}...")
            return {
                "api_key": existing_key,
                "wallet_address": wallet_address,
                "tier": tier,
                "status": "existing",
                "message": "Existing API key found for wallet"
            }
        
        # Generate new API key
        timestamp = str(time.time())
        api_key_data = f"{wallet_address}:{timestamp}:{tier}"
        api_key = f"ac_live_{hashlib.sha256(api_key_data.encode()).hexdigest()[:32]}"
        
        # Store API key
        if redis_client:
            redis_client.setex(f"wallet_api_key:{wallet_address}", 86400 * 365, api_key)
            redis_client.setex(f"api_key_wallet:{api_key}", 86400 * 365, wallet_address)
            redis_client.hset(f"api_key_data:{api_key}", mapping={
                "wallet_address": wallet_address,
                "tier": tier,
                "created_at": timestamp,
                "usage_count": 0,
                "threat_score": 0.0
            })
        else:
            wallet_api_keys[wallet_address] = api_key
        
        logger.info(f"Generated new API key for wallet: {wallet_address[:8]}...")
        
        return {
            "api_key": api_key,
            "wallet_address": wallet_address,
            "tier": tier,
            "status": "new",
            "created_at": time.time(),
            "message": "API key generated successfully",
            "usage_instructions": {
                "header": "Authorization: Bearer <api_key>",
                "rate_limits": {
                    "requests_per_minute": 300 if tier == "pro" else 60,
                    "requests_per_hour": 10000 if tier == "pro" else 1000
                },
                "smart_contract_id": "746510137",
                "testnet_address": "U66YQKAWIN3G623D4T62W2QXTIHJIK4AIMNTPF3YYFOKUM7UDL7YOXJN6I"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate API key: {str(e)}")

@app.get("/api/v1/security/wallet-key/{wallet_address}")
async def get_wallet_api_key(wallet_address: str):
    """Get existing API key for wallet"""
    try:
        # Validate wallet address
        if not wallet_address or len(wallet_address) != 58:
            raise HTTPException(status_code=400, detail="Valid Algorand wallet address required")
        
        # Check for existing API key
        existing_key = None
        if redis_client:
            existing_key = redis_client.get(f"wallet_api_key:{wallet_address}")
            if existing_key:
                usage_data = redis_client.hgetall(f"api_key_data:{existing_key}")
        else:
            existing_key = wallet_api_keys.get(wallet_address)
            usage_data = {}
        
        if not existing_key:
            return {
                "wallet_address": wallet_address,
                "has_api_key": False,
                "message": "No API key found for this wallet"
            }
        
        return {
            "wallet_address": wallet_address,
            "has_api_key": True,
            "api_key": existing_key,
            "usage_stats": {
                "usage_count": int(usage_data.get("usage_count", 0)),
                "threat_score": float(usage_data.get("threat_score", 0.0)),
                "tier": usage_data.get("tier", "pro")
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting wallet API key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get wallet API key: {str(e)}")

@app.post("/api/v1/credit/score")
async def get_credit_score(wallet_address: str):
    """Simple credit scoring endpoint"""
    try:
        # Validate wallet address
        if not wallet_address or len(wallet_address) != 58:
            raise HTTPException(status_code=400, detail="Valid Algorand wallet address required")
        
        # Generate realistic credit score based on wallet
        wallet_hash = hashlib.sha256(wallet_address.encode()).hexdigest()
        base_score = int(wallet_hash[:3], 16) % 300 + 550  # Score between 550-850
        
        return {
            "wallet_address": wallet_address,
            "credit_score": base_score,
            "on_chain_score": (base_score - 550) / 3,  # Convert to 0-100 scale
            "off_chain_score": 75.0,  # Default business score
            "risk_level": "low" if base_score > 750 else "medium" if base_score > 650 else "high",
            "max_loan_amount": base_score * 1000000,  # In microAlgos
            "recommended_interest_rate": 12.0 - (base_score - 550) / 50,  # 6-12%
            "security_context": {
                "api_key_tier": "pro",
                "threat_score": 1.0,
                "validation_timestamp": time.time()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in credit scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Credit scoring failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting AlgoCredit Web3 Security Firewall API...")
    print("📋 Endpoints:")
    print("   • GET  /api/v1/security/health")
    print("   • POST /api/v1/security/generate-key")
    print("   • GET  /api/v1/security/wallet-key/{wallet}")
    print("   • POST /api/v1/credit/score")
    print("   • GET  /docs")
    print("🌐 Server: http://localhost:8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
