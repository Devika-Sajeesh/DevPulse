# backend/services/predictor.py (Improved)

from typing import Dict, Any
import math
import os
from joblib import load
import numpy as np

MODEL_PATH = "ml/historical_risk_model.joblib"
HISTORICAL_RISK_MODEL = None


def load_ml_model():
    """Loads the trained ML model into memory."""
    global HISTORICAL_RISK_MODEL
    
    if HISTORICAL_RISK_MODEL is None and os.path.exists(MODEL_PATH):
        try:
            HISTORICAL_RISK_MODEL = load(MODEL_PATH)
            print(f"ML Model successfully loaded from {MODEL_PATH}")
        except Exception as e:
            print(f"ERROR: Could not load ML model: {e}")
            HISTORICAL_RISK_MODEL = None
    elif HISTORICAL_RISK_MODEL is None:
        print(f"WARNING: ML Model not found at {MODEL_PATH}. Using heuristic fallback.")


def extract_features_for_prediction(parsed_analysis: Dict[str, Any], ai_probability: float) -> np.ndarray:
    """
    Extracts and normalizes features from analysis results.
    
    Features:
    1. Normalized Pylint Score (0-1)
    2. AI Code Probability (0-1)
    3. Normalized Code Lines (0-1)
    4. Normalized Average Complexity (0-1)
    5. Comment Ratio (0-1)
    6. Complexity Density (complexity per 100 LOC)
    """
    
    # 1. Pylint Score (0-10) -> Normalize to 0-1
    pylint_score = parsed_analysis.get("pylint", {}).get("score", 5.0)
    if pylint_score is None:
        pylint_score = 5.0
    static_score_normalized = pylint_score / 10.0
    
    # 2. AI Probability (already 0-1)
    ai_risk = ai_probability
    
    # 3. Code Lines - Better normalization with log scale
    cloc_data = parsed_analysis.get("cloc", {})
    
    # Get total code lines across all languages
    total_code_lines = cloc_data.get("code", 0)
    if total_code_lines == 0 and "languages" in cloc_data:
        # Sum up from languages if SUM not available
        for lang_data in cloc_data.get("languages", {}).values():
            if isinstance(lang_data, dict):
                total_code_lines += lang_data.get("code", 0)
    
    # Log-scale normalization for code lines (handles wide range better)
    # ln(1 + lines) / ln(1 + 10000) normalizes to ~0-1 for 0-10000 lines
    lines_normalized = math.log(1 + total_code_lines) / math.log(1 + 10000)
    lines_normalized = min(1.0, lines_normalized)
    
    # 4. Average Complexity
    radon_data = parsed_analysis.get("radon", {})
    avg_complexity = radon_data.get("average_complexity", 5.0)
    
    # Normalize complexity (typical range 1-20, with 10 being moderate)
    complexity_normalized = min(1.0, avg_complexity / 20.0)
    
    # 5. Comment Ratio (good documentation reduces risk)
    total_comments = cloc_data.get("comment", 0)
    comment_ratio = 0.0
    if total_code_lines > 0:
        comment_ratio = min(1.0, total_comments / total_code_lines)
    
    # 6. Complexity Density (complexity per 100 lines of code)
    complexity_density = 0.0
    if total_code_lines > 0 and radon_data.get("total_complexity", 0) > 0:
        complexity_density = (radon_data["total_complexity"] / total_code_lines) * 100
        complexity_density = min(1.0, complexity_density / 50.0)  # Normalize (50 is very high)
    
    # Build feature vector
    feature_vector = np.array([
        static_score_normalized,    # Higher = better quality
        ai_risk,                     # Higher = more AI code (risk)
        lines_normalized,            # Higher = larger codebase (risk)
        complexity_normalized,       # Higher = more complex (risk)
        comment_ratio,               # Higher = better documented (lower risk)
        complexity_density           # Higher = complex code per line (risk)
    ]).reshape(1, -1)
    
    return feature_vector


def get_historical_risk_score(repo_url: str, commit_sha: str, feature_vector: np.ndarray) -> float:
    """Predicts future technical debt risk using the ML model."""
    
    if HISTORICAL_RISK_MODEL:
        try:
            prediction = HISTORICAL_RISK_MODEL.predict(feature_vector)[0]
            # Clamp to 0-1 range
            return max(0.0, min(1.0, prediction))
        except Exception as e:
            print(f"Prediction failed ({e}). Falling back to heuristic.")
    
    # Fallback heuristic based on feature vector
    # Extract features: [pylint, ai_prob, lines, complexity, comments, density]
    features = feature_vector[0]
    
    # Simple heuristic: combine risk factors
    risk = 0.3  # Base risk
    
    # Penalize low quality
    if features[0] < 0.5:  # pylint < 5.0
        risk += 0.2
    
    # Penalize high AI code
    if features[1] > 0.5:
        risk += 0.2
    
    # Penalize large codebase
    if features[2] > 0.7:
        risk += 0.1
    
    # Penalize high complexity
    if features[3] > 0.6:
        risk += 0.15
    
    # Reward good documentation
    if features[4] > 0.2:
        risk -= 0.1
    
    return max(0.0, min(1.0, risk))


def calculate_chs(parsed_analysis: Dict[str, Any], ai_probability: float, historical_risk: float) -> float:
    """
    Calculates the Code Health Score (CHS) using weighted formula.
    
    CHS = (Pylint * W1) - (AI_Risk * W2) - (Historical_Risk * W3) - (Complexity_Penalty * W4)
    
    Scaled to 0-100.
    """
    
    # 1. Static Quality Score (Pylint 0-10 -> 0-1)
    pylint_score = parsed_analysis.get("pylint", {}).get("score")
    if pylint_score is None:
        static_score_normalized = 0.5
    else:
        static_score_normalized = pylint_score / 10.0
    
    # 2. AI Code Probability (0-1, higher is riskier)
    ai_risk_normalized = ai_probability
    
    # 3. Historical Risk (0-1, higher is riskier)
    historical_risk_normalized = historical_risk
    
    # 4. Complexity Penalty
    radon_data = parsed_analysis.get("radon", {})
    avg_complexity = radon_data.get("average_complexity", 5.0)
    complexity_penalty = min(1.0, avg_complexity / 20.0)
    
    # Define weights
    W_STATIC = 0.45          # Quality matters most
    W_AI_PENALTY = 0.25      # AI code is a moderate risk
    W_HIST_PENALTY = 0.20    # Predicted future risk
    W_COMPLEXITY = 0.10      # Complexity penalty
    
    # Calculate raw score (can be negative)
    chs_raw = (
        (static_score_normalized * W_STATIC) -
        (ai_risk_normalized * W_AI_PENALTY) -
        (historical_risk_normalized * W_HIST_PENALTY) -
        (complexity_penalty * W_COMPLEXITY)
    )
    
    # Add bonus for good documentation
    cloc_data = parsed_analysis.get("cloc", {})
    total_code = cloc_data.get("code", 1)
    total_comments = cloc_data.get("comment", 0)
    comment_ratio = total_comments / total_code if total_code > 0 else 0
    
    # Bonus for good documentation (up to 0.1)
    doc_bonus = min(0.1, comment_ratio * 0.5)
    chs_raw += doc_bonus
    
    # Scale to 100 (raw score is roughly -0.5 to 0.6)
    # Map [-0.5, 0.6] to [0, 100]
    chs_final = ((chs_raw + 0.5) / 1.1) * 100
    chs_final = max(0, min(100, chs_final))
    
    return round(chs_final, 2)