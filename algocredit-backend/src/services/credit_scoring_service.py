"""
AlgoCredit Credit Scoring Service
AI-powered credit scoring based on Algorand wallet analysis
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime
import json
import numpy as np

# Add parent directory to path to import train_model
sys.path.append('/Users/ahmetbugrakurnaz/Desktop/algorand/algocredit-backend')
from train_model import AlgoCreditAI

"""
AlgoCredit Credit Scoring Service
AI-powered credit scoring based on Algorand wallet analysis
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime
import json

# Add parent directory to path to import train_model
sys.path.append('/Users/ahmetbugrakurnaz/Desktop/algorand/algocredit-backend')

try:
    from train_model import AlgoCreditAI
    AI_MODEL_AVAILABLE = True
except ImportError:
    print("⚠️ AI model not available, using fallback scoring")
    AI_MODEL_AVAILABLE = False

from .algorand_service import algorand_service


class CreditScoringService:
    """Service for AI-powered credit scoring"""
    
    def __init__(self):
        """Initialize the credit scoring service"""
        self.ai_model = None
        self.model_loaded = False
        if AI_MODEL_AVAILABLE:
            self.load_model()
    
    def load_model(self) -> bool:
        """Load the trained AI model"""
        if not AI_MODEL_AVAILABLE:
            return False
            
        try:
            self.ai_model = AlgoCreditAI()
            import os
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(current_dir, 'models', 'algocredit_ai_model.pkl')
            
            if os.path.exists(model_path):
                self.ai_model.load_model(model_path)
                self.model_loaded = True
                print("✅ AI model loaded successfully")
                return True
            else:
                print(f"⚠️ Model file not found at {model_path}")
                return False
        except Exception as e:
            print(f"❌ Error loading AI model: {e}")
            return False
    
    async def analyze_wallet_and_score(self, wallet_address: str) -> Dict:
        """Analyze wallet and generate comprehensive credit score"""
        try:
            # Step 1: Get wallet analysis from Algorand service
            print(f"🔍 Analyzing wallet: {wallet_address}")
            wallet_analysis = await algorand_service.analyze_wallet_behavior(wallet_address)
            
            if not wallet_analysis or not wallet_analysis.get('wallet_address'):
                return self._default_credit_assessment(wallet_address, "Unable to analyze wallet")
            
            # Step 2: AI-powered credit scoring
            if self.model_loaded and self.ai_model:
                ai_prediction = self.ai_model.predict_credit_score(wallet_analysis)
                credit_score = ai_prediction['credit_score']
                confidence = ai_prediction['confidence']
                risk_level = ai_prediction['risk_level']
                insights = ai_prediction['insights']
                scoring_method = "AI Model"
            else:
                # Fallback to heuristic scoring
                credit_score, confidence, risk_level, insights = self._heuristic_scoring(wallet_analysis)
                scoring_method = "Heuristic"
            
            # Step 3: Calculate additional metrics
            max_loan_amount = self._calculate_max_loan_amount(credit_score, wallet_analysis)
            recommended_interest_rate = self._calculate_interest_rate(credit_score, risk_level)
            
            # Step 4: Generate detailed assessment
            assessment = {
                "wallet_address": wallet_address,
                "credit_score": credit_score,
                "confidence": confidence,
                "risk_level": risk_level,
                "max_loan_amount": max_loan_amount,
                "recommended_interest_rate": recommended_interest_rate,
                "insights": insights,
                "assessment_breakdown": {
                    "on_chain_score": self._calculate_on_chain_score(wallet_analysis),
                    "stability_score": wallet_analysis.get('balance_stability_score', 0),
                    "activity_score": wallet_analysis.get('transaction_frequency_score', 0),
                    "diversity_score": wallet_analysis.get('asset_diversity_score', 0),
                    "defi_score": wallet_analysis.get('dapp_usage_score', 0)
                },
                "wallet_metrics": {
                    "account_age_days": wallet_analysis.get('account_age_days', 0),
                    "total_transactions": wallet_analysis.get('total_transactions', 0),
                    "current_balance_algo": wallet_analysis.get('current_balance', 0) / 1_000_000,
                    "total_volume_algo": wallet_analysis.get('total_volume', 0) / 1_000_000
                },
                "model_info": {
                    "model_version": "AlgoCredit AI v1.0",
                    "scoring_method": scoring_method,
                    "ai_enabled": self.model_loaded,
                    "assessment_timestamp": datetime.now().isoformat()
                }
            }
            
            print(f"✅ Credit assessment completed for {wallet_address}")
            print(f"   Score: {credit_score}, Risk: {risk_level}, Confidence: {confidence}%")
            
            return assessment
            
        except Exception as e:
            print(f"❌ Error in credit scoring: {e}")
            return self._default_credit_assessment(wallet_address, f"Analysis error: {str(e)}")
    
    def _heuristic_scoring(self, wallet_analysis: Dict) -> tuple:
        """Fallback heuristic scoring when AI model is not available"""
        
        # Extract key metrics
        age_days = wallet_analysis.get('account_age_days', 0)
        transactions = wallet_analysis.get('total_transactions', 0)
        balance = wallet_analysis.get('current_balance', 0)
        stability = wallet_analysis.get('balance_stability_score', 0)
        activity = wallet_analysis.get('transaction_frequency_score', 0)
        
        # Base score calculation
        base_score = 500  # Middle of 300-850 range
        
        # Age factor (up to +100 points)
        if age_days > 730:  # 2+ years
            base_score += 80
        elif age_days > 365:  # 1+ year
            base_score += 60
        elif age_days > 90:  # 3+ months
            base_score += 30
        
        # Transaction history factor (up to +80 points)
        if transactions > 100:
            base_score += 60
        elif transactions > 50:
            base_score += 40
        elif transactions > 10:
            base_score += 20
        
        # Balance factor (up to +70 points)
        balance_algo = balance / 1_000_000
        if balance_algo > 10000:
            base_score += 60
        elif balance_algo > 1000:
            base_score += 40
        elif balance_algo > 100:
            base_score += 20
        
        # Stability and activity factors
        base_score += stability * 0.5  # Up to +50 points
        base_score += activity * 0.3   # Up to +30 points
        
        # Ensure valid range
        credit_score = max(300, min(850, int(base_score)))
        
        # Calculate confidence
        confidence = 75.0  # Default confidence for heuristic
        if age_days < 30 or transactions < 5:
            confidence = 60.0
        elif age_days > 365 and transactions > 50:
            confidence = 85.0
        
        # Determine risk level
        if credit_score >= 750:
            risk_level = 'low'
        elif credit_score >= 650:
            risk_level = 'medium'
        elif credit_score >= 550:
            risk_level = 'medium-high'
        else:
            risk_level = 'high'
        
        # Generate insights
        insights = []
        if age_days > 365:
            insights.append("✅ Established account history")
        if transactions > 50:
            insights.append("✅ Good transaction activity")
        if balance_algo > 1000:
            insights.append("💰 Strong balance position")
        if credit_score < 600:
            insights.append("⚠️ Limited credit history")
        
        return credit_score, confidence, risk_level, insights
    
    def _calculate_on_chain_score(self, wallet_analysis: Dict) -> float:
        """Calculate on-chain behavior score"""
        
        metrics = [
            wallet_analysis.get('balance_stability_score', 0),
            wallet_analysis.get('transaction_frequency_score', 0),
            wallet_analysis.get('asset_diversity_score', 0),
            wallet_analysis.get('dapp_usage_score', 0)
        ]
        
        # Weighted average
        weights = [0.3, 0.25, 0.25, 0.2]
        on_chain_score = sum(metric * weight for metric, weight in zip(metrics, weights))
        
        return round(on_chain_score, 2)
    
    def _calculate_max_loan_amount(self, credit_score: int, wallet_analysis: Dict) -> int:
        """Calculate maximum loan amount based on credit score and wallet metrics"""
        
        # Base loan amount based on credit score
        if credit_score >= 800:
            base_amount = 100000  # 100k ALGO
        elif credit_score >= 750:
            base_amount = 75000
        elif credit_score >= 700:
            base_amount = 50000
        elif credit_score >= 650:
            base_amount = 25000
        elif credit_score >= 600:
            base_amount = 15000
        elif credit_score >= 550:
            base_amount = 10000
        else:
            base_amount = 5000
        
        # Adjust based on wallet balance (collateral factor)
        current_balance = wallet_analysis.get('current_balance', 0) / 1_000_000  # Convert to ALGO
        balance_factor = min(1.0, current_balance / 10000)  # Cap at 10k ALGO
        
        # Adjust based on transaction history
        transactions = wallet_analysis.get('total_transactions', 0)
        history_factor = min(1.0, transactions / 100)  # Cap at 100 transactions
        
        # Final calculation
        max_loan = int(base_amount * (0.6 + 0.3 * balance_factor + 0.1 * history_factor))
        
        return max_loan
    
    def _calculate_interest_rate(self, credit_score: int, risk_level: str) -> float:
        """Calculate recommended interest rate based on credit score"""
        
        # Base rates by credit score
        if credit_score >= 800:
            base_rate = 5.0
        elif credit_score >= 750:
            base_rate = 6.5
        elif credit_score >= 700:
            base_rate = 8.0
        elif credit_score >= 650:
            base_rate = 10.0
        elif credit_score >= 600:
            base_rate = 12.5
        elif credit_score >= 550:
            base_rate = 15.0
        else:
            base_rate = 18.0
        
        # Risk adjustment
        risk_adjustments = {
            'low': -0.5,
            'medium': 0.0,
            'medium-high': 1.0,
            'high': 2.0
        }
        
        final_rate = base_rate + risk_adjustments.get(risk_level, 0)
        
        return round(final_rate, 1)
    
    def _default_credit_assessment(self, wallet_address: str, reason: str) -> Dict:
        """Return default assessment when analysis fails"""
        return {
            "wallet_address": wallet_address,
            "credit_score": 500,  # Neutral score
            "confidence": 30.0,   # Low confidence
            "risk_level": "high",
            "max_loan_amount": 1000,
            "recommended_interest_rate": 20.0,
            "insights": ["⚠️ Unable to analyze wallet", f"Reason: {reason}"],
            "assessment_breakdown": {
                "on_chain_score": 0,
                "stability_score": 0,
                "activity_score": 0,
                "diversity_score": 0,
                "defi_score": 0
            },
            "wallet_metrics": {
                "account_age_days": 0,
                "total_transactions": 0,
                "current_balance_algo": 0,
                "total_volume_algo": 0
            },
            "model_info": {
                "model_version": "Fallback v1.0",
                "scoring_method": "Error Fallback",
                "ai_enabled": False,
                "assessment_timestamp": datetime.now().isoformat(),
                "error": reason
            }
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if self.model_loaded and self.ai_model:
            return {
                "model_loaded": True,
                "model_metadata": getattr(self.ai_model, 'model_metadata', {}),
                "features_count": len(getattr(self.ai_model, 'feature_names', [])) + 6,  # +6 engineered features
                "model_type": "Random Forest Regressor"
            }
        else:
            return {
                "model_loaded": False,
                "fallback_mode": "Heuristic scoring",
                "recommendation": "Train and load AI model for better accuracy"
            }


# Global instance
credit_scoring_service = CreditScoringService()
