# backend/services/predictor.py (Updated)

from typing import Dict, Any
import math
import os
from joblib import load
import numpy as np

# Path to the saved model file
MODEL_PATH = "ml/historical_risk_model.joblib"
# Global variable to hold the loaded ML model
HISTORICAL_RISK_MODEL = None


def load_ml_model():
    """
    Loads the trained ML model into memory.
    This should be called once on application startup.
    """
    global HISTORICAL_RISK_MODEL
    
    if HISTORICAL_RISK_MODEL is None and os.path.exists(MODEL_PATH):
        try:
            HISTORICAL_RISK_MODEL = load(MODEL_PATH)
            print(f"ML Model successfully loaded from {MODEL_PATH}")
        except Exception as e:
            print(f"ERROR: Could not load ML model: {e}")
            HISTORICAL_RISK_MODEL = None
    elif HISTORICAL_RISK_MODEL is None:
        print(f"WARNING: ML Model not found at {MODEL_PATH}. Using fixed heuristic.")
        # If the model doesn't exist, it will remain None, and prediction will fall back.


def extract_features_for_prediction(parsed_analysis: Dict[str, Any], ai_probability: float) -> np.ndarray:
    """
    Extracts and scales features from the current analysis report into the 
    exact vector format expected by the trained ML model.
    """
    # 1. Normalize Static Score (0-1)
    pylint_score = parsed_analysis["pylint"].get("score", 5.0)
    if pylint_score is None:
        pylint_score = 5.0  # safe midpoint fallback
    static_score_normalized = pylint_score / 10.0

    # 2. AI Probability (0-1)
    ai_risk = ai_probability
    
    # 3. Code Lines (Simulated normalization for model input)
    # In a real model, you'd use min/max scaling based on training data statistics.
    total_code_lines = parsed_analysis["cloc"].get("Python", {}).get("code", 0) 
    # Use 5000 lines as a rough maximum for normalization simulation
    lines_normalized = min(1.0, total_code_lines / 5000.0) 

    # 4. Complexity Average (Simulated normalization for model input)
    # Radon output is complex; using a heuristic average complexity.
    # We will simulate this value based on the Pylint score for the feature vector input.
    complexity_avg = 15.0 - (pylint_score * 1.0) # Assume high pylint means low complexity
    complexity_normalized = min(1.0, complexity_avg / 20.0) # Max complexity simulation

    # The ML Model expects: [Norm. Static Score, AI Probability, Code Lines, Complexity Avg]
    feature_vector = np.array([
        static_score_normalized, 
        ai_risk, 
        lines_normalized, 
        complexity_normalized
    ]).reshape(1, -1) # Reshape for single prediction

    return feature_vector


def get_historical_risk_score(repo_url: str, commit_sha: str, feature_vector: np.ndarray) -> float:
    """
    Step 2: Predicts future risk (w3) using the loaded ML model or falls back to heuristic.
    """
    if HISTORICAL_RISK_MODEL:
        try:
            # Predict the Historical Risk Score (w3) using the feature vector
            prediction = HISTORICAL_RISK_MODEL.predict(feature_vector)[0]
            # Clamp the prediction to the 0.0 to 1.0 range
            return max(0.0, min(1.0, prediction))
        except Exception as e:
            print(f"Prediction failed ({e}). Falling back to heuristic.")
            
    # Fallback: Use the original heuristic if the model failed or is not loaded
    if "tutorial" in repo_url.lower():
        return 0.1
    if "api" in repo_url.lower() and "prod" in commit_sha.lower():
         return 0.7 
    return 0.3


def calculate_chs(parsed_analysis: Dict[str, Any], ai_probability: float, historical_risk: float) -> float:
    """
    Step 3: Calculates the Code Health Score (CHS) using a weighted formula.
    """
    # 1. Extract w1: Static Score (Normalized 0-1)
    pylint_score = parsed_analysis["pylint"].get("score")
    if pylint_score is None:
        static_score_normalized = 0.5 
    else:
        static_score_normalized = pylint_score / 10.0

    # 2. Extract w2: AI Detection Score (AI Probability, 0-1)
    ai_risk_normalized = ai_probability

    # 3. Extract w3: Historical Risk Score (0-1)
    historical_risk_normalized = historical_risk

    # Define dynamic weights (fixed weights for this version)
    W_STATIC = 0.5    
    W_AI_PENALTY = 0.3 
    W_HIST_PENALTY = 0.2 

    # Calculate CHS (Score out of 100)
    chs_raw = (
        (static_score_normalized * W_STATIC) -
        (ai_risk_normalized * W_AI_PENALTY) -
        (historical_risk_normalized * W_HIST_PENALTY)
    )

    # Scale CHS to 100 and clamp between 0 and 100
    chs_final = max(0, min(100, chs_raw * 200)) 

    return round(chs_final, 2)