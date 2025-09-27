"""
Corporate Treasury Marketplace API
24-Hour Sprint Implementation
Yatırımcıları startup'larla buluşturan platform
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import sqlite3
import json
from datetime import datetime

# Import existing routers (will adapt them)
from src.api.credit import router as credit_router
from src.api.loans import router as loans_router

# Application metadata
app_metadata = {
    "title": "Corporate Treasury Marketplace API",
    "description": "Connecting Investors with Startups on Algorand",
    "version": "24h-sprint-1.0.0",
    "contact": {
        "name": "Corporate Treasury Team",
        "url": "https://corporate-treasury.io",
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
    allow_origins=["http://localhost:3000", "https://algocredit.vercel.app"],
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
@app.post("/api/v1/credit/score", tags=["Credit Scoring"])
async def get_credit_score(wallet_address: str):
    """
    Temporary credit scoring endpoint
    TODO: Move to proper credit router with full implementation
    """
    if not wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address is required")
    
    # Mock response for now
    return {
        "wallet_address": wallet_address,
        "credit_score": 750,  # Mock score
        "on_chain_score": 65.5,
        "off_chain_score": 84.5,
        "risk_level": "medium",
        "max_loan_amount": 50000,
        "recommended_interest_rate": 8.5,
        "assessment_timestamp": "2025-09-23T14:30:00Z"
    }


# Temporary loan application endpoint
@app.post("/api/v1/loans/apply", tags=["Loans"])
async def apply_for_loan(
    wallet_address: str,
    requested_amount: int,
    loan_term_months: int = 12
):
    """
    Temporary loan application endpoint
    TODO: Move to proper loans router with full implementation
    """
    if not wallet_address or requested_amount <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Valid wallet address and loan amount required"
        )
    
    # Mock response for now
    return {
        "application_id": "loan_12345",
        "wallet_address": wallet_address,
        "requested_amount": requested_amount,
        "approved_amount": min(requested_amount, 50000),  # Mock approval logic
        "interest_rate": 8.5,
        "loan_term_months": loan_term_months,
        "status": "approved" if requested_amount <= 50000 else "pending_review",
        "smart_contract_id": "123456789",  # Mock contract ID
        "application_timestamp": "2025-09-23T14:30:00Z"
    }


# Include API routers
app.include_router(credit_router, prefix="/api/v1/credit", tags=["Credit Scoring"])
app.include_router(loans_router, prefix="/api/v1/loans", tags=["Loans"])
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])  # Will be added later


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
