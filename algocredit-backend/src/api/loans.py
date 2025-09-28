"""
Loan management API endpoints (No Database - Smart Contract Only)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from ..services.credit_scoring_service import credit_scoring_service
from ..services.algorand_service import algorand_service

router = APIRouter()


class LoanApplicationRequest(BaseModel):
    """Request model for loan application"""
    wallet_address: str = Field(..., description="Borrower's Algorand wallet address")
    requested_amount: int = Field(..., description="Requested loan amount in microAlgos", gt=0)
    loan_term_months: int = Field(12, description="Loan term in months", ge=1, le=60)
    purpose: Optional[str] = Field(None, description="Loan purpose description")
    business_data: Optional[dict] = Field(None, description="Business metrics for credit assessment")


class LoanApplicationResponse(BaseModel):
    """Response model for loan application"""
    application_id: str
    wallet_address: str
    requested_amount: int
    approved_amount: Optional[int]
    interest_rate: float
    loan_term_months: int
    monthly_payment: Optional[int]
    total_amount_due: Optional[int]
    status: str  # pending, approved, rejected, active, completed, defaulted
    credit_score: int
    risk_level: str
    smart_contract_id: Optional[str]
    transaction_id: Optional[str]
    application_timestamp: str
    approval_timestamp: Optional[str]
    due_date: Optional[str]


class LoanStatusResponse(BaseModel):
    """Response model for loan status"""
    loan_id: str
    status: str
    amount_borrowed: int
    amount_paid: int
    amount_remaining: int
    next_payment_due: Optional[str]
    payments_made: int
    payments_remaining: int


@router.post("/apply", response_model=LoanApplicationResponse, summary="Apply for Loan")
async def apply_for_loan(request: LoanApplicationRequest):
    """
    Submit a loan application with AI-powered credit assessment
    
    This endpoint:
    1. Validates the loan application
    2. Performs AI credit scoring
    3. Makes automated loan decision
    4. Returns loan approval/rejection with terms
    
    All data will be stored in smart contracts (not database)
    """
    try:
        # Validate wallet address
        if not algorand_service.is_valid_address(request.wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid Algorand wallet address format"
            )
        
        # Perform comprehensive credit assessment
        credit_assessment = await credit_scoring_service.analyze_wallet_and_score(
            wallet_address=request.wallet_address,
            requested_amount=request.requested_amount,
            loan_term_months=request.loan_term_months,
            business_data=request.business_data
        )
        
        if not credit_assessment:
            raise HTTPException(
                status_code=400,
                detail="Unable to assess creditworthiness"
            )
        
        # Loan decision logic based on AI assessment
        credit_score = credit_assessment["credit_score"]
        max_loan_amount = credit_assessment["max_loan_amount"]
        risk_level = credit_assessment["risk_level"]
        recommended_rate = credit_assessment["recommended_interest_rate"]
        
        # Determine loan approval
        if credit_score >= 650 and request.requested_amount <= max_loan_amount:
            status = "approved"
            approved_amount = min(request.requested_amount, max_loan_amount)
            
            # Calculate monthly payment
            monthly_rate = recommended_rate / 100 / 12
            num_payments = request.loan_term_months
            
            if monthly_rate > 0:
                monthly_payment = int(
                    approved_amount * 
                    (monthly_rate * (1 + monthly_rate) ** num_payments) /
                    ((1 + monthly_rate) ** num_payments - 1)
                )
            else:
                monthly_payment = int(approved_amount / num_payments)
            
            total_due = monthly_payment * num_payments
            
        elif credit_score >= 500:
            status = "conditional_approval"
            approved_amount = min(int(request.requested_amount * 0.7), max_loan_amount)
            interest_rate = recommended_rate + 2
            
            monthly_rate = interest_rate / 100 / 12
            num_payments = request.loan_term_months
            
            if monthly_rate > 0:
                monthly_payment = int(
                    approved_amount * 
                    (monthly_rate * (1 + monthly_rate) ** num_payments) /
                    ((1 + monthly_rate) ** num_payments - 1)
                )
            else:
                monthly_payment = int(approved_amount / num_payments)
            
            total_due = monthly_payment * num_payments
            recommended_rate = interest_rate
            
        else:
            status = "rejected"
            approved_amount = None
            monthly_payment = None
            total_due = None
        
        # Generate loan ID
        loan_id = f"loan_{uuid.uuid4().hex[:12]}"
        
        # Calculate due date
        due_date = None
        if status in ["approved", "conditional_approval"]:
            due_date = (datetime.now() + timedelta(days=request.loan_term_months * 30)).isoformat()
        
        response = LoanApplicationResponse(
            application_id=loan_id,
            wallet_address=request.wallet_address,
            requested_amount=request.requested_amount,
            approved_amount=approved_amount,
            interest_rate=recommended_rate,
            loan_term_months=request.loan_term_months,
            monthly_payment=monthly_payment,
            total_amount_due=total_due,
            status=status,
            credit_score=credit_score,
            risk_level=risk_level,
            smart_contract_id=None,  # Will be set after smart contract deployment
            transaction_id=None,     # Will be set after blockchain transaction
            application_timestamp=datetime.now().isoformat(),
            approval_timestamp=datetime.now().isoformat() if status in ["approved", "conditional_approval"] else None,
            due_date=due_date
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during loan application: {str(e)}"
        )

@router.get("/blockchain/status", summary="Get Blockchain Status")
async def get_blockchain_status():
    """Get smart contract and blockchain status"""
    try:
        contract_info = await algorand_service.get_contract_info()
        network_status = await algorand_service.get_network_status()
        
        return {
            "blockchain_connected": True,
            "contract_info": contract_info,
            "network_status": network_status,
            "contract_id": algorand_service.loan_pool_app_id
        }
    except Exception as e:
        return {
            "blockchain_connected": False,
            "error": str(e)
        }

# TODO: Add more endpoints for smart contract integration
# @router.get("/status/{loan_id}")  - Get loan status from smart contract
# @router.post("/repay/{loan_id}")  - Make loan repayment 
# @router.get("/history/{wallet_address}")  - Get loan history from blockchain