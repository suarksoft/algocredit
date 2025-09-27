# ⚡ 24 SAATLİK SPRINT - CORPORATE TREASURY MVP

## 🎯 **HEDEF**
24 saat içinde çalışan Corporate Treasury platformu - Deposit, Yield, Instant Credit Line

---

## ⏰ **ZAMAN ÇİZELGESİ**

### **SAAT 0-4: PROJECT SETUP & SMART CONTRACTS** (23 Eylül 21:00-01:00)

#### **Saat 0-1: Environment Setup**
```bash
# Project structure
mkdir corporate-treasury-24h
cd corporate-treasury-24h

# Backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn py-algorand-sdk pyteal sqlite3

# Frontend  
npx create-next-app@latest frontend --typescript --tailwind --yes
cd frontend
npm install algosdk @perawallet/connect lucide-react
```

#### **Saat 1-3: Treasury Vault Contract**
```python
# contracts/treasury_vault.py
from pyteal import *

def treasury_vault():
    # Global state
    admin_key = Bytes("admin")
    total_deposits_key = Bytes("total_deposits")
    
    # Local state per company
    company_balance_key = Bytes("balance")
    
    # Create app
    on_create = Seq([
        App.globalPut(admin_key, Txn.sender()),
        App.globalPut(total_deposits_key, Int(0)),
        Return(Int(1))
    ])
    
    # Deposit function
    on_deposit = Seq([
        # Verify payment transaction
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[0].receiver() == Global.current_application_address()),
        
        # Update company balance
        current_balance = App.localGet(Txn.sender(), company_balance_key),
        new_balance = current_balance + Gtxn[0].amount(),
        App.localPut(Txn.sender(), company_balance_key, new_balance),
        
        # Update total deposits
        total_deposits = App.globalGet(total_deposits_key),
        App.globalPut(total_deposits_key, total_deposits + Gtxn[0].amount()),
        
        Return(Int(1))
    ])
    
    # Withdraw function
    on_withdraw = Seq([
        # Get requested amount from args
        withdraw_amount = Btoi(Txn.application_args[1]),
        
        # Check sufficient balance
        current_balance = App.localGet(Txn.sender(), company_balance_key),
        Assert(withdraw_amount <= current_balance),
        
        # Update balance
        new_balance = current_balance - withdraw_amount,
        App.localPut(Txn.sender(), company_balance_key, new_balance),
        
        # Send ALGO back
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: Txn.sender(),
            TxnField.amount: withdraw_amount,
            TxnField.note: Bytes("Corporate Treasury Withdrawal")
        }),
        InnerTxnBuilder.Submit(),
        
        Return(Int(1))
    ])
    
    # Get balance function
    on_get_balance = Seq([
        balance = App.localGet(Txn.sender(), company_balance_key),
        Log(Concat(Bytes("balance:"), Itob(balance))),
        Return(Int(1))
    ])
    
    # Main program
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.application_args[0] == Bytes("deposit"), on_deposit],
        [Txn.application_args[0] == Bytes("withdraw"), on_withdraw],
        [Txn.application_args[0] == Bytes("get_balance"), on_get_balance],
        [Int(1), Return(Int(0))]
    )
    
    return program

if __name__ == "__main__":
    print(compileTeal(treasury_vault(), Mode.Application, version=8))
```

#### **Saat 3-4: Loan Manager Contract**
```python
# contracts/loan_manager.py
from pyteal import *

def loan_manager():
    # Global state
    admin_key = Bytes("admin")
    total_loans_key = Bytes("total_loans")
    
    # Local state per company
    credit_limit_key = Bytes("credit_limit")
    loan_amount_key = Bytes("loan_amount")
    loan_status_key = Bytes("loan_status")  # 0=none, 1=active, 2=repaid
    
    # Create app
    on_create = Seq([
        App.globalPut(admin_key, Txn.sender()),
        App.globalPut(total_loans_key, Int(0)),
        Return(Int(1))
    ])
    
    # Set credit limit (50% of deposit)
    on_set_credit_limit = Seq([
        # Only admin can set limits
        Assert(Txn.sender() == App.globalGet(admin_key)),
        
        # Get company address and limit from args
        company_address = Txn.application_args[1],
        limit = Btoi(Txn.application_args[2]),
        
        # Set credit limit
        App.localPut(company_address, credit_limit_key, limit),
        
        Return(Int(1))
    ])
    
    # Issue loan
    on_issue_loan = Seq([
        # Get requested amount from args
        loan_amount = Btoi(Txn.application_args[1]),
        
        # Check credit limit
        credit_limit = App.localGet(Txn.sender(), credit_limit_key),
        Assert(loan_amount <= credit_limit),
        
        # Check no active loan
        current_status = App.localGet(Txn.sender(), loan_status_key),
        Assert(current_status == Int(0)),
        
        # Update loan state
        App.localPut(Txn.sender(), loan_amount_key, loan_amount),
        App.localPut(Txn.sender(), loan_status_key, Int(1)),
        
        # Update total loans
        total_loans = App.globalGet(total_loans_key),
        App.globalPut(total_loans_key, total_loans + loan_amount),
        
        # Send loan amount
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: Txn.sender(),
            TxnField.amount: loan_amount,
            TxnField.note: Bytes("Corporate Treasury Loan")
        }),
        InnerTxnBuilder.Submit(),
        
        Return(Int(1))
    ])
    
    # Repay loan
    on_repay_loan = Seq([
        # Check active loan
        current_status = App.localGet(Txn.sender(), loan_status_key),
        Assert(current_status == Int(1)),
        
        # Get loan amount
        loan_amount = App.localGet(Txn.sender(), loan_amount_key),
        
        # Verify payment covers loan + 5% interest
        interest = loan_amount * Int(5) / Int(100),
        total_due = loan_amount + interest,
        
        # Verify payment transaction
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[0].amount() >= total_due),
        
        # Mark as repaid
        App.localPut(Txn.sender(), loan_status_key, Int(2)),
        
        Return(Int(1))
    ])
    
    # Main program
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.application_args[0] == Bytes("set_limit"), on_set_credit_limit],
        [Txn.application_args[0] == Bytes("issue_loan"), on_issue_loan],
        [Txn.application_args[0] == Bytes("repay_loan"), on_repay_loan],
        [Int(1), Return(Int(0))]
    )
    
    return program

if __name__ == "__main__":
    print(compileTeal(loan_manager(), Mode.Application, version=8))
```

---

### **SAAT 4-8: BACKEND API** (01:00-05:00)

#### **Saat 4-6: Core API Structure**
```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
import sqlite3
import json
from datetime import datetime

app = FastAPI(title="Corporate Treasury API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Algorand client
algod_client = algod.AlgodClient(
    algod_token="",
    algod_address="https://testnet-api.algonode.cloud"
)

# Database setup
def init_db():
    conn = sqlite3.connect('treasury.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            wallet_address TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            amount INTEGER,
            transaction_hash TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            amount INTEGER,
            interest_rate REAL,
            status TEXT,
            transaction_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Pydantic models
class CompanyLogin(BaseModel):
    name: str
    wallet_address: str

class DepositRequest(BaseModel):
    company_id: int
    amount: int

class WithdrawRequest(BaseModel):
    company_id: int
    amount: int

class LoanRequest(BaseModel):
    company_id: int
    amount: int

# Initialize database
init_db()

@app.get("/")
async def root():
    return {"message": "Corporate Treasury API", "status": "running"}

@app.post("/auth/company-login")
async def company_login(company: CompanyLogin):
    conn = sqlite3.connect('treasury.db')
    cursor = conn.cursor()
    
    # Check if company exists
    cursor.execute("SELECT id FROM companies WHERE wallet_address = ?", (company.wallet_address,))
    result = cursor.fetchone()
    
    if result:
        company_id = result[0]
    else:
        # Create new company
        cursor.execute(
            "INSERT INTO companies (name, wallet_address) VALUES (?, ?)",
            (company.name, company.wallet_address)
        )
        company_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return {"company_id": company_id, "status": "success"}

@app.get("/treasury/balance/{company_id}")
async def get_balance(company_id: int):
    # This would call the smart contract
    # For now, return mock data
    return {
        "company_id": company_id,
        "balance": 10000,  # Mock balance
        "yield_earned": 58,
        "liquid_balance": 3000,
        "yield_balance": 7000
    }

@app.post("/treasury/deposit")
async def deposit(deposit_req: DepositRequest):
    # Mock deposit - in real implementation, this would:
    # 1. Call treasury_vault smart contract
    # 2. Record transaction in database
    # 3. Return transaction hash
    
    conn = sqlite3.connect('treasury.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO deposits (company_id, amount, transaction_hash) VALUES (?, ?, ?)",
        (deposit_req.company_id, deposit_req.amount, "mock_tx_hash_123")
    )
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "amount": deposit_req.amount,
        "transaction_hash": "mock_tx_hash_123",
        "message": "Deposit successful"
    }

@app.post("/treasury/withdraw")
async def withdraw(withdraw_req: WithdrawRequest):
    # Mock withdraw
    return {
        "status": "success",
        "amount": withdraw_req.amount,
        "transaction_hash": "mock_tx_hash_456",
        "message": "Withdrawal successful"
    }

@app.get("/loan/calculate-limit/{company_id}")
async def calculate_credit_limit(company_id: int):
    # Mock calculation - 50% of deposit
    balance = 10000  # Would get from smart contract
    credit_limit = balance * 0.5
    
    return {
        "company_id": company_id,
        "credit_limit": int(credit_limit),
        "used_amount": 0,
        "available_amount": int(credit_limit)
    }

@app.post("/loan/draw")
async def draw_loan(loan_req: LoanRequest):
    # Mock loan issuance
    conn = sqlite3.connect('treasury.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO loans (company_id, amount, interest_rate, status, transaction_hash) VALUES (?, ?, ?, ?, ?)",
        (loan_req.company_id, loan_req.amount, 5.0, "active", "mock_loan_tx_789")
    )
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "amount": loan_req.amount,
        "interest_rate": 5.0,
        "transaction_hash": "mock_loan_tx_789",
        "message": "Loan issued successfully"
    }

@app.get("/analytics/summary/{company_id}")
async def get_summary(company_id: int):
    # Mock analytics
    return {
        "company_id": company_id,
        "total_deposits": 10000,
        "current_balance": 10000,
        "yield_earned": 58,
        "active_loans": 2000,
        "net_profit": 42,
        "monthly_yield_rate": 5.0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### **Saat 6-8: API Testing & Database**
```python
# backend/test_api.py
import requests
import json

# Test API endpoints
base_url = "http://localhost:8000"

def test_company_login():
    response = requests.post(f"{base_url}/auth/company-login", json={
        "name": "Test Corp",
        "wallet_address": "TEST123456789"
    })
    print("Company Login:", response.json())

def test_deposit():
    response = requests.post(f"{base_url}/treasury/deposit", json={
        "company_id": 1,
        "amount": 10000
    })
    print("Deposit:", response.json())

def test_balance():
    response = requests.get(f"{base_url}/treasury/balance/1")
    print("Balance:", response.json())

def test_loan():
    response = requests.post(f"{base_url}/loan/draw", json={
        "company_id": 1,
        "amount": 2000
    })
    print("Loan:", response.json())

if __name__ == "__main__":
    test_company_login()
    test_deposit()
    test_balance()
    test_loan()
```

---

### **SAAT 8-16: FRONTEND DEVELOPMENT** (05:00-13:00)

#### **Saat 8-10: Core Components**
```jsx
// frontend/components/WalletConnect.jsx
'use client';
import { useState, useEffect } from 'react';
import { PeraWalletConnect } from '@perawallet/connect';

const peraWallet = new PeraWalletConnect();

export default function WalletConnect() {
  const [account, setAccount] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  const connectWallet = async () => {
    try {
      const accounts = await peraWallet.connect();
      if (accounts.length) {
        setAccount(accounts[0]);
        setIsConnected(true);
        
        // Login to backend
        await fetch('http://localhost:8000/auth/company-login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'Demo Company',
            wallet_address: accounts[0]
          })
        });
      }
    } catch (error) {
      console.error('Wallet connection failed:', error);
    }
  };

  const disconnectWallet = () => {
    peraWallet.disconnect();
    setAccount(null);
    setIsConnected(false);
  };

  return (
    <div className="bg-blue-50 p-4 rounded-lg">
      {!isConnected ? (
        <button
          onClick={connectWallet}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Connect Pera Wallet
        </button>
      ) : (
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Connected</p>
            <p className="font-mono text-sm">{account?.slice(0, 6)}...{account?.slice(-4)}</p>
          </div>
          <button
            onClick={disconnectWallet}
            className="text-red-600 hover:text-red-800"
          >
            Disconnect
          </button>
        </div>
      )}
    </div>
  );
}
```

```jsx
// frontend/components/BalanceCard.jsx
'use client';
import { useState, useEffect } from 'react';

export default function BalanceCard({ companyId }) {
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (companyId) {
      fetchBalance();
    }
  }, [companyId]);

  const fetchBalance = async () => {
    try {
      const response = await fetch(`http://localhost:8000/treasury/balance/${companyId}`);
      const data = await response.json();
      setBalance(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch balance:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (!balance) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-500">No balance data available</p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold mb-4">Corporate Treasury</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-blue-100 text-sm">Total Balance</p>
          <p className="text-2xl font-bold">{balance.balance?.toLocaleString()} ALGO</p>
        </div>
        <div>
          <p className="text-blue-100 text-sm">Yield Earned</p>
          <p className="text-xl font-semibold text-green-300">+{balance.yield_earned} ALGO</p>
        </div>
      </div>
      
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-blue-100">Liquid</p>
          <p className="font-semibold">{balance.liquid_balance} ALGO</p>
        </div>
        <div>
          <p className="text-blue-100">In Yield</p>
          <p className="font-semibold">{balance.yield_balance} ALGO</p>
        </div>
      </div>
    </div>
  );
}
```

#### **Saat 10-12: Main Pages**
```jsx
// frontend/pages/dashboard.jsx
'use client';
import { useState, useEffect } from 'react';
import WalletConnect from '../components/WalletConnect';
import BalanceCard from '../components/BalanceCard';
import DepositModal from '../components/DepositModal';
import LoanCalculator from '../components/LoanCalculator';

export default function Dashboard() {
  const [companyId, setCompanyId] = useState(null);
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [showLoanModal, setShowLoanModal] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Corporate Treasury</h1>
          <p className="text-gray-600">Manage your company's ALGO assets with yield and instant credit</p>
        </header>

        <div className="mb-6">
          <WalletConnect onConnect={setCompanyId} />
        </div>

        {companyId && (
          <>
            <div className="mb-8">
              <BalanceCard companyId={companyId} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-4">Treasury Management</h3>
                <div className="space-y-3">
                  <button
                    onClick={() => setShowDepositModal(true)}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Deposit ALGO
                  </button>
                  <button className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors">
                    Withdraw ALGO
                  </button>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-4">Credit Line</h3>
                <div className="space-y-3">
                  <button
                    onClick={() => setShowLoanModal(true)}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Take Loan
                  </button>
                  <button className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors">
                    Repay Loan
                  </button>
                </div>
              </div>
            </div>
          </>
        )}

        {showDepositModal && (
          <DepositModal
            companyId={companyId}
            onClose={() => setShowDepositModal(false)}
          />
        )}

        {showLoanModal && (
          <LoanCalculator
            companyId={companyId}
            onClose={() => setShowLoanModal(false)}
          />
        )}
      </div>
    </div>
  );
}
```

#### **Saat 12-16: Additional Components & Polish**
```jsx
// frontend/components/DepositModal.jsx
'use client';
import { useState } from 'react';

export default function DepositModal({ companyId, onClose }) {
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDeposit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/treasury/deposit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: companyId,
          amount: parseInt(amount)
        })
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Deposit successful!');
        onClose();
        window.location.reload(); // Refresh to update balance
      } else {
        alert('Deposit failed');
      }
    } catch (error) {
      console.error('Deposit error:', error);
      alert('Deposit failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Deposit ALGO</h3>
        
        <form onSubmit={handleDeposit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amount (ALGO)
            </label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter amount"
              required
            />
          </div>
          
          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Deposit'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

### **SAAT 16-20: INTEGRATION & TESTING** (13:00-17:00)

#### **Saat 16-18: End-to-End Integration**
```bash
# Start backend
cd backend
python main.py

# Start frontend (new terminal)
cd frontend
npm run dev

# Test complete flow
# 1. Open http://localhost:3000
# 2. Connect wallet
# 3. Deposit ALGO
# 4. Take loan
# 5. Check analytics
```

#### **Saat 18-20: Demo Preparation**
```jsx
// frontend/pages/demo.jsx
'use client';
import { useState } from 'react';

export default function Demo() {
  const [step, setStep] = useState(0);
  
  const demoSteps = [
    "1. CEO connects Pera Wallet",
    "2. Dashboard shows 0 ALGO balance",
    "3. CEO deposits 10,000 ALGO",
    "4. System shows: 7,000 ALGO in yield, 3,000 ALGO liquid",
    "5. CEO takes 2,000 ALGO instant loan",
    "6. Monthly report: +58 ALGO earned, -16 ALGO interest = +42 ALGO profit"
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">
          Corporate Treasury Demo
        </h1>
        
        <div className="bg-gray-800 p-6 rounded-lg mb-8">
          <h2 className="text-xl font-semibold mb-4">Demo Steps</h2>
          <div className="space-y-2">
            {demoSteps.map((stepText, index) => (
              <div
                key={index}
                className={`p-3 rounded ${
                  index <= step ? 'bg-green-600' : 'bg-gray-700'
                }`}
              >
                {stepText}
              </div>
            ))}
          </div>
        </div>

        <div className="text-center">
          <button
            onClick={() => setStep(Math.min(step + 1, demoSteps.length - 1))}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 mr-4"
          >
            Next Step
          </button>
          <button
            onClick={() => setStep(0)}
            className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700"
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

### **SAAT 20-24: FINAL POLISH & DEPLOYMENT** (17:00-21:00)

#### **Saat 20-22: UI Polish & Animations**
```css
/* frontend/styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .card-hover {
    @apply transition-all duration-300 hover:shadow-lg hover:scale-105;
  }
  
  .button-primary {
    @apply bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold;
  }
  
  .gradient-bg {
    @apply bg-gradient-to-r from-blue-500 to-purple-600;
  }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-slide-up {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
```

#### **Saat 22-24: Deployment & Final Testing**
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///treasury.db
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
    command: npm run dev
```

```bash
# Final deployment commands
# 1. Test everything locally
npm run test
python -m pytest backend/tests/

# 2. Build for production
cd frontend && npm run build
cd backend && python -m pip freeze > requirements.txt

# 3. Deploy to Vercel (frontend)
vercel --prod

# 4. Deploy to Railway (backend)
railway login
railway init
railway up
```

---

## 🎯 **24 SAAT SONUNDA ELDE EDECEKLERİMİZ**

### **✅ Çalışan Özellikler**
- [x] Pera Wallet bağlantısı
- [x] ALGO deposit/withdraw
- [x] Instant credit line (50% of deposit)
- [x] Real-time balance gösterimi
- [x] Yield calculation (5% APY)
- [x] Loan management
- [x] Analytics dashboard

### **🚀 Demo Ready**
- [x] 5 dakikalık live demo
- [x] Professional UI/UX
- [x] Mobile responsive
- [x] Error handling
- [x] Loading states

### **📊 Success Metrics**
- [x] <3 saniye transaction time
- [x] 100% uptime during demo
- [x] Smooth user experience
- [x] Professional presentation

---

## 🏆 **HACKATHON WINNING FACTORS**

### **Technical Excellence**
- PyTeal smart contracts
- Algorand SDK integration
- Clean architecture
- Error handling

### **Innovation**
- Corporate treasury use case
- Instant credit line
- Yield optimization
- Simple but effective

### **Impact**
- Real business value
- Algorand adoption
- Corporate onboarding
- Scalable solution

### **Presentation**
- Live demo execution
- Clear value proposition
- Professional delivery
- Wow factor

---

**BAŞLANGIÇ ZAMANI**: 23 Eylül 2025, 21:00  
**BİTİŞ ZAMANI**: 24 Eylül 2025, 21:00  
**HEDEF**: Çalışan Corporate Treasury MVP

---

*24 saatte çalışan bir platform! Hemen başlayalım! 🚀*
