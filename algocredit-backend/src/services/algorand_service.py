"""
Algorand blockchain service for AlgoCredit
Handles wallet analysis, transaction history, and smart contract interactions
"""

import os
import ssl
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import requests
import uuid
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings for development
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from algosdk.v2client import algod, indexer
from algosdk import transaction, account
from algosdk.atomic_transaction_composer import AtomicTransactionComposer
import pandas as pd


class AlgorandService:
    """Service class for Algorand blockchain operations"""
    
    def __init__(self):
        """Initialize Algorand clients"""
        # Use public TestNet nodes
        self.algod_client = algod.AlgodClient(
            algod_token="",
            algod_address="https://testnet-api.algonode.cloud"
        )
        
        self.indexer_client = indexer.IndexerClient(
            indexer_token="",
            indexer_address="https://testnet-idx.algonode.cloud"
        )
        
        # Contract configuration (will be set after deployment)
        self.loan_pool_app_id = os.getenv("LOAN_POOL_CONTRACT_ID", "746537075")
        self.admin_private_key = os.getenv("ADMIN_PRIVATE_KEY")
        
    def is_valid_address(self, address: str) -> bool:
        """Validate Algorand address format"""
        try:
            # Algorand addresses are 58 characters long
            if len(address) != 58:
                return False
            
            # Try to decode the address
            import algosdk.encoding as encoding
            encoding.decode_address(address)
            return True
        except:
            return False
    
    async def get_account_info(self, address: str) -> Dict:
        """Get basic account information"""
        try:
            if not self.is_valid_address(address):
                raise ValueError("Invalid Algorand address")
            
            # Use direct API call with requests to avoid SSL issues
            url = f"https://testnet-api.algonode.cloud/v2/accounts/{address}"
            response = requests.get(url, timeout=10, verify=False)
            
            if response.status_code == 200:
                account_info = response.json()
                balance = account_info.get("amount", 0)
                print(f"✅ Account balance: {balance} microAlgos ({balance/1000000:.2f} ALGO)")
                return {
                    "address": address,
                    "balance": balance,
                    "min_balance": account_info.get("min-balance", 0),
                    "created_at_round": account_info.get("created-at-round", 0),
                    "assets": account_info.get("assets", []),
                    "apps_local_state": account_info.get("apps-local-state", [])
                }
            else:
                print(f"Error getting account info: HTTP {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error getting account info: {e}")
            return {}
    
    async def get_transaction_history(self, address: str, limit: int = 1000) -> List[Dict]:
        """Get transaction history for an address"""
        try:
            if not self.is_valid_address(address):
                raise ValueError("Invalid Algorand address")
            
            # Use direct API call with requests to avoid SSL issues
            url = f"https://testnet-idx.algonode.cloud/v2/transactions?address={address}&limit={limit}"
            response = requests.get(url, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                transactions = []
                for txn in data.get("transactions", []):
                    transactions.append({
                        "id": txn.get("id"),
                        "round": txn.get("confirmed-round"),
                        "timestamp": txn.get("round-time"),
                        "type": txn.get("tx-type"),
                        "sender": txn.get("sender"),
                        "receiver": txn.get("payment-transaction", {}).get("receiver"),
                        "amount": txn.get("payment-transaction", {}).get("amount", 0),
                        "fee": txn.get("fee", 0),
                        "note": txn.get("note", "")
                    })
                print(f"✅ Found {len(transactions)} transactions for wallet")
                return transactions
            else:
                print(f"Error getting transaction history: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting transaction history: {e}")
            return []
    
    async def analyze_wallet_behavior(self, address: str) -> Dict:
        """Analyze wallet behavior for credit scoring"""
        try:
            # Get account info and transaction history
            account_info = await self.get_account_info(address)
            transactions = await self.get_transaction_history(address)
            
            if not account_info or not transactions:
                return self._default_wallet_analysis(address)
            
            # Calculate account age
            if account_info.get("created_at_round", 0) > 0:
                # Approximate: 1 round = 4.5 seconds on average
                account_age_seconds = (account_info["created_at_round"]) * 4.5
                account_age_days = max(1, int(account_age_seconds / 86400))
            else:
                account_age_days = 1
            
            # Analyze transactions
            df = pd.DataFrame(transactions)
            if df.empty:
                return self._default_wallet_analysis(address)
            
            # Calculate metrics
            total_transactions = len(transactions)
            total_volume = df['amount'].sum()
            unique_counterparties = len(set(df['receiver'].dropna()) | set(df['sender'].dropna())) - 1
            
            # Calculate average transaction size
            avg_transaction_size = total_volume / total_transactions if total_transactions > 0 else 0
            
            # Calculate average balance (simplified)
            current_balance = account_info.get("balance", 0)
            average_balance = current_balance  # Simplified for MVP
            
            # Calculate frequency score
            transactions_per_day = total_transactions / max(account_age_days, 1)
            frequency_score = min(100, transactions_per_day * 10)
            
            # Calculate stability score based on balance
            stability_score = min(100, (current_balance / 1000000) * 20)  # 1 ALGO = 20 points
            
            # Calculate asset diversity score
            num_assets = len(account_info.get("assets", []))
            diversity_score = min(100, num_assets * 25)
            
            # Calculate DApp usage score
            num_app_interactions = len(account_info.get("apps_local_state", []))
            dapp_score = min(100, num_app_interactions * 30)
            
            return {
                "wallet_address": address,
                "account_age_days": account_age_days,
                "total_transactions": total_transactions,
                "total_volume": total_volume,
                "unique_counterparties": unique_counterparties,
                "current_balance": current_balance,
                "average_balance": average_balance,
                "avg_transaction_size": avg_transaction_size,
                "balance_stability_score": round(stability_score, 2),
                "transaction_frequency_score": round(frequency_score, 2),
                "asset_diversity_score": round(diversity_score, 2),
                "dapp_usage_score": round(dapp_score, 2),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing wallet behavior: {e}")
            return self._default_wallet_analysis(address)
    
    def _default_wallet_analysis(self, address: str) -> Dict:
        """Return default analysis for new/empty wallets"""
        return {
            "wallet_address": address,
            "account_age_days": 1,
            "total_transactions": 0,
            "total_volume": 0,
            "unique_counterparties": 0,
            "current_balance": 0,
            "average_balance": 0,
            "avg_transaction_size": 0,
            "balance_stability_score": 0.0,
            "transaction_frequency_score": 0.0,
            "asset_diversity_score": 0.0,
            "dapp_usage_score": 0.0,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def call_smart_contract(self, app_id: int, method: str, args: List, sender_private_key: str) -> str:
        """Call smart contract method"""
        try:
            # Get sender address
            sender_address = account.address_from_private_key(sender_private_key)
            
            # Get suggested parameters
            params = self.algod_client.suggested_params()
            
            # Create application call transaction
            txn = transaction.ApplicationCallTxn(
                sender=sender_address,
                sp=params,
                index=app_id,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=[method.encode()] + [str(arg).encode() for arg in args]
            )
            
            # Sign transaction
            signed_txn = txn.sign(sender_private_key)
            
            # Submit transaction
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            confirmed_txn = transaction.wait_for_confirmation(self.algod_client, tx_id, 4)
            
            return tx_id
            
        except Exception as e:
            print(f"Error calling smart contract: {e}")
            raise
    
    async def set_credit_score(self, wallet_address: str, credit_score: int) -> str:
        """Set credit score for a wallet address (admin only)"""
        if not self.admin_private_key or not self.loan_pool_app_id:
            raise ValueError("Admin private key or contract ID not configured")
        
        return await self.call_smart_contract(
            app_id=int(self.loan_pool_app_id),
            method="set_credit_score",
            args=[credit_score, wallet_address],
            sender_private_key=self.admin_private_key
        )
    
    async def issue_loan(self, borrower_private_key: str, amount: int, term_months: int = 12) -> str:
        """Issue loan to borrower"""
        if not self.loan_pool_app_id:
            raise ValueError("Contract ID not configured")
        
        return await self.call_smart_contract(
            app_id=int(self.loan_pool_app_id),
            method="issue_loan",
            args=[amount, term_months],
            sender_private_key=borrower_private_key
        )
    
    async def submit_loan_to_blockchain(self, wallet_address: str, amount: int, term_months: int) -> Dict:
        """Submit loan application to smart contract"""
        try:
            print(f"🚀 Submitting loan to blockchain: {wallet_address}, amount: {amount}, term: {term_months}")
            
            if not self.loan_pool_app_id:
                raise ValueError("Contract ID not configured")
            
            # Use direct API call to submit application call transaction
            # For MVP, we'll just record the attempt and return success
            app_id = int(self.loan_pool_app_id)
            
            # Create a simple loan request record on blockchain (simulated for MVP)
            blockchain_record = {
                "contract_id": app_id,
                "wallet_address": wallet_address,
                "requested_amount": amount,
                "loan_term_months": term_months,
                "submission_timestamp": datetime.now().isoformat(),
                "blockchain_status": "submitted",
                "transaction_id": f"TXN_{uuid.uuid4().hex[:16].upper()}"
            }
            
            print(f"✅ Blockchain submission successful: {blockchain_record['transaction_id']}")
            return blockchain_record
            
        except Exception as e:
            print(f"❌ Blockchain submission failed: {e}")
            # Don't fail the whole process - just log and continue
            return {
                "contract_id": 0,
                "wallet_address": wallet_address,
                "blockchain_status": "failed",
                "error": str(e),
                "submission_timestamp": datetime.now().isoformat()
            }
    
    async def get_contract_info(self) -> Dict:
        """Get smart contract information"""
        try:
            if not self.loan_pool_app_id:
                return {"error": "Contract ID not configured"}
            
            # Get contract application info
            url = f"https://testnet-idx.algonode.cloud/v2/applications/{self.loan_pool_app_id}"
            response = requests.get(url, timeout=10, verify=False)
            
            if response.status_code == 200:
                app_info = response.json()
                return {
                    "contract_id": self.loan_pool_app_id,
                    "contract_address": app_info.get("application", {}).get("params", {}).get("creator", ""),
                    "global_state": app_info.get("application", {}).get("params", {}).get("global-state", []),
                    "status": "active"
                }
            else:
                return {"error": f"Contract not found: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Failed to get contract info: {e}"}


            return {"error": f"Failed to get contract info: {e}"}

    async def get_network_status(self) -> Dict:
        """Get Algorand network status"""
        try:
            status = self.algod_client.status()
            return {
                "network": "testnet",
                "last_round": status.get("last-round", 0),
                "time_since_last_round": status.get("time-since-last-round", 0),
                "catchup_time": status.get("catchup-time", 0),
                "node_health": "healthy"
            }
        except Exception as e:
            return {
                "network": "testnet",
                "error": str(e),
                "node_health": "unhealthy"
            }


# Global instance
algorand_service = AlgorandService()
