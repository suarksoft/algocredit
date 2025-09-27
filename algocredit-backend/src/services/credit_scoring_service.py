"""
AI Credit Scoring Service for AlgoCredit
Combines on-chain and off-chain data to generate credit scores
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime
import json

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from .algorand_service import algorand_service


class CreditScoringService:
    """AI-powered credit scoring service"""
    
    def __init__(self):
        """Initialize the credit scoring service"""
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        # Model weights for different components
        self.weights = {
            "on_chain": 0.6,      # 60% weight for blockchain data
            "off_chain": 0.4      # 40% weight for business data
        }
        
        # Initialize with dummy training data
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize model with synthetic training data for MVP"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [account_age, transaction_count, balance, volume, assets, apps, business_score]
        X = np.random.rand(n_samples, 7)
        
        # Normalize features to realistic ranges
        X[:, 0] = X[:, 0] * 365 + 30        # account_age_days: 30-395
        X[:, 1] = X[:, 1] * 1000 + 10       # transaction_count: 10-1010
        X[:, 2] = X[:, 2] * 1000000 + 100000 # balance: 100K-1.1M microAlgos
        X[:, 3] = X[:, 3] * 10000000        # volume: 0-10M microAlgos
        X[:, 4] = X[:, 4] * 10               # unique_assets: 0-10
        X[:, 5] = X[:, 5] * 5                # app_interactions: 0-5
        X[:, 6] = X[:, 6] * 100              # business_score: 0-100
        
        # Generate target scores (300-850 range)
        # Higher values in features should correlate with higher scores
        y = (
            (X[:, 0] / 365) * 100 +          # Account age contribution
            (X[:, 1] / 1000) * 150 +         # Transaction count contribution
            (X[:, 2] / 1000000) * 100 +      # Balance contribution
            (X[:, 3] / 10000000) * 100 +     # Volume contribution
            (X[:, 4] / 10) * 50 +            # Assets contribution
            (X[:, 5] / 5) * 50 +             # Apps contribution
            (X[:, 6] / 100) * 200 +          # Business contribution
            np.random.normal(0, 50, n_samples)  # Add some noise
        )
        
        # Normalize to 300-850 range
        y = np.clip(300 + (y / np.max(y)) * 550, 300, 850)
        
        # Train the model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        print("✅ Credit scoring model initialized with synthetic data")
    
    async def analyze_credit_score(self, wallet_address: str, business_data: Optional[Dict] = None) -> Dict:
        """
        Generate comprehensive credit score analysis
        
        Args:
            wallet_address: Algorand wallet address
            business_data: Optional business metrics data
            
        Returns:
            Dictionary containing credit score and analysis
        """
        try:
            # Get on-chain analysis
            on_chain_data = await algorand_service.analyze_wallet_behavior(wallet_address)
            
            # Calculate on-chain score
            on_chain_score = self._calculate_on_chain_score(on_chain_data)
            
            # Calculate off-chain score
            off_chain_score = self._calculate_off_chain_score(business_data or {})
            
            # Combine scores
            combined_score = (
                on_chain_score * self.weights["on_chain"] + 
                off_chain_score * self.weights["off_chain"]
            )
            
            # Use ML model for final prediction
            features = self._prepare_features(on_chain_data, business_data or {})
            ml_score = self._predict_with_model(features)
            
            # Final score is weighted average of rule-based and ML scores
            final_score = int((combined_score * 0.7) + (ml_score * 0.3))
            final_score = max(300, min(850, final_score))  # Ensure valid range
            
            # Determine risk level
            risk_level = self._determine_risk_level(final_score)
            
            # Calculate loan parameters
            max_loan_amount, interest_rate = self._calculate_loan_parameters(final_score, on_chain_data)
            
            return {
                "wallet_address": wallet_address,
                "credit_score": final_score,
                "on_chain_score": round(on_chain_score, 2),
                "off_chain_score": round(off_chain_score, 2),
                "risk_level": risk_level,
                "max_loan_amount": max_loan_amount,
                "recommended_interest_rate": round(interest_rate, 2),
                "score_breakdown": {
                    "account_age_contribution": self._score_account_age(on_chain_data.get("account_age_days", 1)),
                    "transaction_activity": self._score_transaction_activity(on_chain_data),
                    "balance_stability": on_chain_data.get("balance_stability_score", 0),
                    "asset_diversity": on_chain_data.get("asset_diversity_score", 0),
                    "dapp_usage": on_chain_data.get("dapp_usage_score", 0),
                    "business_metrics": off_chain_score
                },
                "analysis_timestamp": datetime.now().isoformat(),
                "model_version": "1.0.0"
            }
            
        except Exception as e:
            print(f"Error analyzing credit score: {e}")
            return self._default_credit_analysis(wallet_address)
    
    def _calculate_on_chain_score(self, wallet_data: Dict) -> float:
        """Calculate on-chain credit score component"""
        scores = []
        
        # Account age score (0-100)
        age_score = self._score_account_age(wallet_data.get("account_age_days", 1))
        scores.append(age_score * 0.25)  # 25% weight
        
        # Transaction activity score (0-100)
        activity_score = self._score_transaction_activity(wallet_data)
        scores.append(activity_score * 0.25)  # 25% weight
        
        # Balance stability (0-100)
        stability_score = wallet_data.get("balance_stability_score", 0)
        scores.append(stability_score * 0.2)  # 20% weight
        
        # Asset diversity (0-100)
        diversity_score = wallet_data.get("asset_diversity_score", 0)
        scores.append(diversity_score * 0.15)  # 15% weight
        
        # DApp usage (0-100)
        dapp_score = wallet_data.get("dapp_usage_score", 0)
        scores.append(dapp_score * 0.15)  # 15% weight
        
        total_score = sum(scores)
        
        # Convert to 300-850 scale (on-chain portion)
        return 300 + (total_score / 100) * 350
    
    def _calculate_off_chain_score(self, business_data: Dict) -> float:
        """Calculate off-chain credit score component"""
        if not business_data:
            return 500  # Neutral score for missing data
        
        scores = []
        
        # Startup age
        startup_age_months = business_data.get("startup_age_months", 0)
        age_score = min(100, (startup_age_months / 24) * 100)  # 2 years = 100 points
        scores.append(age_score * 0.2)
        
        # Team experience
        team_experience = business_data.get("team_experience_years", 0)
        exp_score = min(100, (team_experience / 10) * 100)  # 10 years = 100 points
        scores.append(exp_score * 0.25)
        
        # Revenue traction
        monthly_revenue = business_data.get("monthly_revenue", 0)
        revenue_score = min(100, (monthly_revenue / 50000) * 100)  # $50K = 100 points
        scores.append(revenue_score * 0.25)
        
        # User growth
        user_growth_rate = business_data.get("user_growth_rate", 0)
        growth_score = min(100, user_growth_rate * 10)  # 10% growth = 100 points
        scores.append(growth_score * 0.15)
        
        # Market size
        market_size = business_data.get("market_size_score", 50)  # Default neutral
        scores.append(market_size * 0.15)
        
        total_score = sum(scores)
        
        # Convert to 300-850 scale (off-chain portion)
        return 300 + (total_score / 100) * 350
    
    def _score_account_age(self, age_days: int) -> float:
        """Score account age (newer accounts have lower scores)"""
        if age_days < 30:
            return 20
        elif age_days < 90:
            return 40
        elif age_days < 180:
            return 60
        elif age_days < 365:
            return 80
        else:
            return 100
    
    def _score_transaction_activity(self, wallet_data: Dict) -> float:
        """Score transaction activity"""
        tx_count = wallet_data.get("total_transactions", 0)
        volume = wallet_data.get("total_volume", 0)
        
        # Count score (0-50)
        count_score = min(50, (tx_count / 100) * 50)
        
        # Volume score (0-50)
        volume_score = min(50, (volume / 10000000) * 50)  # 10 ALGO = 50 points
        
        return count_score + volume_score
    
    def _prepare_features(self, on_chain_data: Dict, business_data: Dict) -> np.ndarray:
        """Prepare features for ML model"""
        features = [
            on_chain_data.get("account_age_days", 1),
            on_chain_data.get("total_transactions", 0),
            on_chain_data.get("current_balance", 0),
            on_chain_data.get("total_volume", 0),
            len(on_chain_data.get("unique_counterparties", [])) if isinstance(on_chain_data.get("unique_counterparties"), list) else on_chain_data.get("unique_counterparties", 0),
            on_chain_data.get("dapp_usage_score", 0) / 10,  # Normalize
            self._calculate_off_chain_score(business_data) / 10  # Normalize
        ]
        
        return np.array(features).reshape(1, -1)
    
    def _predict_with_model(self, features: np.ndarray) -> float:
        """Predict credit score using ML model"""
        try:
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            return max(300, min(850, prediction))
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return 650  # Default score
    
    def _determine_risk_level(self, score: int) -> str:
        """Determine risk level based on credit score"""
        if score >= 750:
            return "low"
        elif score >= 650:
            return "medium"
        elif score >= 550:
            return "high"
        else:
            return "very_high"
    
    def _calculate_loan_parameters(self, credit_score: int, wallet_data: Dict) -> Tuple[int, float]:
        """Calculate maximum loan amount and interest rate"""
        # Base loan amount based on credit score
        score_factor = (credit_score - 300) / 550  # 0-1 range
        base_amount = int(score_factor * 100000 * 1000000)  # Up to 100K ALGO in microAlgos
        
        # Adjust based on wallet balance
        balance = wallet_data.get("current_balance", 0)
        balance_factor = min(1.0, balance / 1000000)  # 1 ALGO = 1.0 factor
        
        max_loan = int(base_amount * (0.5 + balance_factor * 0.5))
        max_loan = max(1000000, min(max_loan, 100000000000))  # 1 ALGO to 100K ALGO
        
        # Interest rate calculation (inverse to credit score)
        base_rate = 15.0  # 15% base rate
        score_discount = ((credit_score - 300) / 550) * 10  # Up to 10% discount
        interest_rate = max(3.0, base_rate - score_discount)
        
        return max_loan, interest_rate
    
    def _default_credit_analysis(self, wallet_address: str) -> Dict:
        """Return default credit analysis for errors"""
        return {
            "wallet_address": wallet_address,
            "credit_score": 500,
            "on_chain_score": 50.0,
            "off_chain_score": 50.0,
            "risk_level": "high",
            "max_loan_amount": 1000000,  # 1 ALGO
            "recommended_interest_rate": 12.0,
            "score_breakdown": {
                "account_age_contribution": 0,
                "transaction_activity": 0,
                "balance_stability": 0,
                "asset_diversity": 0,
                "dapp_usage": 0,
                "business_metrics": 50
            },
            "analysis_timestamp": datetime.now().isoformat(),
            "model_version": "1.0.0",
            "error": "Failed to analyze wallet"
        }


# Global instance
credit_scoring_service = CreditScoringService()
