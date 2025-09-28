"""
Credit scoring API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.models import CreditAssessment, WalletAnalysis, User

from ..services.credit_scoring_service import credit_scoring_service
from ..services.algorand_service import algorand_service

router = APIRouter()


class CreditScoreRequest(BaseModel):
    """Request model for credit score analysis"""
    wallet_address: str = Field(..., description="Algorand wallet address", min_length=58, max_length=58)
    business_data: Optional[Dict[str, Any]] = Field(None, description="Optional business metrics data")


class CreditScoreResponse(BaseModel):
    """Response model for credit score analysis"""
    wallet_address: str
    credit_score: int
    on_chain_score: float
    off_chain_score: float
    risk_level: str
    max_loan_amount: int
    recommended_interest_rate: float
    score_breakdown: Dict[str, Any]
    analysis_timestamp: str
    model_version: str


class WalletAnalysisResponse(BaseModel):
    """Response model for wallet analysis"""
    wallet_address: str
    account_age_days: int
    total_transactions: int
    total_volume: int
    current_balance: int
    balance_stability_score: float
    transaction_frequency_score: float
    asset_diversity_score: float
    dapp_usage_score: float
    analysis_timestamp: str


class BatchCreditScoreRequest(BaseModel):
    """Request model for batch credit scoring"""
    wallet_addresses: List[str] = Field(..., description="List of wallet addresses to analyze")
    business_data: Optional[Dict[str, Any]] = None


class BatchCreditScoreResponse(BaseModel):
    """Response model for batch credit scoring"""
    results: List[Dict[str, Any]]
    processed_count: int
    success_count: int
    error_count: int


@router.post("/score", response_model=CreditScoreResponse, summary="Generate Credit Score")
async def generate_credit_score(request: CreditScoreRequest, db: Session = Depends(get_db)):
    """
    Generate comprehensive credit score for a wallet address
    
    This endpoint analyzes both on-chain blockchain data and optional off-chain
    business metrics to generate a credit score between 300-850.
    
    **On-chain Analysis Includes:**
    - Account age and transaction history
    - Balance stability and volume
    - Asset diversity and DApp usage
    
    **Off-chain Analysis Includes (Optional):**
    - Startup age and team experience
    - Revenue traction and user growth
    - Market size and competitive analysis
    """
    try:
        # Validate wallet address format
        if not algorand_service.is_valid_address(request.wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid Algorand wallet address format"
            )
        
        # Generate credit score analysis
        analysis = await credit_scoring_service.analyze_credit_score(
            wallet_address=request.wallet_address,
            business_data=request.business_data
        )
        
        # Get or create user
        user = db.query(User).filter(User.wallet_address == request.wallet_address).first()
        if not user:
            user = User(
                wallet_address=request.wallet_address
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Save credit assessment to database
        credit_assessment = CreditAssessment(
            user_id=user.id,
            credit_score=analysis["credit_score"],
            on_chain_score=analysis["on_chain_score"],
            off_chain_score=analysis["off_chain_score"],
            risk_level=analysis["risk_level"],
            max_loan_amount=analysis["max_loan_amount"],
            recommended_interest_rate=analysis["recommended_interest_rate"],
            assessment_data=json.dumps(analysis),
            wallet_age_days=analysis.get("wallet_age_days", 1),
            transaction_count=analysis.get("transaction_count", 0),
            total_volume=analysis.get("total_volume", 0)
        )
        db.add(credit_assessment)
        db.commit()
        
        return CreditScoreResponse(**analysis)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during credit analysis: {str(e)}"
        )


@router.get("/wallet/{wallet_address}", response_model=WalletAnalysisResponse, summary="Analyze Wallet")
async def analyze_wallet(wallet_address: str, db: Session = Depends(get_db)):
    """
    Get detailed blockchain analysis for a wallet address
    
    This endpoint provides comprehensive on-chain analysis including:
    - Transaction history and patterns
    - Balance stability metrics
    - Asset diversity analysis
    - DApp interaction scores
    """
    try:
        # Validate wallet address
        if not algorand_service.is_valid_address(wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid Algorand wallet address format"
            )
        
        # Get wallet analysis
        analysis = await algorand_service.analyze_wallet_behavior(wallet_address)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found or unable to analyze"
            )
        
        return WalletAnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during wallet analysis: {str(e)}"
        )


@router.post("/batch", response_model=BatchCreditScoreResponse, summary="Batch Credit Analysis")
async def batch_credit_analysis(request: BatchCreditScoreRequest, db: Session = Depends(get_db)):
    """
    Generate credit scores for multiple wallet addresses
    
    Useful for processing multiple loan applications or portfolio analysis.
    Limited to 10 addresses per request to prevent abuse.
    """
    try:
        if len(request.wallet_addresses) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 wallet addresses allowed per batch request"
            )
        
        results = []
        success_count = 0
        error_count = 0
        
        for address in request.wallet_addresses:
            if not algorand_service.is_valid_address(address):
                results.append({
                    "wallet_address": address,
                    "error": "Invalid wallet address format"
                })
                continue
            
            try:
                analysis = await credit_scoring_service.analyze_credit_score(
                    wallet_address=address,
                    business_data=request.business_data
                )
                results.append(analysis)
                success_count += 1
            except Exception as e:
                results.append({
                    "wallet_address": address,
                    "error": f"Analysis failed: {str(e)}"
                })
                error_count += 1
        
        return BatchCreditScoreResponse(
            results=results,
            processed_count=len(request.wallet_addresses),
            success_count=success_count,
            error_count=error_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during batch analysis: {str(e)}"
        )


@router.get("/model/info", summary="Get Model Information")
async def get_model_info():
    """
    Get information about the credit scoring model
    
    Returns details about the current model version, features,
    and scoring methodology.
    """
    return {
        "model_version": "1.0.0",
        "model_type": "Random Forest Regressor",
        "features": [
            "account_age_days",
            "total_transactions", 
            "current_balance",
            "total_volume",
            "unique_counterparties",
            "dapp_usage_score",
            "business_metrics"
        ],
        "score_range": {"min": 300, "max": 850},
        "weights": {
            "on_chain_analysis": 0.6,
            "off_chain_analysis": 0.4
        },
        "risk_levels": {
            "low": "750-850",
            "medium": "650-749", 
            "high": "550-649",
            "very_high": "300-549"
        },
        "last_updated": "2025-09-23T15:30:00Z"
    }
