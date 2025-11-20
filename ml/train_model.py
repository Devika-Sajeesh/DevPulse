# ml/train_model.py (Improved)

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from joblib import dump
import os

def fetch_simulated_historical_data():
    """
    Generates synthetic training data with 6 features matching the new predictor.
    
    Features: [pylint_norm, ai_prob, lines_norm, complexity_norm, comment_ratio, complexity_density]
    Target: Historical Risk Score (0-1)
    """
    
    # Expanded training set with more realistic scenarios
    X = np.array([
        # [pylint, ai_prob, lines, complexity, comments, density]
        [0.9, 0.05, 0.2, 0.15, 0.25, 0.10],  # Excellent: High quality, well-documented
        [0.8, 0.10, 0.4, 0.25, 0.20, 0.15],  # Good: Solid quality
        [0.7, 0.15, 0.5, 0.35, 0.15, 0.20],  # Above Average
        [0.6, 0.25, 0.6, 0.45, 0.12, 0.30],  # Average with some issues
        [0.5, 0.40, 0.7, 0.55, 0.08, 0.40],  # Below Average
        [0.4, 0.60, 0.8, 0.65, 0.05, 0.50],  # Poor: High AI, complex
        [0.3, 0.80, 0.9, 0.75, 0.02, 0.65],  # Very Poor
        [0.2, 0.90, 0.95, 0.85, 0.01, 0.80], # Critical: Likely AI-generated mess
        
        # Edge cases
        [0.95, 0.0, 0.1, 0.10, 0.35, 0.05],  # Nearly perfect small project
        [0.85, 0.05, 0.85, 0.20, 0.30, 0.12], # Large but well-maintained
        [0.45, 0.70, 0.75, 0.70, 0.03, 0.60], # AI-heavy, complex, large
        [0.55, 0.30, 0.50, 0.60, 0.10, 0.45], # Moderate across the board
        
        # More realistic patterns
        [0.75, 0.20, 0.55, 0.40, 0.18, 0.25], # Decent with moderate AI
        [0.65, 0.35, 0.65, 0.50, 0.10, 0.35], # Degrading quality
        [0.82, 0.12, 0.45, 0.30, 0.22, 0.18], # Good maintenance
        [0.38, 0.75, 0.88, 0.80, 0.04, 0.70], # High-risk project
    ])
    
    # Target: Future Technical Debt Risk (0 = low, 1 = high)
    Y = np.array([
        0.05,  # Excellent code -> very low risk
        0.12,  # Good code -> low risk
        0.20,  # Above average -> low-moderate risk
        0.35,  # Average -> moderate risk
        0.50,  # Below average -> moderate-high risk
        0.68,  # Poor -> high risk
        0.82,  # Very poor -> very high risk
        0.95,  # Critical -> critical risk
        
        # Edge cases
        0.03,  # Nearly perfect
        0.15,  # Large but maintained
        0.78,  # AI-heavy complex
        0.45,  # Moderate
        
        # Realistic patterns
        0.25,  # Decent
        0.48,  # Degrading
        0.18,  # Well maintained
        0.85,  # High risk
    ])
    
    return X, Y

def train_and_save_model(model_path="ml/historical_risk_model.joblib"):
    """
    Trains a Ridge Regression model (better than plain Linear Regression).
    Includes feature scaling for better predictions.
    """
    print("\n" + "="*60)
    print("Starting ML Model Training (Improved Version)")
    print("="*60)
    
    X, Y = fetch_simulated_historical_data()
    
    print(f"\nTraining data shape: {X.shape}")
    print(f"Target data shape: {Y.shape}")
    print(f"Feature ranges:")
    print(f"  - Pylint (normalized): {X[:, 0].min():.2f} to {X[:, 0].max():.2f}")
    print(f"  - AI Probability: {X[:, 1].min():.2f} to {X[:, 1].max():.2f}")
    print(f"  - Code Lines (normalized): {X[:, 2].min():.2f} to {X[:, 2].max():.2f}")
    print(f"  - Complexity (normalized): {X[:, 3].min():.2f} to {X[:, 3].max():.2f}")
    print(f"  - Comment Ratio: {X[:, 4].min():.2f} to {X[:, 4].max():.2f}")
    print(f"  - Complexity Density: {X[:, 5].min():.2f} to {X[:, 5].max():.2f}")
    
    # Use Ridge Regression with regularization to prevent overfitting
    model = Ridge(alpha=0.1)  # Small regularization
    model.fit(X, Y)
    
    # Calculate R² score on training data
    score = model.score(X, Y)
    print(f"\nModel R² Score: {score:.4f}")
    
    # Save the trained model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    dump(model, model_path)
    
    print(f"\n✓ ML Model trained and saved to: {model_path}")
    print(f"\nModel coefficients (feature weights):")
    feature_names = ["Pylint", "AI_Prob", "Lines", "Complexity", "Comments", "Density"]
    for name, coef in zip(feature_names, model.coef_):
        direction = "↓ reduces risk" if coef < 0 else "↑ increases risk"
        print(f"  {name:12s}: {coef:+.4f}  {direction}")
    
    print(f"\nIntercept (baseline risk): {model.intercept_:.4f}")
    
    # Test predictions on sample data
    print("\n" + "="*60)
    print("Sample Predictions:")
    print("="*60)
    test_cases = [
        ([0.9, 0.05, 0.3, 0.2, 0.25, 0.1], "High quality, well-documented"),
        ([0.5, 0.5, 0.7, 0.6, 0.05, 0.5], "Average quality, high AI"),
        ([0.3, 0.8, 0.9, 0.8, 0.02, 0.7], "Poor quality, likely AI-generated"),
    ]
    
    for features, description in test_cases:
        pred = model.predict([features])[0]
        pred_clamped = max(0.0, min(1.0, pred))
        print(f"\n{description}")
        print(f"  Features: {features}")
        print(f"  Predicted Risk: {pred_clamped:.2%}")
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60 + "\n")
    
    return model_path

if __name__ == "__main__":
    train_and_save_model()