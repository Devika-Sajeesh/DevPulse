// frontend/src/components/PredictiveMetricsCard.jsx (Renamed from AISummaryCard.jsx)

import React from "react";
import ReactMarkdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import CodeHealthGauge from "./CodeHealthGauge"; // New Import

const PredictiveMetricsCard = ({ results }) => {
  if (!results || !results.ai_metrics) {
    return <div className="analysis-card">Loading predictive metrics...</div>;
  }

  // New Data Structure from backend/services/analyzer.py:
  const { code_health_score, historical_risk_score, ai_metrics, git_sha } =
    results;

  const { ai_probability, ai_risk_notes, recommendations } = ai_metrics;

  // Helper to format risk scores as percentage (0 to 1 -> 0% to 100%)
  const formatRisk = (score) => (score * 100).toFixed(0) + "%";

  // Helper to get color for risk scores (Red: High, Yellow: Medium, Green: Low)
  const getRiskColor = (prob) => {
    if (prob >= 0.7) return "var(--color-danger)";
    if (prob >= 0.4) return "var(--color-warning)";
    return "var(--color-success)";
  };

  return (
    <div className="analysis-card ai-summary-card">
      <h2 className="card-title">DevPulse Predictive Scorecard</h2>
      <p className="repo-info">
        Commit:{" "}
        <span className="git-sha">
          {git_sha ? git_sha.substring(0, 10) : "N/A"}
        </span>
      </p>

      <div className="metrics-grid">
        {/* 1. Code Health Score (CHS) - Gauge */}
        <div className="metric-box">
          <CodeHealthGauge score={code_health_score} />
        </div>

        {/* 2. AI Code Probability (w2) */}
        <div className="metric-box">
          <p className="metric-label">AI Code Probability (w2)</p>
          <p
            className="metric-value"
            style={{ color: getRiskColor(ai_probability) }}
          >
            {formatRisk(ai_probability)}
          </p>
          <p className="metric-note">**Risk Note:** {ai_risk_notes}</p>
        </div>

        {/* 3. Historical Risk Score (w3) */}
        <div className="metric-box">
          <p className="metric-label">Historical Debt Risk (w3)</p>
          <p
            className="metric-value"
            style={{ color: getRiskColor(historical_risk_score) }}
          >
            {formatRisk(historical_risk_score)}
          </p>
          <p className="metric-note">Predicted future tech debt risk.</p>
        </div>
      </div>

      {/* Actionable Insights */}
      <div className="recommendations">
        <h3>Actionable Insights:</h3>
        <ul>
          {recommendations.map((rec, index) => (
            <li key={index}>{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default PredictiveMetricsCard;
