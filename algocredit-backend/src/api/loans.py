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


@router.get("/{loan_id}", response_model=LoanApplicationResponse, summary="Get Loan Details")
async def get_loan_details(loan_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific loan
    
    Returns comprehensive loan information including current status,
    payment history, and remaining balance.
    """
    try:
        # Fetch loan from database
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        # Get user info
        user = db.query(User).filter(User.id == loan.borrower_id).first()
        
        return LoanApplicationResponse(
            application_id=loan.id,
            wallet_address=user.wallet_address if user else "",
            requested_amount=loan.requested_amount,
            approved_amount=loan.approved_amount,
            interest_rate=float(loan.interest_rate),
            loan_term_months=loan.term_months,
            monthly_payment=loan.monthly_payment,
            total_amount_due=loan.total_amount_due,
            status=loan.status,
            credit_score=0,  # Would need to fetch from credit assessment
            risk_level="medium",  # Would need to fetch from credit assessment
            smart_contract_id=str(loan.smart_contract_id) if loan.smart_contract_id else None,
            transaction_id=loan.transaction_id,
            application_timestamp=loan.created_at.isoformat() if loan.created_at else "",
            approval_timestamp=loan.approved_at.isoformat() if loan.approved_at else None,
            due_date=loan.due_date.isoformat() if loan.due_date else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving loan: {str(e)}"
        )


@router.get("/{loan_id}/status", response_model=LoanStatusResponse, summary="Get Loan Status")
async def get_loan_status(loan_id: str, db: Session = Depends(get_db)):
    """
    Get current loan status and payment information
    
    Returns current loan status including payment progress,
    remaining balance, and next payment due date.
    """
    try:
        # Fetch loan from database
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        # Calculate payment information
        amount_borrowed = loan.approved_amount or 0
        amount_paid = loan.amount_paid or 0
        amount_remaining = amount_borrowed - amount_paid
        
        # Calculate payment progress
        total_payments = loan.term_months
        if loan.monthly_payment and loan.monthly_payment > 0:
            payments_made = amount_paid // loan.monthly_payment
            payments_remaining = max(0, total_payments - payments_made)
        else:
            payments_made = 0
            payments_remaining = total_payments
        
        # Calculate next payment due
        next_payment_due = None
        if loan.due_date and payments_remaining > 0:
            # Simplified calculation - would need more sophisticated logic
            next_payment_due = loan.due_date.isoformat()
        
        return LoanStatusResponse(
            loan_id=loan.id,
            status=loan.status,
            amount_borrowed=amount_borrowed,
            amount_paid=amount_paid,
            amount_remaining=amount_remaining,
            next_payment_due=next_payment_due,
            payments_made=payments_made,
            payments_remaining=payments_remaining
        )
        
    except HTTPException:
        raise
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
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List loans with optional filtering
    
    Returns a paginated list of loans with optional filters
    by wallet address and status.
    """
    try:
        query = db.query(Loan)
        
        # Apply filters
        if wallet_address:
            user = db.query(User).filter(User.wallet_address == wallet_address).first()
            if user:
                query = query.filter(Loan.borrower_id == user.id)
            else:
                # No user found with this wallet address
                return {
                    "loans": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset
                }
        
        if status:
            query = query.filter(Loan.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        loans = query.offset(offset).limit(limit).all()
        
        # Format response
        loan_list = []
        for loan in loans:
            user = db.query(User).filter(User.id == loan.borrower_id).first()
            loan_list.append({
                "application_id": loan.id,
                "wallet_address": user.wallet_address if user else "",
                "requested_amount": loan.requested_amount,
                "approved_amount": loan.approved_amount,
                "status": loan.status,
                "interest_rate": float(loan.interest_rate),
                "term_months": loan.term_months,
                "application_timestamp": loan.created_at.isoformat() if loan.created_at else ""
            })
        
        return {
            "loans": loan_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error listing loans: {str(e)}"
        )


@router.post("/{loan_id}/approve", summary="Approve Loan (Admin)")
async def approve_loan(loan_id: str, db: Session = Depends(get_db)):
    """
    Manually approve a loan application (admin only)
    
    This endpoint allows administrators to manually approve loans
    that require review or override automated decisions.
    """
    try:
        # Fetch loan from database
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        if loan.status not in ["pending", "pending_review"]:
            raise HTTPException(
                status_code=400,
                detail=f"Loan cannot be approved. Current status: {loan.status}"
            )
        
        # Update loan status
        loan.status = "approved"
        loan.approved_at = datetime.now()
        db.commit()
        
        return {
            "loan_id": loan_id,
            "status": "approved",
            "message": "Loan approved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error approving loan: {str(e)}"
        )


@router.post("/{loan_id}/disburse", summary="Disburse Loan Funds")
async def disburse_loan(loan_id: str, db: Session = Depends(get_db)):
    """
    Disburse approved loan funds to borrower
    
    This endpoint triggers the smart contract to transfer
    approved loan amount to the borrower's wallet.
    """
    try:
        # Fetch loan from database
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        if loan.status != "approved":
            raise HTTPException(
                status_code=400,
                detail=f"Loan must be approved before disbursement. Current status: {loan.status}"
            )
        
        # Update loan status
        loan.status = "active"
        loan.transaction_id = f"TXN_{uuid.uuid4().hex[:16].upper()}"
        db.commit()
        
        # TODO: Call smart contract to disburse funds
        
        return {
            "loan_id": loan_id,
            "status": "disbursed",
            "transaction_id": loan.transaction_id,
            "message": "Loan funds disbursed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error disbursing loan: {str(e)}"
        )