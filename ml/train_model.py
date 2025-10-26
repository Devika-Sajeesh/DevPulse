# ml/train_model.py

import numpy as np
from sklearn.linear_model import LinearRegression
from joblib import dump
import os

# --- This function simulates loading historical data from your SQLite DB ---
def fetch_simulated_historical_data():
    """
    Simulates loading data. In production, this would query db_service.get_all_reports()
    and process real metrics (Cyclomatic Complexity, LoC, etc.) 
    against a human-labeled 'Future Risk' or bug count.
    """
    
    # Static Metrics: X (Features)
    # [Norm. Static Score, AI Probability, Code Lines, Complexity Avg]
    X = np.array([
        [0.8, 0.1, 500, 5.0],  # Low Risk: High Static, Low AI, Small, Simple
        [0.4, 0.6, 2000, 15.0], # High Risk: Low Static, High AI, Large, Complex
        [0.6, 0.3, 1000, 8.0],  # Medium Risk
        [0.9, 0.0, 300, 4.0],   # Very Low Risk
        [0.5, 0.5, 1500, 12.0], # Medium Risk
        [0.3, 0.9, 5000, 20.0], # Very High Risk
    ])
    
    # Historical Risk: Y (Target)
    # The 'Future Cost' or 'Technical Debt' label (0.0 to 1.0)
    Y = np.array([0.1, 0.7, 0.4, 0.05, 0.6, 0.95])
    
    return X, Y

def train_and_save_model(model_path="ml/historical_risk_model.joblib"):
    """
    Trains a simple Linear Regression model and saves it.
    """
    print("Starting ML Model Training...")
    X, Y = fetch_simulated_historical_data()
    
    # Initialize and train the model
    model = LinearRegression()
    model.fit(X, Y)
    
    # Save the trained model to disk
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    dump(model, model_path)
    
    print(f"ML Model trained and saved to: {model_path}")
    print(f"Model coefficients (Weights): {model.coef_}")
    
    return model_path

if __name__ == "__main__":
    train_and_save_model()