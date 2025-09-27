"""
Corporate Treasury - Unified API
24-Hour Sprint Complete Backend
Marketplace + Security APIs + RWA Integration
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
import json
import time
import hashlib
import random
import asyncio
from datetime import datetime, timedelta
from statistics import mean

app = FastAPI(
    title="Corporate Treasury - Unified API",
    description="Complete 24-Hour Sprint Backend - Marketplace + Security + RWA",
    version="2.0.0-unified"
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3003", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Cache system
cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 30

# Performance tracking
request_metrics = {
    "total_requests": 0,
    "response_times": [],
    "cache_hits": 0,
    "cache_misses": 0,
    "errors": 0,
    "start_time": time.time()
}

# Database setup
def init_unified_db():
    """Initialize complete database schema"""
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    # Core tables
    cursor.executescript('''
        -- Users table (unified)
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_address TEXT UNIQUE NOT NULL,
            user_type TEXT NOT NULL, -- investor, startup, developer
            name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Investors table
        CREATE TABLE IF NOT EXISTS investors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            investment_capacity INTEGER,
            risk_preference TEXT,
            current_balance INTEGER DEFAULT 0,
            total_invested INTEGER DEFAULT 0,
            yield_earned INTEGER DEFAULT 0,
            active_investments INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        -- Startups table
        CREATE TABLE IF NOT EXISTS startups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            business_description TEXT,
            requested_amount INTEGER,
            loan_term_months INTEGER DEFAULT 12,
            credit_score INTEGER DEFAULT 650,
            interest_rate REAL DEFAULT 8.5,
            funding_status TEXT DEFAULT 'seeking',
            investor_id INTEGER,
            funded_amount INTEGER DEFAULT 0,
            rwa_assets TEXT, -- JSON string for RWA assets
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (investor_id) REFERENCES investors (id)
        );
        
        -- RWA Assets table (Huma Finance benzeri)
        CREATE TABLE IF NOT EXISTS rwa_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            asset_type TEXT NOT NULL, -- invoice, receivable, equipment, inventory
            asset_value INTEGER,
            asset_metadata TEXT, -- JSON
            asa_token_id INTEGER,
            credit_limit INTEGER,
            status TEXT DEFAULT 'pending', -- pending, approved, funded, repaid
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES startups (id)
        );
        
        -- Transactions table
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            from_user_id INTEGER,
            to_user_id INTEGER,
            amount INTEGER,
            transaction_hash TEXT,
            rwa_asset_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users (id),
            FOREIGN KEY (to_user_id) REFERENCES users (id),
            FOREIGN KEY (rwa_asset_id) REFERENCES rwa_assets (id)
        );
        
        -- API Keys table (for developer API)
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            tier TEXT DEFAULT 'free', -- free, pro, enterprise
            calls_per_day INTEGER DEFAULT 1000,
            calls_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_users_wallet ON users(wallet_address);
        CREATE INDEX IF NOT EXISTS idx_startups_status ON startups(funding_status);
        CREATE INDEX IF NOT EXISTS idx_rwa_assets_company ON rwa_assets(company_id);
        CREATE INDEX IF NOT EXISTS idx_rwa_assets_type ON rwa_assets(asset_type);
        CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
        CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(api_key);
        
        -- Enable WAL mode for performance
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=NORMAL;
        PRAGMA cache_size=10000;
    ''')
    
    # Insert demo API keys
    cursor.execute('''
        INSERT OR IGNORE INTO api_keys (api_key, tier, calls_per_day)
        VALUES ('demo_key_123', 'free', 1000)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Unified database initialized")

# Initialize database
init_unified_db()

# Pydantic models
class UserRegistration(BaseModel):
    name: str
    wallet_address: str
    user_type: str  # investor, startup, developer
    email: Optional[str] = None

class InvestorProfile(BaseModel):
    investment_capacity: int
    risk_preference: str

class StartupProfile(BaseModel):
    business_description: str
    requested_amount: int
    loan_term_months: int = 12

class RWAAsset(BaseModel):
    asset_type: str  # invoice, receivable, equipment, inventory
    asset_value: int
    asset_metadata: Dict[str, Any]
    description: str

class DepositRequest(BaseModel):
    user_id: int
    amount: int

class FundingRequest(BaseModel):
    investor_id: int
    startup_id: int

# Web3 Security API Models
class TransactionAnalysisRequest(BaseModel):
    transaction_hash: str
    contract_address: str
    function_name: str
    parameters: Optional[List[Any]] = []
    value: Optional[int] = 0

class SecurityThreat(BaseModel):
    type: str  # reentrancy, overflow, phishing, etc.
    severity: str  # low, medium, high, critical
    description: str
    recommendation: str

class TransactionAnalysisResponse(BaseModel):
    risk_score: int  # 0-100
    security_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    threats: List[SecurityThreat]
    recommendations: List[str]
    analysis_time: str

class ContractAuditRequest(BaseModel):
    contract_address: str
    contract_source: Optional[str] = None
    audit_depth: str = "basic"  # basic, detailed, comprehensive

class SecurityMonitorRequest(BaseModel):
    contracts: List[str]

# Cache utilities
def get_cache_key(endpoint: str, params: str = "") -> str:
    return hashlib.md5(f"{endpoint}:{params}".encode()).hexdigest()

def get_cached_data(cache_key: str) -> Optional[Dict[str, Any]]:
    if cache_key in cache:
        cached_item = cache[cache_key]
        if time.time() - cached_item['timestamp'] < CACHE_TTL:
            return cached_item['data']
        else:
            del cache[cache_key]
    return None

def set_cache_data(cache_key: str, data: Dict[str, Any]) -> None:
    cache[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }

# Performance tracking middleware
@app.middleware("http")
async def track_performance(request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        end_time = time.time()
        
        request_metrics["total_requests"] += 1
        response_time = (end_time - start_time) * 1000
        request_metrics["response_times"].append(response_time)
        
        if len(request_metrics["response_times"]) > 100:
            request_metrics["response_times"] = request_metrics["response_times"][-100:]
        
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        return response
        
    except Exception as e:
        request_metrics["errors"] += 1
        raise e

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Corporate Treasury - Unified API",
        "version": "2.0.0-unified",
        "description": "Complete marketplace + security + RWA platform",
        "features": [
            "Corporate Treasury Marketplace",
            "Web3 Security APIs", 
            "RWA Credit Infrastructure",
            "Performance Monitoring"
        ],
        "endpoints": {
            "marketplace": "/api/marketplace/*",
            "security": "/api/security/*",
            "rwa": "/api/rwa/*",
            "monitoring": "/api/monitoring/*"
        },
        "status": "operational"
    }

# ==================== MARKETPLACE APIs ====================

@app.get("/api/marketplace/stats")
async def get_marketplace_stats():
    """Get marketplace statistics with caching"""
    cache_key = get_cache_key("marketplace_stats")
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return cached_data
    
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    # Get stats
    cursor.execute("SELECT COUNT(*) FROM investors")
    total_investors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM startups")
    total_startups = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(funded_amount), 0) FROM startups WHERE funding_status = 'funded'")
    total_funding = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM startups WHERE funding_status = 'seeking'")
    available_opportunities = cursor.fetchone()[0]
    
    conn.close()
    
    data = {
        "total_investors": total_investors,
        "total_startups": total_startups,
        "total_funding_volume": total_funding,
        "available_opportunities": available_opportunities,
        "platform_fee": "2%",
        "avg_interest_rate": "8.5%"
    }
    
    set_cache_data(cache_key, data)
    return data

@app.post("/api/marketplace/register")
async def register_user(user: UserRegistration):
    """Register new user (investor, startup, or developer)"""
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    try:
        # Insert user
        cursor.execute('''
            INSERT INTO users (wallet_address, user_type, name, email)
            VALUES (?, ?, ?, ?)
        ''', (user.wallet_address, user.user_type, user.name, user.email))
        
        user_id = cursor.lastrowid
        
        # Create type-specific profile
        if user.user_type == "investor":
            cursor.execute('''
                INSERT INTO investors (user_id)
                VALUES (?)
            ''', (user_id,))
        elif user.user_type == "startup":
            cursor.execute('''
                INSERT INTO startups (user_id)
                VALUES (?)
            ''', (user_id,))
        elif user.user_type == "developer":
            # Generate API key for developers
            api_key = f"dev_{hashlib.md5(user.wallet_address.encode()).hexdigest()[:16]}"
            cursor.execute('''
                INSERT INTO api_keys (api_key, user_id, tier)
                VALUES (?, ?, 'free')
            ''', (api_key, user_id))
        
        conn.commit()
        
        return {
            "status": "success",
            "user_id": user_id,
            "user_type": user.user_type,
            "message": f"User {user.name} registered successfully",
            "api_key": api_key if user.user_type == "developer" else None
        }
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Wallet address already registered")
    
    finally:
        conn.close()

@app.post("/api/marketplace/investor/deposit")
async def investor_deposit(deposit: DepositRequest):
    """Investor deposits ALGO"""
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    try:
        # Update investor balance
        cursor.execute('''
            UPDATE investors 
            SET current_balance = current_balance + ? 
            WHERE user_id = ?
        ''', (deposit.amount, deposit.user_id))
        
        # Record transaction
        cursor.execute('''
            INSERT INTO transactions (transaction_type, from_user_id, amount, status)
            VALUES ('deposit', ?, ?, 'completed')
        ''', (deposit.user_id, deposit.amount))
        
        conn.commit()
        
        return {
            "status": "success",
            "amount": deposit.amount,
            "message": "Deposit successful"
        }
    
    finally:
        conn.close()

@app.get("/api/marketplace/startups/available")
async def get_available_startups():
    """Get startups seeking funding"""
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.id, u.name, s.business_description, s.requested_amount, 
               s.credit_score, s.interest_rate, s.loan_term_months, s.created_at
        FROM startups s
        JOIN users u ON s.user_id = u.id
        WHERE s.funding_status = 'seeking'
        ORDER BY s.credit_score DESC
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
        "available_startups": startups,
        "count": len(startups)
    }

# ==================== SECURITY APIs ====================

@app.post("/api/security/trust-score")
async def get_trust_score(wallet_address: str):
    """Get AI-powered trust score"""
    
    # Simulate AI trust scoring
    wallet_hash = int(hashlib.md5(wallet_address.encode()).hexdigest()[:8], 16)
    base_score = 300 + (wallet_hash % 550)
    
    # On-chain analysis simulation
    on_chain_factors = {
        "wallet_age_days": wallet_hash % 1000,
        "transaction_count": wallet_hash % 10000,
        "avg_transaction_size": (wallet_hash % 100000) / 1000,
        "defi_interactions": wallet_hash % 50,
        "governance_participation": wallet_hash % 10
    }
    
    # Calculate final score
    final_score = min(850, base_score + (on_chain_factors["defi_interactions"] * 2))
    
    return {
        "wallet_address": wallet_address,
        "trust_score": final_score,
        "risk_level": "low" if final_score >= 750 else "medium" if final_score >= 650 else "high",
        "confidence": 0.95,
        "on_chain_analysis": on_chain_factors,
        "processing_time_ms": random.randint(10, 30),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/security/fraud-check")
async def check_fraud_risk(wallet_address: str):
    """Check fraud risk for wallet"""
    
    wallet_hash = int(hashlib.md5(wallet_address.encode()).hexdigest()[:8], 16)
    
    fraud_indicators = {
        "mixer_usage": wallet_hash % 10 == 0,
        "rapid_transactions": wallet_hash % 15 == 0,
        "suspicious_patterns": wallet_hash % 20 == 0,
        "blacklist_connections": wallet_hash % 50 == 0
    }
    
    fraud_score = sum([
        20 if fraud_indicators["mixer_usage"] else 0,
        15 if fraud_indicators["rapid_transactions"] else 0,
        25 if fraud_indicators["suspicious_patterns"] else 0,
        30 if fraud_indicators["blacklist_connections"] else 0
    ])
    
    return {
        "wallet_address": wallet_address,
        "fraud_score": min(100, fraud_score + (wallet_hash % 20)),
        "risk_level": "high" if fraud_score >= 50 else "medium" if fraud_score >= 25 else "low",
        "fraud_indicators": fraud_indicators,
        "recommendation": "block" if fraud_score >= 50 else "verify" if fraud_score >= 25 else "proceed",
        "processing_time_ms": random.randint(15, 40),
        "timestamp": datetime.now().isoformat()
    }

# ==================== RWA APIs (Huma Finance benzeri) ====================

@app.post("/api/rwa/asset/create")
async def create_rwa_asset(asset: RWAAsset, company_id: int):
    """Create RWA asset (Huma Finance benzeri)"""
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    try:
        # Calculate credit limit based on asset value
        credit_limit = int(asset.asset_value * 0.8)  # 80% LTV ratio
        
        # Generate mock ASA token ID
        asa_token_id = random.randint(100000000, 999999999)
        
        # Insert RWA asset
        cursor.execute('''
            INSERT INTO rwa_assets (company_id, asset_type, asset_value, asset_metadata, 
                                  asa_token_id, credit_limit, status)
            VALUES (?, ?, ?, ?, ?, ?, 'approved')
        ''', (company_id, asset.asset_type, asset.asset_value, 
              json.dumps(asset.asset_metadata), asa_token_id, credit_limit))
        
        asset_id = cursor.lastrowid
        conn.commit()
        
        return {
            "status": "success",
            "asset_id": asset_id,
            "asa_token_id": asa_token_id,
            "credit_limit": credit_limit,
            "ltv_ratio": "80%",
            "message": f"{asset.asset_type} tokenized successfully"
        }
    
    finally:
        conn.close()

@app.get("/api/rwa/assets/{company_id}")
async def get_company_rwa_assets(company_id: int):
    """Get company's RWA assets"""
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, asset_type, asset_value, asa_token_id, credit_limit, status, created_at
        FROM rwa_assets
        WHERE company_id = ?
        ORDER BY created_at DESC
    ''', (company_id,))
    
    assets = []
    for row in cursor.fetchall():
        assets.append({
            "id": row[0],
            "asset_type": row[1],
            "asset_value": row[2],
            "asa_token_id": row[3],
            "credit_limit": row[4],
            "status": row[5],
            "created_at": row[6]
        })
    
    conn.close()
    
    total_credit_limit = sum([asset["credit_limit"] for asset in assets])
    
    return {
        "assets": assets,
        "total_assets": len(assets),
        "total_credit_limit": total_credit_limit,
        "company_id": company_id
    }

@app.post("/api/rwa/credit/draw")
async def draw_rwa_credit(company_id: int, amount: int, asset_id: int):
    """Draw credit against RWA asset"""
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    try:
        # Check asset and credit limit
        cursor.execute('''
            SELECT credit_limit, status FROM rwa_assets WHERE id = ? AND company_id = ?
        ''', (asset_id, company_id))
        
        asset_data = cursor.fetchone()
        if not asset_data:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        credit_limit, status = asset_data
        
        if status != "approved":
            raise HTTPException(status_code=400, detail="Asset not approved for credit")
        
        if amount > credit_limit:
            raise HTTPException(status_code=400, detail="Amount exceeds credit limit")
        
        # Record credit transaction
        cursor.execute('''
            INSERT INTO transactions (transaction_type, to_user_id, amount, rwa_asset_id, status)
            VALUES ('rwa_credit', ?, ?, ?, 'completed')
        ''', (company_id, amount, asset_id))
        
        # Update asset status
        cursor.execute('''
            UPDATE rwa_assets SET status = 'funded' WHERE id = ?
        ''', (asset_id,))
        
        conn.commit()
        
        return {
            "status": "success",
            "amount": amount,
            "asset_id": asset_id,
            "transaction_type": "rwa_credit",
            "message": "RWA credit drawn successfully"
        }
    
    finally:
        conn.close()

# ==================== MONITORING APIs ====================

@app.get("/api/monitoring/health")
async def get_system_health():
    """System health check"""
    try:
        conn = sqlite3.connect('corporate_treasury.db')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        db_status = "healthy"
    except:
        db_status = "error"
    
    return {
        "overall_status": "healthy" if db_status == "healthy" else "degraded",
        "components": {
            "database": db_status,
            "api": "healthy",
            "cache": "healthy"
        },
        "uptime": time.time() - request_metrics["start_time"],
        "total_requests": request_metrics["total_requests"],
        "error_rate": (request_metrics["errors"] / max(1, request_metrics["total_requests"])) * 100
    }

@app.get("/api/monitoring/metrics")
async def get_metrics():
    """Get performance metrics"""
    uptime = time.time() - request_metrics["start_time"]
    response_times = request_metrics["response_times"]
    avg_response_time = mean(response_times) if response_times else 0
    
    return {
        "uptime_seconds": round(uptime, 1),
        "total_requests": request_metrics["total_requests"],
        "requests_per_second": round(request_metrics["total_requests"] / uptime, 2) if uptime > 0 else 0,
        "average_response_time": round(avg_response_time, 2),
        "cache_entries": len(cache),
        "error_count": request_metrics["errors"]
    }

# ==================== WEB3 SECURITY APIs ====================

# API Key validation
def validate_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Validate API key for security endpoints"""
    api_key = credentials.credentials
    
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tier, calls_per_day, calls_used FROM api_keys 
        WHERE api_key = ?
    ''', (api_key,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    tier, calls_per_day, calls_used = result
    
    if calls_used >= calls_per_day:
        raise HTTPException(status_code=429, detail="API rate limit exceeded")
    
    return api_key

def analyze_transaction_security(request: TransactionAnalysisRequest) -> TransactionAnalysisResponse:
    """Analyze transaction for security threats"""
    threats = []
    recommendations = []
    
    # Simulated security analysis
    risk_score = random.randint(0, 100)
    
    # Check for common threats based on function name
    if "transfer" in request.function_name.lower():
        if request.value and request.value > 1000000:  # Large transfer
            threats.append(SecurityThreat(
                type="high_value_transfer",
                severity="medium",
                description="Large value transfer detected",
                recommendation="Verify recipient address and amount"
            ))
            risk_score += 20
    
    if "approve" in request.function_name.lower():
        threats.append(SecurityThreat(
            type="unlimited_approval",
            severity="high",
            description="Unlimited token approval detected",
            recommendation="Consider using limited approval amounts"
        ))
        risk_score += 30
    
    # Contract address analysis
    if len(request.contract_address) != 58:  # Invalid Algorand address
        threats.append(SecurityThreat(
            type="invalid_address",
            severity="critical",
            description="Invalid contract address format",
            recommendation="Verify contract address before proceeding"
        ))
        risk_score += 50
    
    # Determine security level
    if risk_score >= 80:
        security_level = "CRITICAL"
    elif risk_score >= 60:
        security_level = "HIGH"
    elif risk_score >= 30:
        security_level = "MEDIUM"
    else:
        security_level = "LOW"
    
    # Generate recommendations
    if threats:
        recommendations.append("Review all detected threats before proceeding")
        recommendations.append("Consider using a multi-signature wallet for high-value transactions")
    else:
        recommendations.append("Transaction appears safe to proceed")
    
    return TransactionAnalysisResponse(
        risk_score=min(risk_score, 100),
        security_level=security_level,
        threats=threats,
        recommendations=recommendations,
        analysis_time=datetime.now().isoformat()
    )

@app.post("/api/web3-security/analyze", response_model=TransactionAnalysisResponse)
async def analyze_transaction(
    request: TransactionAnalysisRequest,
    api_key: str = Depends(validate_api_key)
):
    """Analyze transaction for security threats"""
    try:
        # Update API usage
        conn = sqlite3.connect('corporate_treasury.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE api_keys SET calls_used = calls_used + 1 
            WHERE api_key = ?
        ''', (api_key,))
        conn.commit()
        conn.close()
        
        # Perform analysis
        analysis = analyze_transaction_security(request)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/web3-security/audit-contract")
async def audit_contract(
    request: ContractAuditRequest,
    api_key: str = Depends(validate_api_key)
):
    """Audit smart contract for security issues"""
    try:
        # Update API usage
        conn = sqlite3.connect('corporate_treasury.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE api_keys SET calls_used = calls_used + 1 
            WHERE api_key = ?
        ''', (api_key,))
        conn.commit()
        conn.close()
        
        # Simulated contract audit
        vulnerabilities = []
        
        if request.audit_depth == "comprehensive":
            vulnerabilities.extend([
                {
                    "type": "reentrancy",
                    "severity": "medium",
                    "line": 45,
                    "description": "Potential reentrancy vulnerability in transfer function"
                },
                {
                    "type": "access_control",
                    "severity": "low",
                    "line": 23,
                    "description": "Missing access control on admin function"
                }
            ])
        
        return {
            "contract_address": request.contract_address,
            "audit_depth": request.audit_depth,
            "overall_score": random.randint(70, 95),
            "vulnerabilities": vulnerabilities,
            "recommendations": [
                "Implement reentrancy guards",
                "Add proper access controls",
                "Use latest compiler version"
            ],
            "audit_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")

@app.post("/api/web3-security/monitor")
async def start_monitoring(
    request: SecurityMonitorRequest,
    api_key: str = Depends(validate_api_key)
):
    """Start real-time security monitoring for contracts"""
    try:
        # Update API usage
        conn = sqlite3.connect('corporate_treasury.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE api_keys SET calls_used = calls_used + 1 
            WHERE api_key = ?
        ''', (api_key,))
        conn.commit()
        conn.close()
        
        return {
            "status": "monitoring_started",
            "contracts": request.contracts,
            "monitor_id": f"monitor_{random.randint(1000, 9999)}",
            "websocket_url": f"ws://localhost:8000/ws/security-monitor?api_key={api_key}",
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")

# WebSocket endpoint for real-time monitoring
@app.websocket("/ws/security-monitor")
async def websocket_security_monitor(websocket: WebSocket, api_key: str):
    """WebSocket endpoint for real-time security monitoring"""
    # Validate API key
    conn = sqlite3.connect('corporate_treasury.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tier FROM api_keys WHERE api_key = ?', (api_key,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        await websocket.close(code=1008, reason="Invalid API key")
        return
    
    await websocket.accept()
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "message": "Security monitoring active",
            "timestamp": datetime.now().isoformat()
        })
        
        # Simulate real-time security alerts
        while True:
            await asyncio.sleep(10)  # Send alert every 10 seconds
            
            alert = {
                "type": "security_alert",
                "threat_type": random.choice(["suspicious_transaction", "contract_interaction", "high_value_transfer"]),
                "severity": random.choice(["low", "medium", "high"]),
                "contract_address": "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFG",
                "description": "Suspicious activity detected",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_json(alert)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Generate API key endpoint
@app.post("/api/web3-security/generate-key")
async def generate_api_key(user_email: str = "demo@example.com"):
    """Generate new API key"""
    try:
        new_key = f"ak_{hashlib.md5(f'{user_email}_{time.time()}'.encode()).hexdigest()}"
        
        conn = sqlite3.connect('corporate_treasury.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_keys (api_key, tier, calls_per_day, calls_used)
            VALUES (?, 'free', 1000, 0)
        ''', (new_key,))
        
        conn.commit()
        conn.close()
        
        return {
            "api_key": new_key,
            "tier": "free",
            "calls_per_day": 1000,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key generation failed: {str(e)}")

# Health check for frontend
@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Corporate Treasury Unified API...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,  # Standard port
        log_level="info"
    )
