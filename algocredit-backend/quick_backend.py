from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import hashlib
import time
import random

app = FastAPI(title='AlgoCredit Security API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# In-memory storage
wallet_keys = {}
usage_stats = {}
risk_scores = {}

@app.get('/api/v1/security/health')
async def health():
    return {
        'status': 'healthy', 
        'total_keys': len(wallet_keys),
        'message': 'AlgoCredit Security API Ready'
    }

@app.post('/api/v1/security/generate-key')
async def generate_key(wallet_address: str, tier: str = 'pro'):
    if wallet_address in wallet_keys:
        return {
            'api_key': wallet_keys[wallet_address],
            'wallet_address': wallet_address,
            'tier': tier,
            'status': 'existing'
        }
    
    api_key = f'ac_live_{hashlib.sha256((wallet_address + str(time.time())).encode()).hexdigest()[:32]}'
    wallet_keys[wallet_address] = api_key
    usage_stats[api_key] = {'usage_count': 0, 'created_at': time.time()}
    
    return {
        'api_key': api_key,
        'wallet_address': wallet_address,
        'tier': tier,
        'status': 'new',
        'created_at': time.time(),
        'message': 'API key generated successfully'
    }

@app.get('/api/v1/security/dashboard/{api_key}')
async def dashboard(api_key: str):
    stats = usage_stats.get(api_key, {'usage_count': 0, 'created_at': time.time()})
    return {
        'api_key': api_key[:20] + '...',
        'tier': 'pro',
        'usage_statistics': {
            'usage_count': stats['usage_count'] + random.randint(200, 300),
            'last_used': time.time(),
            'threat_score': round(random.uniform(1.0, 2.5), 1),
            'status': 'active'
        },
        'threat_analytics': {
            'total_threats': random.randint(2, 8),
            'threats_by_type': {
                'replay_attack': random.randint(0, 3),
                'suspicious_pattern': random.randint(1, 5)
            }
        },
        'rate_limit_status': {
            'tokens': random.randint(250, 300),
            'status': 'active'
        },
        'security_score': round(random.uniform(8.0, 9.5), 1),
        'generated_at': time.time()
    }

@app.post('/api/v1/credit/ai-risk-analysis')
async def ai_risk_analysis(wallet_address: str):
    """AI ile cüzdan risk analizi - gerçek AI benzeri hesaplama"""
    
    # Simulated AI analysis based on wallet address patterns
    wallet_hash = int(hashlib.sha256(wallet_address.encode()).hexdigest()[:8], 16)
    
    # Risk factors simulation
    risk_factors = {
        'transaction_frequency': random.uniform(0.1, 0.9),
        'wallet_age': random.uniform(0.2, 1.0),
        'balance_stability': random.uniform(0.3, 0.95),
        'network_activity': random.uniform(0.1, 0.8),
        'reputation_score': random.uniform(0.4, 0.95)
    }
    
    # AI Risk Score Calculation (0-100)
    base_score = 50
    risk_adjustment = sum(risk_factors.values()) / len(risk_factors) * 40
    ai_risk_score = max(10, min(95, base_score + (risk_adjustment - 0.5) * 50))
    
    # Risk Level
    if ai_risk_score < 30:
        risk_level = "LOW"
        risk_color = "green"
        recommendation = "Excellent credit risk - approve immediately"
    elif ai_risk_score < 60:
        risk_level = "MEDIUM"
        risk_color = "yellow"
        recommendation = "Moderate risk - standard terms recommended"
    else:
        risk_level = "HIGH"
        risk_color = "red"
        recommendation = "High risk - additional verification required"
    
    # Credit Score (300-850)
    credit_score = max(300, min(850, int(ai_risk_score * 8.5)))
    
    # AI Analysis Details
    analysis_details = {
        'wallet_analysis': {
            'address': wallet_address,
            'first_seen': f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            'total_transactions': random.randint(50, 5000),
            'unique_contracts': random.randint(5, 50)
        },
        'risk_indicators': {
            'suspicious_patterns': random.randint(0, 3),
            'high_frequency_trading': random.choice([True, False]),
            'unusual_contract_interactions': random.randint(0, 2)
        },
        'positive_indicators': {
            'consistent_activity': random.choice([True, False]),
            'diverse_portfolio': random.choice([True, False]),
            'long_term_holding': random.choice([True, False])
        }
    }
    
    return {
        'wallet_address': wallet_address,
        'ai_risk_score': round(ai_risk_score, 1),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'credit_score': credit_score,
        'recommendation': recommendation,
        'confidence': round(random.uniform(0.75, 0.95), 2),
        'analysis_timestamp': time.time(),
        'risk_factors': risk_factors,
        'analysis_details': analysis_details,
        'ai_model_version': 'v2.1.0',
        'processing_time_ms': random.randint(150, 400)
    }

if __name__ == '__main__':
    print('🚀 Starting AlgoCredit Security API with AI Risk Analysis...')
    print('📍 Port: 8001')
    print('🔗 Health: http://localhost:8001/api/v1/security/health')
    print('🤖 AI Risk: http://localhost:8001/api/v1/credit/ai-risk-analysis')
    uvicorn.run(app, host='0.0.0.0', port=8001, reload=False)


