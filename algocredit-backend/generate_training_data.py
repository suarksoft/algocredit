"""
Synthetic Training Data Generation for AlgoCredit AI Model
Generates realistic Algorand wallet data for credit scoring model training
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import List, Dict
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

class WalletDataGenerator:
    """Generate synthetic Algorand wallet data for training"""
    
    def __init__(self):
        self.risk_profiles = {
            'low_risk': {
                'credit_score_range': (750, 850),
                'age_range': (365, 1825),  # 1-5 years
                'transaction_range': (100, 500),
                'balance_range': (10000, 100000),  # microALGOs
                'stability_range': (0.8, 1.0)
            },
            'medium_risk': {
                'credit_score_range': (600, 750),
                'age_range': (90, 730),  # 3 months - 2 years
                'transaction_range': (20, 200),
                'balance_range': (1000, 50000),
                'stability_range': (0.5, 0.8)
            },
            'high_risk': {
                'credit_score_range': (300, 600),
                'age_range': (1, 180),  # New to 6 months
                'transaction_range': (1, 50),
                'balance_range': (0, 10000),
                'stability_range': (0.0, 0.6)
            }
        }
    
    def generate_wallet_profile(self, risk_category: str) -> Dict:
        """Generate a single wallet profile"""
        profile = self.risk_profiles[risk_category]
        
        # Base metrics
        account_age_days = np.random.randint(*profile['age_range'])
        total_transactions = np.random.randint(*profile['transaction_range'])
        current_balance = np.random.randint(*profile['balance_range'])
        
        # Derived metrics
        avg_transaction_size = current_balance / max(total_transactions, 1) if total_transactions > 0 else 0
        transaction_frequency = total_transactions / max(account_age_days / 30, 1)  # per month
        
        # Calculate scores (0-100)
        balance_stability_score = np.random.uniform(*profile['stability_range']) * 100
        
        # Transaction frequency score (normalized)
        frequency_score = min(100, transaction_frequency * 10)
        
        # Asset diversity (0-10 different assets)
        num_assets = np.random.poisson(
            lam=3 if risk_category == 'low_risk' 
            else 2 if risk_category == 'medium_risk' 
            else 1
        )
        asset_diversity_score = min(100, num_assets * 20)
        
        # DApp usage
        dapp_interactions = np.random.poisson(
            lam=5 if risk_category == 'low_risk'
            else 2 if risk_category == 'medium_risk'
            else 0.5
        )
        dapp_usage_score = min(100, dapp_interactions * 15)
        
        # Target credit score
        credit_score = np.random.randint(*profile['credit_score_range'])
        
        # Add some noise for realism
        credit_score += np.random.randint(-10, 11)
        credit_score = max(300, min(850, credit_score))
        
        return {
            'wallet_address': f"SYNTH_{risk_category.upper()}_{np.random.randint(10000, 99999)}",
            'account_age_days': account_age_days,
            'total_transactions': total_transactions,
            'total_volume': current_balance * np.random.uniform(2, 10),  # Historical volume
            'current_balance': current_balance,
            'average_balance': current_balance * np.random.uniform(0.7, 1.3),
            'balance_stability_score': balance_stability_score,
            'transaction_frequency_score': frequency_score,
            'asset_diversity_score': asset_diversity_score,
            'dapp_usage_score': dapp_usage_score,
            'unique_counterparties': min(total_transactions, np.random.randint(1, 50)),
            'avg_transaction_size': avg_transaction_size,
            'risk_category': risk_category,
            'credit_score': credit_score  # Target variable
        }
    
    def generate_dataset(self, 
                        total_samples: int = 1000,
                        risk_distribution: Dict[str, float] = None) -> pd.DataFrame:
        """Generate complete dataset"""
        
        if risk_distribution is None:
            risk_distribution = {
                'low_risk': 0.3,
                'medium_risk': 0.5,
                'high_risk': 0.2
            }
        
        data = []
        
        for risk_category, proportion in risk_distribution.items():
            num_samples = int(total_samples * proportion)
            print(f"Generating {num_samples} {risk_category} profiles...")
            
            for _ in range(num_samples):
                wallet_profile = self.generate_wallet_profile(risk_category)
                data.append(wallet_profile)
        
        df = pd.DataFrame(data)
        
        # Add some correlation adjustments for realism
        self._add_realistic_correlations(df)
        
        return df
    
    def _add_realistic_correlations(self, df: pd.DataFrame):
        """Add realistic correlations between variables"""
        
        # Older accounts tend to have more transactions
        age_bonus = (df['account_age_days'] / 365) * 20
        df['total_transactions'] = df['total_transactions'] + age_bonus.astype(int)
        
        # Higher balance -> higher stability (with noise)
        balance_factor = np.log(df['current_balance'] + 1) / 10
        df['balance_stability_score'] = np.clip(
            df['balance_stability_score'] + balance_factor + np.random.normal(0, 5, len(df)),
            0, 100
        )
        
        # More transactions -> higher frequency score
        freq_adjustment = np.log(df['total_transactions'] + 1) * 5
        df['transaction_frequency_score'] = np.clip(
            df['transaction_frequency_score'] + freq_adjustment,
            0, 100
        )
        
        # Ensure credit scores make sense with other metrics
        composite_score = (
            df['balance_stability_score'] * 0.3 +
            df['transaction_frequency_score'] * 0.2 +
            df['asset_diversity_score'] * 0.2 +
            df['dapp_usage_score'] * 0.3
        )
        
        # Adjust credit scores based on composite score
        adjustment = (composite_score - 50) * 2  # -100 to +100 adjustment
        df['credit_score'] = np.clip(
            df['credit_score'] + adjustment + np.random.normal(0, 20, len(df)),
            300, 850
        ).astype(int)

def generate_and_save_data():
    """Generate training data and save to files"""
    print("🤖 Generating synthetic training data for AlgoCredit AI model...")
    
    generator = WalletDataGenerator()
    
    # Generate training dataset
    print("📊 Creating training dataset...")
    train_df = generator.generate_dataset(total_samples=2000)
    
    # Generate test dataset
    print("📊 Creating test dataset...")
    test_df = generator.generate_dataset(total_samples=500)
    
    # Save datasets
    train_df.to_csv('algocredit-backend/data/training_data.csv', index=False)
    test_df.to_csv('algocredit-backend/data/test_data.csv', index=False)
    
    # Save as JSON for API testing
    train_sample = train_df.sample(10).to_dict('records')
    with open('algocredit-backend/data/sample_wallets.json', 'w') as f:
        json.dump(train_sample, f, indent=2)
    
    # Dataset statistics
    print("\n✅ Dataset Generated Successfully!")
    print(f"📈 Training samples: {len(train_df)}")
    print(f"📈 Test samples: {len(test_df)}")
    
    print("\n📊 Credit Score Distribution:")
    score_dist = train_df['credit_score'].describe()
    print(f"   Mean: {score_dist['mean']:.0f}")
    print(f"   Min: {score_dist['min']:.0f}")
    print(f"   Max: {score_dist['max']:.0f}")
    print(f"   Std: {score_dist['std']:.0f}")
    
    print("\n🎯 Risk Category Distribution:")
    risk_dist = train_df['risk_category'].value_counts()
    for category, count in risk_dist.items():
        print(f"   {category}: {count} ({count/len(train_df)*100:.1f}%)")
    
    print("\n🔗 Sample Data Preview:")
    print(train_df.head(3)[['wallet_address', 'account_age_days', 'total_transactions', 'credit_score']].to_string())
    
    return train_df, test_df

if __name__ == "__main__":
    # Create data directory
    import os
    os.makedirs('algocredit-backend/data', exist_ok=True)
    
    # Generate data
    train_df, test_df = generate_and_save_data()