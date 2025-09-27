"""
Loan management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
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
    Submit a loan application
    
    This endpoint processes a loan application by:
    1. Analyzing the borrower's credit score
    2. Determining loan eligibility and terms
    3. Creating a loan application record
    4. Optionally auto-approving based on credit score
    
    **Approval Criteria:**
    - Minimum credit score: 550
    - Maximum loan amount based on credit score
    - Automatic approval for scores > 700
    """
    try:
        # Validate wallet address
        if not algorand_service.is_valid_address(request.wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid Algorand wallet address format"
            )
        
        # Generate credit assessment
        credit_analysis = await credit_scoring_service.analyze_credit_score(
            wallet_address=request.wallet_address,
            business_data=request.business_data
        )
        
        credit_score = credit_analysis["credit_score"]
        max_loan_amount = credit_analysis["max_loan_amount"]
        recommended_rate = credit_analysis["recommended_interest_rate"]
        risk_level = credit_analysis["risk_level"]
        
        # Determine loan approval
        if credit_score < 550:
            status = "rejected"
            approved_amount = None
            monthly_payment = None
            total_due = None
        else:
            # Approve loan up to maximum allowed amount
            approved_amount = min(request.requested_amount, max_loan_amount)
            status = "approved" if credit_score >= 650 else "pending_review"
            
            # Calculate monthly payment and total due
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
        
        # Generate application ID
        application_id = f"loan_{uuid.uuid4().hex[:8]}"
        
        # Calculate due date
        due_date = None
        if status == "approved":
            from datetime import timedelta
            due_date = (datetime.now() + timedelta(days=request.loan_term_months * 30)).isoformat()
        
        response = LoanApplicationResponse(
            application_id=application_id,
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
            approval_timestamp=datetime.now().isoformat() if status == "approved" else None,
            due_date=due_date
        )
        
        # TODO: Save to database
        # TODO: If approved, interact with smart contract
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during loan application: {str(e)}"
        )


@router.get("/{loan_id}", response_model=LoanApplicationResponse, summary="Get Loan Details")
async def get_loan_details(loan_id: str):
    """
    Get detailed information about a specific loan
    
    Returns comprehensive loan information including current status,
    payment history, and remaining balance.
    """
    try:
        # TODO: Fetch from database
        # For now, return mock data
        
        # Mock loan data
        mock_loan = {
            "application_id": loan_id,
            "wallet_address": "EXAMPLE123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890AB",
            "requested_amount": 50000000,  # 50 ALGO
            "approved_amount": 40000000,   # 40 ALGO
            "interest_rate": 8.5,
            "loan_term_months": 12,
            "monthly_payment": 3500000,    # ~3.5 ALGO
            "total_amount_due": 42000000,  # ~42 ALGO
            "status": "active",
            "credit_score": 720,
            "risk_level": "medium",
            "smart_contract_id": "123456789",
            "transaction_id": "ABCDEF123456789",
            "application_timestamp": "2025-09-23T15:30:00Z",
            "approval_timestamp": "2025-09-23T15:35:00Z",
            "due_date": "2026-09-23T15:30:00Z"
        }
        
        return LoanApplicationResponse(**mock_loan)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving loan: {str(e)}"
        )


@router.post("/{loan_id}/approve", summary="Approve Loan (Admin)")
async def approve_loan(loan_id: str):
    """
    Manually approve a loan application (admin only)
    
    This endpoint allows administrators to manually approve loans
    that require review or override automated decisions.
    """
    try:
        # TODO: Implement admin authentication
        # TODO: Fetch loan from database
        # TODO: Update status and deploy to smart contract
        
        return {
            "loan_id": loan_id,
            "status": "approved",
            "message": "Loan approved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error approving loan: {str(e)}"
        )


@router.post("/{loan_id}/disburse", summary="Disburse Loan Funds")
async def disburse_loan(loan_id: str):
    """
    Disburse approved loan funds to borrower
    
    This endpoint triggers the smart contract to transfer
    approved loan amount to the borrower's wallet.
    """
    try:
        # TODO: Fetch loan from database
        # TODO: Call smart contract to disburse funds
        # TODO: Update loan status
        
        return {
            "loan_id": loan_id,
            "status": "disbursed",
            "transaction_id": f"TXN_{uuid.uuid4().hex[:16].upper()}",
            "message": "Loan funds disbursed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error disbursing loan: {str(e)}"
        )


@router.get("/{loan_id}/status", response_model=LoanStatusResponse, summary="Get Loan Status")
async def get_loan_status(loan_id: str):
    """
    Get current loan status and payment information
    
    Returns current loan status including payment progress,
    remaining balance, and next payment due date.
    """
    try:
        # TODO: Fetch from database and smart contract
        # Mock status data
        
        mock_status = {
            "loan_id": loan_id,
            "status": "active",
            "amount_borrowed": 40000000,    # 40 ALGO
            "amount_paid": 10000000,       # 10 ALGO paid
            "amount_remaining": 32000000,   # 32 ALGO remaining
            "next_payment_due": "2025-10-23T15:30:00Z",
            "payments_made": 3,
            "payments_remaining": 9
        }
        
        return LoanStatusResponse(**mock_status)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving loan status: {str(e)}"
        )


@router.get("/", summary="List Loans")
async def list_loans(
    wallet_address: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """
    List loans with optional filtering
    
    Returns a paginated list of loans with optional filters
    by wallet address and status.
    """
    try:
        # TODO: Implement database query with filters
        
        # Mock loan list
        mock_loans = [
            {
                "application_id": f"loan_mock_{i}",
                "wallet_address": f"MOCK{i}234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890AB",
                "approved_amount": 30000000 + (i * 5000000),
                "status": ["active", "completed", "pending"][i % 3],
                "credit_score": 650 + (i * 20),
                "application_timestamp": f"2025-09-{20+i}T15:30:00Z"
            }
            for i in range(min(limit, 5))  # Return max 5 mock loans
        ]
        
        return {
            "loans": mock_loans,
            "total": len(mock_loans),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error listing loans: {str(e)}"
        )
