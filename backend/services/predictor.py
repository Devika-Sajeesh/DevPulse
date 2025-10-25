# backend/services/predictor.py

from typing import Dict, Any
import math

# Placeholder for the Historical Learning Module (The w3 score)
def get_historical_risk_score(repo_url: str, commit_sha: str) -> float:
    """
    Step 2: Placeholder for the ML model that predicts future risk (w3).

    In the MVP, this returns a simple, deterministic score.
    In the final product, this would query a trained LSTM/Transformer model.
    A score of 0.1 is Low Risk, 0.5 is Medium Risk, 1.0 is High Risk.
    """
    # For MVP: Return a fixed risk score until the ML model is trained.
    # Logic could be based on repo name, or a constant.
    if "tutorial" in repo_url.lower():
        return 0.1 # Low risk for simple repos
    if "api" in repo_url.lower() and "prod" in commit_sha.lower():
         return 0.7 # Medium-High risk for production code

    return 0.3 # Default Low-Medium Risk


def calculate_chs(parsed_analysis: Dict[str, Any], ai_probability: float, historical_risk: float) -> float:
    """
    Step 3: Calculates the Code Health Score (CHS) using a weighted formula.

    CHS = w1*StaticScore + w2*AI_DetectionScore + w3*HistoricalRiskScore
    The Pylint score is used as the primary static score (w1).
    """
    # 1. Extract w1: Static Score (Normalized 0-1)
    # Pylint score is 0-10, so normalize it.
    pylint_score = parsed_analysis["pylint"].get("score")
    if pylint_score is None:
        static_score_normalized = 0.5 # Neutral if Pylint score is missing
    else:
        static_score_normalized = pylint_score / 10.0

    # 2. Extract w2: AI Detection Score (AI Probability, 0-1)
    # Since higher AI probability means lower health, we subtract it.
    ai_risk_normalized = ai_probability

    # 3. Extract w3: Historical Risk Score (0-1)
    # Higher historical risk means lower health, so we subtract it.
    historical_risk_normalized = historical_risk

    # Define dynamic weights (MVP fixed weights for linear combination)
    # These weights would be dynamically optimized in the final product (Step 3)
    W_STATIC = 0.5    # How much static quality contributes to health
    W_AI_PENALTY = 0.3 # Penalty for AI-generated code risk
    W_HIST_PENALTY = 0.2 # Penalty for historical technical debt

    # Calculate CHS (Score out of 100 for better reporting)
    # Note: AI and Historical components act as penalties (subtracted).
    chs_raw = (
        (static_score_normalized * W_STATIC) -
        (ai_risk_normalized * W_AI_PENALTY) -
        (historical_risk_normalized * W_HIST_PENALTY)
    )

    # Scale CHS to 100 and clamp between 0 and 100
    chs_final = max(0, min(100, chs_raw * 200)) # Multiplying by 200 to give a range that balances penalties

    return round(chs_final, 2)