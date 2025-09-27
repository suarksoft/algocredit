"""
Corporate Treasury Marketplace API - 24 Hour Sprint
Hızlı ve basit marketplace endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import json
from datetime import datetime

app = FastAPI(
    title="Corporate Treasury Marketplace API",
    description="24-Hour Sprint - Investor-Startup Matching Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
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
    loan_term_months: int = 12

class DepositRequest(BaseModel):
    investor_id: int
    amount: int

class FundingRequest(BaseModel):
    investor_id: int
    startup_id: int

class UserLogin(BaseModel):
    wallet_address: str
    user_type: str  # investor or startup

# Database initialization
def init_marketplace_db():
    """Initialize marketplace database"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    # Investors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            wallet_address TEXT UNIQUE NOT NULL,
            investment_capacity INTEGER,
            risk_preference TEXT,
            current_balance INTEGER DEFAULT 0,
            total_invested INTEGER DEFAULT 0,
            yield_earned INTEGER DEFAULT 0,
            active_investments INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Startups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS startups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            wallet_address TEXT UNIQUE NOT NULL,
            business_description TEXT,
            requested_amount INTEGER,
            loan_term_months INTEGER DEFAULT 12,
            credit_score INTEGER DEFAULT 650,
            interest_rate REAL DEFAULT 8.5,
            funding_status TEXT DEFAULT 'seeking', -- seeking, funded, repaid
            investor_id INTEGER,
            funded_amount INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investor_id) REFERENCES investors (id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL, -- deposit, funding, repayment
            investor_id INTEGER,
            startup_id INTEGER,
            amount INTEGER,
            transaction_hash TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investor_id) REFERENCES investors (id),
            FOREIGN KEY (startup_id) REFERENCES startups (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_marketplace_db()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🏦 Corporate Treasury Marketplace API",
        "status": "running",
        "version": "24h-sprint-1.0.0",
        "endpoints": [
            "/docs",
            "/marketplace/stats",
            "/investor/register",
            "/startup/register",
            "/user/login",
            "/investor/deposit",
            "/startup/available",
            "/funding/execute"
        ]
    }

@app.get("/marketplace/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM investors")
    total_investors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM startups")
    total_startups = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(funded_amount) FROM startups WHERE funding_status = 'funded'")
    result = cursor.fetchone()[0]
    total_funding = result if result else 0
    
    cursor.execute("SELECT COUNT(*) FROM startups WHERE funding_status = 'seeking'")
    available_opportunities = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_investors": total_investors,
        "total_startups": total_startups,
        "total_funding_volume": total_funding,
        "available_opportunities": available_opportunities,
        "platform_fee": "2%",
        "avg_interest_rate": "8.5%"
    }

@app.post("/investor/register")
async def register_investor(investor: InvestorRegistration):
    """Register new investor"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO investors (name, wallet_address, investment_capacity, risk_preference)
            VALUES (?, ?, ?, ?)
        ''', (investor.name, investor.wallet_address, investor.investment_capacity, investor.risk_preference))
        
        investor_id = cursor.lastrowid
        conn.commit()
        
        return {
            "status": "success",
            "investor_id": investor_id,
            "message": f"Investor {investor.name} registered successfully",
            "wallet_address": investor.wallet_address
        }
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Wallet address already registered")
    
    finally:
        conn.close()

@app.post("/startup/register")
async def register_startup(startup: StartupRegistration):
    """Register new startup"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    try:
        # Calculate credit score based on requested amount (simple demo logic)
        if startup.requested_amount <= 10000:
            credit_score = 750
            interest_rate = 6.5
        elif startup.requested_amount <= 50000:
            credit_score = 700
            interest_rate = 8.5
        else:
            credit_score = 650
            interest_rate = 12.0
        
        cursor.execute('''
            INSERT INTO startups (name, wallet_address, business_description, requested_amount, 
                                loan_term_months, credit_score, interest_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (startup.name, startup.wallet_address, startup.business_description, 
              startup.requested_amount, startup.loan_term_months, credit_score, interest_rate))
        
        startup_id = cursor.lastrowid
        conn.commit()
        
        return {
            "status": "success",
            "startup_id": startup_id,
            "message": f"Startup {startup.name} registered successfully",
            "credit_score": credit_score,
            "interest_rate": interest_rate,
            "requested_amount": startup.requested_amount
        }
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Wallet address already registered")
    
    finally:
        conn.close()

@app.post("/user/login")
async def user_login(login: UserLogin):
    """Login user by wallet address"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    if login.user_type == "investor":
        cursor.execute("SELECT * FROM investors WHERE wallet_address = ?", (login.wallet_address,))
        user = cursor.fetchone()
        
        if user:
            return {
                "status": "success",
                "user_type": "investor",
                "user_id": user[0],
                "name": user[1],
                "wallet_address": user[2],
                "current_balance": user[5],
                "total_invested": user[6],
                "yield_earned": user[7],
                "active_investments": user[8]
            }
    
    elif login.user_type == "startup":
        cursor.execute("SELECT * FROM startups WHERE wallet_address = ?", (login.wallet_address,))
        user = cursor.fetchone()
        
        if user:
            return {
                "status": "success",
                "user_type": "startup",
                "user_id": user[0],
                "name": user[1],
                "wallet_address": user[2],
                "business_description": user[3],
                "requested_amount": user[4],
                "credit_score": user[6],
                "interest_rate": user[7],
                "funding_status": user[8],
                "funded_amount": user[10]
            }
    
    conn.close()
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/investor/deposit")
async def investor_deposit(deposit: DepositRequest):
    """Investor deposits ALGO"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    # Update investor balance
    cursor.execute('''
        UPDATE investors 
        SET current_balance = current_balance + ? 
        WHERE id = ?
    ''', (deposit.amount, deposit.investor_id))
    
    # Record transaction
    cursor.execute('''
        INSERT INTO transactions (transaction_type, investor_id, amount, status)
        VALUES ('deposit', ?, ?, 'completed')
    ''', (deposit.investor_id, deposit.amount))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": "Deposit successful",
        "amount": deposit.amount,
        "transaction_id": "mock_tx_" + str(datetime.now().timestamp())
    }

@app.get("/startup/available")
async def get_available_startups():
    """Get list of startups seeking funding"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, business_description, requested_amount, credit_score, 
               interest_rate, loan_term_months, created_at
        FROM startups 
        WHERE funding_status = 'seeking'
        ORDER BY credit_score DESC, created_at DESC
    ''')
    
    startups = []
    for row in cursor.fetchall():
        startups.append({
            "id": row[0],
            "name": row[1],
            "business_description": row[2],
            "requested_amount": row[3],
            "credit_score": row[4],
            "interest_rate": row[5],
            "loan_term_months": row[6],
            "created_at": row[7],
            "risk_level": "Low" if row[4] > 700 else "Medium" if row[4] > 650 else "High"
        })
    
    conn.close()
    
    return {
        "status": "success",
        "available_startups": startups,
        "count": len(startups)
    }

@app.post("/funding/execute")
async def execute_funding(funding: FundingRequest):
    """Execute funding from investor to startup"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    # Get startup details
    cursor.execute("SELECT requested_amount, funding_status FROM startups WHERE id = ?", (funding.startup_id,))
    startup_data = cursor.fetchone()
    
    if not startup_data:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    if startup_data[1] != 'seeking':
        raise HTTPException(status_code=400, detail="Startup is not seeking funding")
    
    requested_amount = startup_data[0]
    
    # Get investor balance
    cursor.execute("SELECT current_balance FROM investors WHERE id = ?", (funding.investor_id,))
    investor_data = cursor.fetchone()
    
    if not investor_data or investor_data[0] < requested_amount:
        raise HTTPException(status_code=400, detail="Insufficient investor balance")
    
    # Calculate platform fee (2%)
    platform_fee = int(requested_amount * 0.02)
    net_amount = requested_amount - platform_fee
    
    # Update investor
    cursor.execute('''
        UPDATE investors 
        SET current_balance = current_balance - ?,
            total_invested = total_invested + ?,
            active_investments = active_investments + 1
        WHERE id = ?
    ''', (requested_amount, requested_amount, funding.investor_id))
    
    # Update startup
    cursor.execute('''
        UPDATE startups 
        SET funding_status = 'funded',
            investor_id = ?,
            funded_amount = ?
        WHERE id = ?
    ''', (funding.investor_id, requested_amount, funding.startup_id))
    
    # Record transaction
    cursor.execute('''
        INSERT INTO transactions (transaction_type, investor_id, startup_id, amount, status)
        VALUES ('funding', ?, ?, ?, 'completed')
    ''', (funding.investor_id, funding.startup_id, requested_amount))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": "Funding executed successfully",
        "funded_amount": requested_amount,
        "net_amount": net_amount,
        "platform_fee": platform_fee,
        "transaction_id": "funding_tx_" + str(datetime.now().timestamp())
    }

@app.get("/investor/{investor_id}/portfolio")
async def get_investor_portfolio(investor_id: int):
    """Get investor portfolio"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    # Get investor info
    cursor.execute("SELECT * FROM investors WHERE id = ?", (investor_id,))
    investor = cursor.fetchone()
    
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    # Get funded startups
    cursor.execute('''
        SELECT id, name, funded_amount, interest_rate, funding_status, loan_term_months
        FROM startups 
        WHERE investor_id = ?
    ''', (investor_id,))
    
    investments = []
    for row in cursor.fetchall():
        expected_return = int(row[2] * (1 + row[3]/100))
        investments.append({
            "startup_id": row[0],
            "startup_name": row[1],
            "invested_amount": row[2],
            "interest_rate": row[3],
            "status": row[4],
            "loan_term": row[5],
            "expected_return": expected_return,
            "profit": expected_return - row[2]
        })
    
    conn.close()
    
    total_invested = sum([inv["invested_amount"] for inv in investments])
    total_expected_return = sum([inv["expected_return"] for inv in investments])
    total_profit = total_expected_return - total_invested
    
    return {
        "investor_id": investor_id,
        "name": investor[1],
        "current_balance": investor[5],
        "total_invested": total_invested,
        "expected_return": total_expected_return,
        "expected_profit": total_profit,
        "roi_percentage": round((total_profit / total_invested * 100), 2) if total_invested > 0 else 0,
        "active_investments": len([inv for inv in investments if inv["status"] == "funded"]),
        "investments": investments
    }

@app.get("/startup/{startup_id}/details")
async def get_startup_details(startup_id: int):
    """Get startup details"""
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM startups WHERE id = ?", (startup_id,))
    startup = cursor.fetchone()
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    conn.close()
    
    return {
        "startup_id": startup[0],
        "name": startup[1],
        "wallet_address": startup[2],
        "business_description": startup[3],
        "requested_amount": startup[4],
        "loan_term_months": startup[5],
        "credit_score": startup[6],
        "interest_rate": startup[7],
        "funding_status": startup[8],
        "funded_amount": startup[10],
        "risk_level": "Low" if startup[6] > 700 else "Medium" if startup[6] > 650 else "High"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
