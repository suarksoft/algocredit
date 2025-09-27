"""
Performance Optimized Corporate Treasury API
24-Hour Sprint - Caching and Performance Enhancements
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
import json
import time
from datetime import datetime, timedelta
import asyncio
import hashlib

app = FastAPI(
    title="Corporate Treasury Marketplace API - Optimized",
    description="24-Hour Sprint - High Performance Investor-Startup Platform",
    version="1.1.0-optimized"
)

# Add performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for performance
cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 30  # 30 seconds cache

def get_cache_key(endpoint: str, params: str = "") -> str:
    """Generate cache key"""
    return hashlib.md5(f"{endpoint}:{params}".encode()).hexdigest()

def get_cached_data(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get data from cache if not expired"""
    if cache_key in cache:
        cached_item = cache[cache_key]
        if time.time() - cached_item['timestamp'] < CACHE_TTL:
            return cached_item['data']
        else:
            # Remove expired cache
            del cache[cache_key]
    return None

def set_cache_data(cache_key: str, data: Dict[str, Any]) -> None:
    """Set data in cache with timestamp"""
    cache[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }

# Database connection pool (simple implementation)
def get_db_connection():
    """Get database connection with optimizations"""
    conn = sqlite3.connect('marketplace.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    # Enable WAL mode for better performance
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    return conn

# Pydantic models (same as before but with performance hints)
class InvestorRegistration(BaseModel):
    name: str
    wallet_address: str
    investment_capacity: int
    risk_preference: str

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
    user_type: str

# Initialize optimized database
def init_optimized_db():
    """Initialize database with performance optimizations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create indexes for better performance
    cursor.executescript('''
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_investors_wallet ON investors(wallet_address);
        CREATE INDEX IF NOT EXISTS idx_startups_wallet ON startups(wallet_address);
        CREATE INDEX IF NOT EXISTS idx_startups_status ON startups(funding_status);
        CREATE INDEX IF NOT EXISTS idx_transactions_investor ON transactions(investor_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_startup ON transactions(startup_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
        
        -- Analyze tables for query optimization
        ANALYZE;
    ''')
    
    conn.commit()
    conn.close()

# Initialize optimized database
init_optimized_db()

@app.get("/")
async def root():
    """Root endpoint with caching"""
    cache_key = get_cache_key("root")
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return cached_data
    
    data = {
        "message": "🏦 Corporate Treasury Marketplace API - Optimized",
        "status": "running",
        "version": "1.1.0-optimized",
        "performance": "Enhanced with caching",
        "cache_ttl": f"{CACHE_TTL}s",
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
    
    set_cache_data(cache_key, data)
    return data

@app.get("/marketplace/stats")
async def get_marketplace_stats_cached():
    """Get marketplace statistics with caching"""
    cache_key = get_cache_key("marketplace_stats")
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        cached_data['cached'] = True
        cached_data['cache_age'] = f"{int(time.time() - cache[cache_key]['timestamp'])}s"
        return cached_data
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Optimized queries with single connection
    stats_query = '''
        SELECT 
            (SELECT COUNT(*) FROM investors) as total_investors,
            (SELECT COUNT(*) FROM startups) as total_startups,
            (SELECT COALESCE(SUM(funded_amount), 0) FROM startups WHERE funding_status = 'funded') as total_funding,
            (SELECT COUNT(*) FROM startups WHERE funding_status = 'seeking') as available_opportunities
    '''
    
    cursor.execute(stats_query)
    result = cursor.fetchone()
    conn.close()
    
    data = {
        "total_investors": result[0],
        "total_startups": result[1], 
        "total_funding_volume": result[2],
        "available_opportunities": result[3],
        "platform_fee": "2%",
        "avg_interest_rate": "8.5%",
        "cached": False,
        "response_time": "optimized"
    }
    
    set_cache_data(cache_key, data)
    return data

@app.get("/startup/available")
async def get_available_startups_cached():
    """Get available startups with caching"""
    cache_key = get_cache_key("available_startups")
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return cached_data
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Optimized query with proper indexing
    cursor.execute('''
        SELECT id, name, business_description, requested_amount, credit_score, 
               interest_rate, loan_term_months, created_at
        FROM startups 
        WHERE funding_status = 'seeking'
        ORDER BY credit_score DESC, created_at DESC
        LIMIT 50
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
    
    data = {
        "status": "success",
        "available_startups": startups,
        "count": len(startups),
        "cached": False
    }
    
    set_cache_data(cache_key, data)
    return data

@app.post("/investor/register")
async def register_investor_optimized(investor: InvestorRegistration, background_tasks: BackgroundTasks):
    """Register investor with background cache invalidation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO investors (name, wallet_address, investment_capacity, risk_preference)
            VALUES (?, ?, ?, ?)
        ''', (investor.name, investor.wallet_address, investor.investment_capacity, investor.risk_preference))
        
        investor_id = cursor.lastrowid
        conn.commit()
        
        # Invalidate marketplace stats cache in background
        background_tasks.add_task(invalidate_stats_cache)
        
        return {
            "status": "success",
            "investor_id": investor_id,
            "message": f"Investor {investor.name} registered successfully",
            "wallet_address": investor.wallet_address,
            "performance": "optimized"
        }
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Wallet address already registered")
    
    finally:
        conn.close()

@app.post("/startup/register")
async def register_startup_optimized(startup: StartupRegistration, background_tasks: BackgroundTasks):
    """Register startup with AI scoring and cache invalidation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Enhanced AI scoring logic
        credit_score = calculate_enhanced_credit_score(startup.requested_amount, startup.business_description)
        interest_rate = calculate_dynamic_interest_rate(credit_score)
        
        cursor.execute('''
            INSERT INTO startups (name, wallet_address, business_description, requested_amount, 
                                loan_term_months, credit_score, interest_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (startup.name, startup.wallet_address, startup.business_description, 
              startup.requested_amount, startup.loan_term_months, credit_score, interest_rate))
        
        startup_id = cursor.lastrowid
        conn.commit()
        
        # Invalidate caches in background
        background_tasks.add_task(invalidate_startup_caches)
        
        return {
            "status": "success",
            "startup_id": startup_id,
            "message": f"Startup {startup.name} registered successfully",
            "credit_score": credit_score,
            "interest_rate": interest_rate,
            "requested_amount": startup.requested_amount,
            "ai_processing_time": "optimized"
        }
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Wallet address already registered")
    
    finally:
        conn.close()

def calculate_enhanced_credit_score(amount: int, description: str) -> int:
    """Enhanced AI credit scoring with performance optimization"""
    # Base score
    base_score = 650
    
    # Amount-based scoring (optimized logic)
    if amount <= 10000:
        amount_score = 100
    elif amount <= 30000:
        amount_score = 80
    elif amount <= 50000:
        amount_score = 60
    else:
        amount_score = 40
    
    # Description-based scoring (simple keyword analysis)
    positive_keywords = ['AI', 'blockchain', 'sustainable', 'innovative', 'scalable', 'proven']
    description_lower = description.lower()
    keyword_score = sum(10 for keyword in positive_keywords if keyword.lower() in description_lower)
    
    # Final score calculation
    final_score = min(850, base_score + amount_score + keyword_score)
    return final_score

def calculate_dynamic_interest_rate(credit_score: int) -> float:
    """Calculate dynamic interest rate based on credit score"""
    # Higher score = lower rate
    if credit_score >= 800:
        return 5.5
    elif credit_score >= 750:
        return 6.5
    elif credit_score >= 700:
        return 8.5
    elif credit_score >= 650:
        return 10.5
    else:
        return 12.0

async def invalidate_stats_cache():
    """Background task to invalidate stats cache"""
    cache_key = get_cache_key("marketplace_stats")
    if cache_key in cache:
        del cache[cache_key]

async def invalidate_startup_caches():
    """Background task to invalidate startup-related caches"""
    keys_to_remove = []
    for key in cache.keys():
        if 'startup' in key or 'marketplace_stats' in key:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del cache[key]

@app.get("/performance/cache-stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    total_entries = len(cache)
    cache_info = []
    
    for key, value in cache.items():
        age = time.time() - value['timestamp']
        cache_info.append({
            "key": key[:20] + "..." if len(key) > 20 else key,
            "age_seconds": round(age, 1),
            "expires_in": round(CACHE_TTL - age, 1)
        })
    
    return {
        "total_cache_entries": total_entries,
        "cache_ttl": CACHE_TTL,
        "cache_details": cache_info,
        "memory_usage": "optimized"
    }

@app.get("/performance/database-stats")
async def get_database_stats():
    """Get database performance statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get database size and performance info
    cursor.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]
    
    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    
    db_size_mb = (page_count * page_size) / (1024 * 1024)
    
    # Get table row counts
    cursor.execute("SELECT COUNT(*) FROM investors")
    investor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM startups")
    startup_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    transaction_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "database_size_mb": round(db_size_mb, 2),
        "total_records": investor_count + startup_count + transaction_count,
        "investors": investor_count,
        "startups": startup_count,
        "transactions": transaction_count,
        "performance_mode": "WAL + optimized"
    }

# Copy existing endpoints with performance enhancements
@app.post("/user/login")
async def user_login_optimized(login: UserLogin):
    """Optimized user login with caching"""
    cache_key = get_cache_key("user_login", f"{login.wallet_address}:{login.user_type}")
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        cached_data['cached'] = True
        return cached_data
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if login.user_type == "investor":
        cursor.execute("SELECT * FROM investors WHERE wallet_address = ?", (login.wallet_address,))
        user = cursor.fetchone()
        
        if user:
            data = {
                "status": "success",
                "user_type": "investor",
                "user_id": user[0],
                "name": user[1],
                "wallet_address": user[2],
                "current_balance": user[5],
                "total_invested": user[6],
                "yield_earned": user[7],
                "active_investments": user[8],
                "cached": False
            }
            set_cache_data(cache_key, data)
            conn.close()
            return data
    
    elif login.user_type == "startup":
        cursor.execute("SELECT * FROM startups WHERE wallet_address = ?", (login.wallet_address,))
        user = cursor.fetchone()
        
        if user:
            data = {
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
                "funded_amount": user[10],
                "cached": False
            }
            set_cache_data(cache_key, data)
            conn.close()
            return data
    
    conn.close()
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/investor/deposit")
async def investor_deposit_optimized(deposit: DepositRequest, background_tasks: BackgroundTasks):
    """Optimized investor deposit with background cache invalidation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use transaction for consistency
    cursor.execute('BEGIN TRANSACTION')
    
    try:
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
        
        cursor.execute('COMMIT')
        
        # Invalidate related caches in background
        background_tasks.add_task(invalidate_investor_caches, deposit.investor_id)
        
        return {
            "status": "success",
            "message": "Deposit successful",
            "amount": deposit.amount,
            "transaction_id": f"optimized_tx_{int(time.time())}",
            "performance": "enhanced"
        }
        
    except Exception as e:
        cursor.execute('ROLLBACK')
        raise HTTPException(status_code=500, detail=f"Deposit failed: {str(e)}")
    
    finally:
        conn.close()

async def invalidate_investor_caches(investor_id: int):
    """Background task to invalidate investor-related caches"""
    keys_to_remove = []
    for key in cache.keys():
        if f"investor_{investor_id}" in key or "marketplace_stats" in key:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del cache[key]

@app.get("/performance/benchmark")
async def run_performance_benchmark():
    """Run performance benchmark"""
    start_time = time.time()
    
    # Test database performance
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Run 100 quick queries
    for i in range(100):
        cursor.execute("SELECT COUNT(*) FROM investors")
        cursor.fetchone()
    
    db_time = time.time() - start_time
    conn.close()
    
    # Test cache performance
    start_time = time.time()
    for i in range(1000):
        cache_key = get_cache_key("test", str(i))
        set_cache_data(cache_key, {"test": i})
        get_cached_data(cache_key)
    
    cache_time = time.time() - start_time
    
    return {
        "database_performance": {
            "100_queries_time": f"{db_time:.3f}s",
            "queries_per_second": round(100 / db_time, 0)
        },
        "cache_performance": {
            "1000_operations_time": f"{cache_time:.3f}s",
            "operations_per_second": round(1000 / cache_time, 0)
        },
        "overall_status": "optimized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8002,  # Different port for optimized API
        log_level="info",
        access_log=False  # Disable access logs for performance
    )
