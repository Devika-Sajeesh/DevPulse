# backend/services/predictor.py (Improved)

from typing import Dict, Any
import math
import os
from joblib import load
import numpy as np

# Use absolute path to avoid permission/CWD issues
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(_PROJECT_ROOT, "ml", "historical_risk_model.joblib")
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
    
    # Fallback: continuous weighted heuristic (smooth, not step-function)
    # Features: [pylint_norm, ai_prob, lines_norm, complexity_norm, comment_ratio, density]
    f = feature_vector[0]
    
    # Weighted continuous scoring — each factor contributes proportionally
    risk = (
        0.35 * (1.0 - f[0]) +   # Low pylint score = high risk
        0.20 * f[1] +             # High AI probability = moderate risk
        0.10 * f[2] +             # Large codebase = slight risk
        0.20 * f[3] +             # High complexity = significant risk
        -0.10 * f[4] +            # Good documentation reduces risk
        0.15 * f[5]               # High complexity density = risk
    )
    
    return max(0.0, min(1.0, risk))


def calculate_chs(parsed_analysis: Dict[str, Any], ai_probability: float, historical_risk: float) -> float:
    """
    Calculates the Code Health Score (CHS) on a 0-100 scale.
    
    Balanced formula where max positive = 100 and penalties subtract from it.
    Components:
      + Pylint quality:     0-50 points (code quality is the biggest factor)
      + Low complexity:     0-20 points (reward for simple, maintainable code)
      + Non-AI authenticity: 0-10 points (reward for human-written code)
      + Documentation:      0-15 points (reward for good comments)
      + Base credit:         5 points  (having analyzable code at all)
      - Historical risk:    0-15 points (predicted tech debt penalty)
    Max theoretical = 100, Min = 0
    """
    
    # 1. Pylint Quality (0-50 points)
    pylint_score = parsed_analysis.get("pylint", {}).get("score")
    if pylint_score is None:
        pylint_score = 5.0
    pylint_score = max(0.0, min(10.0, pylint_score))
    pylint_contribution = (pylint_score / 10.0) * 50

    # 2. Low Complexity Bonus (0-20 points) — reward simple code
    radon_data = parsed_analysis.get("radon", {})
    avg_complexity = radon_data.get("average_complexity", 5.0)
    # Lower complexity = higher bonus. complexity 1 → 20pts, complexity 20+ → 0pts
    complexity_bonus = max(0.0, (1.0 - min(1.0, avg_complexity / 20.0)) * 20)

    # 3. Non-AI Authenticity Bonus (0-10 points) — reward human-written code
    ai_bonus = (1.0 - ai_probability) * 10

    # 4. Documentation Bonus (0-15 points)
    cloc_data = parsed_analysis.get("cloc", {})
    total_code = max(cloc_data.get("code", 1), 1)
    total_comments = cloc_data.get("comment", 0)
    comment_ratio = total_comments / total_code
    doc_bonus = min(15.0, comment_ratio * 60)  # 25% ratio = full bonus

    # 5. Base Credit (5 points for having analyzable code)
    base = 5.0

    # 6. Historical Risk Penalty (0-15 points subtracted)
    risk_penalty = historical_risk * 15

    # Calculate final score
    chs_final = pylint_contribution + complexity_bonus + ai_bonus + doc_bonus + base - risk_penalty
    chs_final = max(0.0, min(100.0, chs_final))
    
    return round(chs_final, 2)