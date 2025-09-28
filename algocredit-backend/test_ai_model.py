"""
Simple AI model test script
"""
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from train_model import AlgoCreditAI
    print('✅ AI model import successful')
    
    ai = AlgoCreditAI()
    ai.load_model()
    print('✅ AI model loading successful')
    
    # Test prediction with sample wallet
    sample_wallet = {
        'account_age_days': 500,
        'total_transactions': 150,
        'total_volume': 75000000000,  # 75k ALGO in microAlgos
        'current_balance': 15000000000,  # 15k ALGO
        'average_balance': 12000000000,
        'balance_stability_score': 85.0,
        'transaction_frequency_score': 75.0,
        'asset_diversity_score': 60.0,
        'dapp_usage_score': 80.0,
        'unique_counterparties': 35,
        'avg_transaction_size': 500000000
    }
    
    print('\n🧪 Testing AI Credit Scoring...')
    print('Sample Wallet Profile:')
    print(f'  - Account Age: {sample_wallet["account_age_days"]} days')
    print(f'  - Transactions: {sample_wallet["total_transactions"]}')
    print(f'  - Balance: {sample_wallet["current_balance"] / 1_000_000:.2f} ALGO')
    print(f'  - Stability Score: {sample_wallet["balance_stability_score"]}%')
    
    result = ai.predict_credit_score(sample_wallet)
    
    print('\n🎯 AI Prediction Results:')
    print(f'  - Credit Score: {result["credit_score"]}')
    print(f'  - Risk Level: {result["risk_level"]}')
    print(f'  - Confidence: {result["confidence"]}%')
    print(f'  - Insights: {result["insights"]}')
    
    # Test different risk profiles
    print('\n📊 Testing Different Risk Profiles:')
    
    # Low risk profile
    low_risk_wallet = {
        'account_age_days': 1000,
        'total_transactions': 500,
        'total_volume': 200000000000,
        'current_balance': 50000000000,
        'average_balance': 45000000000,
        'balance_stability_score': 95.0,
        'transaction_frequency_score': 90.0,
        'asset_diversity_score': 85.0,
        'dapp_usage_score': 75.0,
        'unique_counterparties': 80,
        'avg_transaction_size': 400000000
    }
    
    low_risk_result = ai.predict_credit_score(low_risk_wallet)
    print(f'Low Risk Wallet: Score {low_risk_result["credit_score"]}, Risk: {low_risk_result["risk_level"]}')
    
    # High risk profile
    high_risk_wallet = {
        'account_age_days': 30,
        'total_transactions': 5,
        'total_volume': 1000000000,
        'current_balance': 500000000,
        'average_balance': 400000000,
        'balance_stability_score': 25.0,
        'transaction_frequency_score': 15.0,
        'asset_diversity_score': 10.0,
        'dapp_usage_score': 5.0,
        'unique_counterparties': 3,
        'avg_transaction_size': 200000000
    }
    
    high_risk_result = ai.predict_credit_score(high_risk_wallet)
    print(f'High Risk Wallet: Score {high_risk_result["credit_score"]}, Risk: {high_risk_result["risk_level"]}')
    
    print('\n✅ AI Model Test Completed Successfully!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()