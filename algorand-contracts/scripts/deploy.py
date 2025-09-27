"""
Deployment script for AlgoCredit smart contracts
"""

import os
import sys
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk import transaction
from algosdk.atomic_transaction_composer import AtomicTransactionComposer
import base64
from pathlib import Path

# Add contracts directory to path
sys.path.append(str(Path(__file__).parent.parent / "contracts"))

from loan_pool import loan_pool_contract, clear_state_program
from pyteal import compileTeal, Mode


class AlgorandDeployer:
    def __init__(self, node_url="https://testnet-api.algonode.cloud", node_token=""):
        """Initialize Algorand client"""
        self.algod_client = algod.AlgodClient(node_token, node_url)
        self.admin_private_key = None
        self.admin_address = None
        
    def setup_admin_account(self, private_key=None):
        """Setup admin account for deployment"""
        if private_key:
            self.admin_private_key = private_key
            self.admin_address = account.address_from_private_key(private_key)
        else:
            # Generate new account for testing
            self.admin_private_key, self.admin_address = account.generate_account()
            print(f"Generated new admin account: {self.admin_address}")
            print(f"Private key: {self.admin_private_key}")
            print("⚠️  Please fund this account with TestNet ALGOs from the faucet:")
            print("   https://testnet.algoexplorer.io/dispenser")
            
        return self.admin_address
    
    def get_account_balance(self, address):
        """Get account balance"""
        try:
            account_info = self.algod_client.account_info(address)
            return account_info['amount']
        except Exception as e:
            print(f"Error getting account balance: {e}")
            return 0
    
    def compile_contract(self):
        """Compile the smart contract"""
        print("🔨 Compiling smart contract...")
        
        # Compile approval program
        approval_program = loan_pool_contract()
        approval_teal = compileTeal(approval_program, Mode.Application, version=8)
        approval_result = self.algod_client.compile(approval_teal)
        approval_binary = base64.b64decode(approval_result['result'])
        
        # Compile clear state program
        clear_program = clear_state_program()
        clear_teal = compileTeal(clear_program, Mode.Application, version=8)
        clear_result = self.algod_client.compile(clear_teal)
        clear_binary = base64.b64decode(clear_result['result'])
        
        print("✅ Smart contract compiled successfully")
        return approval_binary, clear_binary
    
    def deploy_contract(self):
        """Deploy the smart contract to Algorand"""
        print("🚀 Deploying smart contract to Algorand TestNet...")
        
        # Check admin account balance
        balance = self.get_account_balance(self.admin_address)
        if balance < 1000000:  # 1 ALGO minimum
            print(f"❌ Insufficient balance: {balance/1000000:.6f} ALGO")
            print("Please fund the admin account with TestNet ALGOs")
            return None
        
        print(f"💰 Admin account balance: {balance/1000000:.6f} ALGO")
        
        # Compile contract
        approval_binary, clear_binary = self.compile_contract()
        
        # Get suggested parameters
        params = self.algod_client.suggested_params()
        
        # Define schema
        global_schema = transaction.StateSchema(
            num_uints=6,  # pool_balance, total_loans, total_repaid, default_rate, min_credit_score, admin
            num_byte_slices=0
        )
        
        local_schema = transaction.StateSchema(
            num_uints=5,  # credit_score, loan_amount, loan_due_date, interest_rate, loan_status
            num_byte_slices=0
        )
        
        # Create application transaction
        txn = transaction.ApplicationCreateTxn(
            sender=self.admin_address,
            sp=params,
            on_complete=transaction.OnComplete.NoOpOC,
            approval_program=approval_binary,
            clear_program=clear_binary,
            global_schema=global_schema,
            local_schema=local_schema,
            app_args=[]
        )
        
        # Sign transaction
        signed_txn = txn.sign(self.admin_private_key)
        
        try:
            # Submit transaction
            tx_id = self.algod_client.send_transaction(signed_txn)
            print(f"📤 Transaction submitted: {tx_id}")
            
            # Wait for confirmation
            confirmed_txn = transaction.wait_for_confirmation(self.algod_client, tx_id, 4)
            app_id = confirmed_txn['application-index']
            
            print(f"✅ Smart contract deployed successfully!")
            print(f"🆔 Application ID: {app_id}")
            print(f"🔗 View on AlgoExplorer: https://testnet.algoexplorer.io/application/{app_id}")
            
            return app_id
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return None
    
    def fund_contract(self, app_id, amount=5000000):  # 5 ALGO
        """Fund the smart contract with initial capital"""
        print(f"💸 Funding contract with {amount/1000000:.6f} ALGO...")
        
        # Get application address
        app_address = self.get_application_address(app_id)
        
        # Create payment transaction
        params = self.algod_client.suggested_params()
        txn = transaction.PaymentTxn(
            sender=self.admin_address,
            sp=params,
            receiver=app_address,
            amt=amount,
            note=b"Initial funding for AlgoCredit loan pool"
        )
        
        # Sign and submit
        signed_txn = txn.sign(self.admin_private_key)
        tx_id = self.algod_client.send_transaction(signed_txn)
        
        # Wait for confirmation
        transaction.wait_for_confirmation(self.algod_client, tx_id, 4)
        print(f"✅ Contract funded successfully: {tx_id}")
        
        return tx_id
    
    def get_application_address(self, app_id):
        """Get the application address for a given app ID"""
        return transaction.logic.get_application_address(app_id)


def main():
    """Main deployment function"""
    print("🎯 AlgoCredit Smart Contract Deployment")
    print("=" * 50)
    
    # Initialize deployer
    deployer = AlgorandDeployer()
    
    # Setup admin account
    # For production, use: deployer.setup_admin_account(private_key="your_private_key")
    admin_address = deployer.setup_admin_account()
    
    print(f"\n📋 Deployment Summary:")
    print(f"   Admin Address: {admin_address}")
    print(f"   Network: Algorand TestNet")
    print(f"   Node: https://testnet-api.algonode.cloud")
    
    # Check if we should proceed
    if input("\n🤔 Continue with deployment? (y/N): ").lower() != 'y':
        print("Deployment cancelled.")
        return
    
    # Deploy contract
    app_id = deployer.deploy_contract()
    
    if app_id:
        print(f"\n🎉 Deployment completed successfully!")
        print(f"📝 Save these details:")
        print(f"   Application ID: {app_id}")
        print(f"   Admin Address: {admin_address}")
        print(f"   Admin Private Key: {deployer.admin_private_key}")
        
        # Optional: Fund the contract
        if input("\n💰 Fund the contract with 5 ALGO? (y/N): ").lower() == 'y':
            deployer.fund_contract(app_id)
        
        # Save deployment info
        with open("deployment_info.txt", "w") as f:
            f.write(f"AlgoCredit Smart Contract Deployment\n")
            f.write(f"=====================================\n")
            f.write(f"Application ID: {app_id}\n")
            f.write(f"Admin Address: {admin_address}\n")
            f.write(f"Admin Private Key: {deployer.admin_private_key}\n")
            f.write(f"Network: TestNet\n")
            f.write(f"Explorer: https://testnet.algoexplorer.io/application/{app_id}\n")
        
        print(f"\n💾 Deployment info saved to deployment_info.txt")
    else:
        print("❌ Deployment failed.")


if __name__ == "__main__":
    main()
