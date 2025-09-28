"""
AlgoCredit API - Simple Blockchain-First Implementation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time

# Try to import services, skip if not available
try:
    from src.services.credit_scoring_service import credit_scoring_service
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI Service not available: {e}")
    AI_AVAILABLE = False

app = FastAPI(
    title="AlgoCredit API",
    description="AI-powered lending on Algorand",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🚀 AlgoCredit API is running!",
        "status": "healthy",
        "ai_enabled": AI_AVAILABLE
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "ai_model": "loaded" if AI_AVAILABLE else "unavailable",
        "timestamp": time.time()
    }

@app.post("/api/v1/credit/score")
async def get_credit_score(
    wallet_address: str,
    requested_amount: int = 50000000,
    loan_term_months: int = 12
):
    """Credit scoring endpoint"""
    
    if not AI_AVAILABLE:
        # Mock response for demo
        return {
            "wallet_address": wallet_address,
            "credit_score": 650,
            "confidence": 75.0,
            "risk_level": "medium",
            "max_loan_amount": requested_amount // 1000000,  # Convert to ALGO
            "recommended_interest_rate": 12.5,
            "model_info": {
                "model_version": "Demo v1.0",
                "scoring_method": "Mock Data",
                "ai_enabled": False
            }
        }
    
    try:
        result = await credit_scoring_service.analyze_wallet_and_score(
            wallet_address
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/marketplace/stats")
async def marketplace_stats():
    return {
        "total_startups": 12,
        "total_investors": 8,
        "total_funding_algo": 25000,
        "success_rate": 85.5
    }

@app.post("/user/login")
async def user_login(wallet_address: str, user_type: str):
    return {
        "success": True,
        "user_id": f"{user_type}_{wallet_address[:10]}",
        "wallet_address": wallet_address,
        "user_type": user_type
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)