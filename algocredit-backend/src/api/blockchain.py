"""
Blockchain integration API endpoints
Simple smart contract integration for AlgoCredit
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

from ..services.algorand_service import algorand_service

router = APIRouter()


class BlockchainLoanRequest(BaseModel):
    """Simple loan request for blockchain"""
    wallet_address: str
    amount: int  # in microAlgos
    term_months: int


@router.get("/status", summary="Get Blockchain Status")
async def get_blockchain_status():
    """Get smart contract and blockchain connection status"""
    try:
        contract_info = await algorand_service.get_contract_info()
        network_status = await algorand_service.get_network_status()
        
        return {
            "status": "connected",
            "contract_id": algorand_service.loan_pool_app_id,
            "network": "testnet",
            "contract_active": True,
            "details": {
                "contract_info": contract_info,
                "network_info": network_status
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/submit-loan", summary="Submit Loan to Blockchain")
async def submit_loan_to_blockchain(request: BlockchainLoanRequest):
    """Submit a loan application directly to the smart contract"""
    try:
        # Submit to blockchain
        blockchain_result = await algorand_service.submit_loan_to_blockchain(
            wallet_address=request.wallet_address,
            amount=request.amount,
            term_months=request.term_months
        )
        
        return {
            "success": True,
            "message": "Loan submitted to blockchain successfully",
            "blockchain_result": blockchain_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit loan to blockchain: {str(e)}"
        )


@router.get("/contract-info", summary="Get Smart Contract Information")
async def get_contract_info():
    """Get detailed smart contract information"""
    try:
        contract_info = await algorand_service.get_contract_info()
        
        return {
            "contract_id": algorand_service.loan_pool_app_id,
            "contract_address": contract_info.get("contract_address", ""),
            "status": "active",
            "deployed_on": "testnet",
            "details": contract_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get contract info: {str(e)}"
        )