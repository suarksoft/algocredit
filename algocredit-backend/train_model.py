"""
AlgoCredit AI Credit Scoring Model
Machine Learning model for wallet-based credit scoring
"""

import pandas as pd
import numpy as np
import pickle
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

class AlgoCreditAI:
    """AI model for credit scoring based on Algorand wallet analysis"""
    
    def __init__(self):
        self.model = None
        self.scaler = RobustScaler()  # More robust to outliers
        self.feature_names = [
            'account_age_days',
            'total_transactions', 
            'total_volume',
            'current_balance',
            'average_balance',
            'balance_stability_score',
            'transaction_frequency_score',
            'asset_diversity_score',
            'dapp_usage_score',
            'unique_counterparties',
            'avg_transaction_size'
        ]
        self.is_trained = False
        self.model_metadata = {}
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and engineer features for training"""
        
        # Create feature matrix
        feature_df = df[self.feature_names].copy()
        
        # Feature engineering
        feature_df['log_balance'] = np.log(feature_df['current_balance'] + 1)
        feature_df['log_volume'] = np.log(feature_df['total_volume'] + 1)
        feature_df['transactions_per_day'] = feature_df['total_transactions'] / (feature_df['account_age_days'] + 1)
        feature_df['balance_to_volume_ratio'] = feature_df['current_balance'] / (feature_df['total_volume'] + 1)
        feature_df['avg_transaction_normalized'] = feature_df['avg_transaction_size'] / (feature_df['current_balance'] + 1)
        
        # Composite scores
        feature_df['activity_score'] = (
            feature_df['transaction_frequency_score'] * 0.4 +
            feature_df['asset_diversity_score'] * 0.3 +
            feature_df['dapp_usage_score'] * 0.3
        )
        
        feature_df['stability_score'] = (
            feature_df['balance_stability_score'] * 0.6 +
            (feature_df['account_age_days'] / 365) * 20 * 0.4  # Age factor
        )
        
        # Handle any infinite or NaN values
        feature_df = feature_df.replace([np.inf, -np.inf], np.nan)
        feature_df = feature_df.fillna(0)
        
        return feature_df
    
    def train_model(self, train_data: pd.DataFrame, target_col: str = 'credit_score') -> Dict:
        """Train the credit scoring model"""
        
        print("🚀 Starting AlgoCredit AI Model Training...")
        
        # Prepare features and target
        X = self.prepare_features(train_data)
        y = train_data[target_col].values
        
        print(f"📊 Training with {len(X)} samples and {len(X.columns)} features")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=pd.cut(y, bins=5)
        )
        
        # Scale features
        print("⚖️ Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Try multiple models and select the best
        models = {
            'RandomForest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        }
        
        best_model = None
        best_score = -np.inf
        model_results = {}
        
        print("🔍 Testing different models...")
        
        for name, model in models.items():
            print(f"   Training {name}...")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Validate
            val_pred = model.predict(X_val_scaled)
            r2 = r2_score(y_val, val_pred)
            rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            mae = mean_absolute_error(y_val, val_pred)
            
            model_results[name] = {
                'r2_score': r2,
                'rmse': rmse,
                'mae': mae,
                'model': model
            }
            
            print(f"   {name} - R²: {r2:.3f}, RMSE: {rmse:.1f}, MAE: {mae:.1f}")
            
            if r2 > best_score:
                best_score = r2
                best_model = model
                best_model_name = name
        
        # Save the best model
        self.model = best_model
        self.is_trained = True
        
        # Model metadata
        self.model_metadata = {
            'best_model': best_model_name,
            'training_date': datetime.now().isoformat(),
            'training_samples': len(X_train),
            'validation_samples': len(X_val),
            'features_count': len(X.columns),
            'performance': model_results[best_model_name],
            'all_results': {k: {key: val for key, val in v.items() if key != 'model'} 
                           for k, v in model_results.items()}
        }
        
        print(f"✅ Best model: {best_model_name} with R² = {best_score:.3f}")
        
        # Feature importance analysis
        if hasattr(best_model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': best_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\n📊 Top 5 Most Important Features:")
            for idx, row in feature_importance.head().iterrows():
                print(f"   {row['feature']}: {row['importance']:.3f}")
            
            self.model_metadata['feature_importance'] = feature_importance.to_dict('records')
        
        return self.model_metadata
    
    def predict_credit_score(self, wallet_data: Dict) -> Dict:
        """Predict credit score for a single wallet"""
        
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        # Convert to DataFrame
        df = pd.DataFrame([wallet_data])
        
        # Prepare features
        X = self.prepare_features(df)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        raw_prediction = self.model.predict(X_scaled)[0]
        
        # Ensure score is in valid range (300-850)
        credit_score = max(300, min(850, int(round(raw_prediction))))
        
        # Calculate confidence based on feature values
        confidence = self._calculate_confidence(wallet_data)
        
        # Determine risk level
        risk_level = self._get_risk_level(credit_score)
        
        # Additional insights
        insights = self._generate_insights(wallet_data, credit_score)
        
        return {
            'credit_score': credit_score,
            'confidence': round(confidence, 2),
            'risk_level': risk_level,
            'insights': insights,
            'model_version': self.model_metadata.get('training_date', 'unknown'),
            'features_used': len(self.feature_names) + 6  # +6 for engineered features
        }
    
    def _calculate_confidence(self, wallet_data: Dict) -> float:
        """Calculate prediction confidence based on data quality"""
        
        confidence = 100.0
        
        # Penalize for missing or low data
        if wallet_data.get('account_age_days', 0) < 30:
            confidence -= 20  # New accounts are less reliable
        
        if wallet_data.get('total_transactions', 0) < 10:
            confidence -= 15  # Low transaction history
        
        if wallet_data.get('current_balance', 0) < 1000:
            confidence -= 10  # Very low balance
        
        # Bonus for good data
        if wallet_data.get('account_age_days', 0) > 365:
            confidence += 10
        
        if wallet_data.get('dapp_usage_score', 0) > 50:
            confidence += 5
        
        return max(50, min(100, confidence))  # Keep between 50-100%
    
    def _get_risk_level(self, credit_score: int) -> str:
        """Convert credit score to risk level"""
        if credit_score >= 750:
            return 'low'
        elif credit_score >= 650:
            return 'medium'
        elif credit_score >= 550:
            return 'medium-high'
        else:
            return 'high'
    
    def _generate_insights(self, wallet_data: Dict, credit_score: int) -> List[str]:
        """Generate insights based on wallet analysis"""
        insights = []
        
        age_days = wallet_data.get('account_age_days', 0)
        transactions = wallet_data.get('total_transactions', 0)
        balance = wallet_data.get('current_balance', 0)
        
        # Age insights
        if age_days > 730:
            insights.append("✅ Mature account with long history")
        elif age_days > 180:
            insights.append("📅 Established account")
        else:
            insights.append("⚠️ Relatively new account")
        
        # Activity insights
        if transactions > 100:
            insights.append("✅ High transaction activity")
        elif transactions > 20:
            insights.append("📊 Moderate activity level")
        else:
            insights.append("⚠️ Limited transaction history")
        
        # Balance insights
        if balance > 50000:
            insights.append("💰 Strong financial position")
        elif balance > 10000:
            insights.append("💵 Adequate balance")
        else:
            insights.append("⚠️ Low account balance")
        
        # DApp usage
        dapp_score = wallet_data.get('dapp_usage_score', 0)
        if dapp_score > 70:
            insights.append("🔗 Active DeFi participant")
        elif dapp_score > 30:
            insights.append("🔗 Some DApp usage")
        
        return insights
    
    def save_model(self, filepath: str = None):
        """Save trained model to file"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        if filepath is None:
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_dir, 'models', 'algocredit_ai_model.pkl')
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metadata': self.model_metadata
        }
        
        joblib.dump(model_data, filepath)
        print(f"💾 Model saved to {filepath}")
    
    def load_model(self, filepath: str = None):
        """Load trained model from file"""
        if filepath is None:
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_dir, 'models', 'algocredit_ai_model.pkl')
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_metadata = model_data['metadata']
        self.is_trained = True
        
        print(f"📂 Model loaded from {filepath}")

def train_and_save_model():
    """Train and save the AlgoCredit AI model"""
    
    # Load training data
    print("📂 Loading training data...")
    train_df = pd.read_csv('algocredit-backend/data/training_data.csv')
    test_df = pd.read_csv('algocredit-backend/data/test_data.csv')
    
    # Initialize and train model
    ai_model = AlgoCreditAI()
    training_results = ai_model.train_model(train_df)
    
    # Test on test set
    print("\n🧪 Testing on hold-out test set...")
    test_X = ai_model.prepare_features(test_df)
    test_X_scaled = ai_model.scaler.transform(test_X)
    test_pred = ai_model.model.predict(test_X_scaled)
    
    test_r2 = r2_score(test_df['credit_score'], test_pred)
    test_rmse = np.sqrt(mean_squared_error(test_df['credit_score'], test_pred))
    
    print(f"📊 Test Set Performance:")
    print(f"   R² Score: {test_r2:.3f}")
    print(f"   RMSE: {test_rmse:.1f}")
    
    # Save model
    ai_model.save_model()
    
    # Save metadata (without model objects)
    metadata_to_save = training_results.copy()
    if 'performance' in metadata_to_save and 'model' in metadata_to_save['performance']:
        del metadata_to_save['performance']['model']
    
    with open('algocredit-backend/models/model_metadata.json', 'w') as f:
        json.dump(metadata_to_save, f, indent=2)
    
    print("\n🎉 AlgoCredit AI model training completed!")
    return ai_model

if __name__ == "__main__":
    train_and_save_model()