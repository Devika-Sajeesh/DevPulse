import React from "react";
import CodeHealthGauge from "./CodeHealthGauge";

const PredictiveMetricsCard = ({ results }) => {
  if (!results || !results.ai_metrics) {
    return (
      <div className="ai-summary-card">
        <div className="ai-summary-header">
          <div className="ai-summary-title">
            <i className="fas fa-chart-line"></i>
            <h3>DevPulse Predictive Scorecard</h3>
          </div>
        </div>
        <div className="ai-summary-content expanded">
          <div className="loading">Loading predictive metrics...</div>
        </div>
      </div>
    );
  }

  const { code_health_score, historical_risk_score, ai_metrics, git_sha } =
    results;
  const { ai_probability, ai_risk_notes, recommendations } = ai_metrics;

  const formatRisk = (score) => (score * 100).toFixed(0) + "%";

  const getRiskColor = (prob) => {
    if (prob >= 0.7) return "var(--danger)";
    if (prob >= 0.4) return "var(--warning)";
    return "var(--success)";
  };

  return (
    <div className="ai-summary-card">
      <div className="ai-summary-header">
        <div className="ai-summary-title">
          <i className="fas fa-chart-line"></i>
          <h3>DevPulse Predictive Scorecard</h3>
        </div>
      </div>

      <div className="ai-summary-content expanded">
        <div className="metrics-grid">
          {/* Code Health Score - Full width on mobile */}
          <div className="metric-card health-score-card">
            <CodeHealthGauge score={code_health_score} />
          </div>

          {/* AI Code Probability */}
          <div className="metric-card">
            <span className="metric-name">AI Code Probability</span>
            <span
              className="metric-value"
              style={{ color: getRiskColor(ai_probability) }}
            >
              {formatRisk(ai_probability)}
            </span>
            <div className="metric-note">{ai_risk_notes}</div>
          </div>

          {/* Historical Risk Score */}
          <div className="metric-card">
            <span className="metric-name">Historical Debt Risk</span>
            <span
              className="metric-value"
              style={{ color: getRiskColor(historical_risk_score) }}
            >
              {formatRisk(historical_risk_score)}
            </span>
            <div className="metric-note">Predicted future tech debt risk</div>
          </div>
        </div>

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <div className="recommendations">
            <h4 className="md-heading md-h4">Actionable Insights</h4>
            <ul className="md-list">
              {recommendations.map((rec, index) => (
                <li key={index} className="md-list-item">
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {git_sha && (
          <div className="repo-info">
            Commit:{" "}
            <span className="inline-code">{git_sha.substring(0, 10)}</span>
          </div>
        )}
      </div>

      <div className="ai-summary-footer">
        <div className="ai-tag">
          <i className="fas fa-chart-bar"></i>
          Predictive Analytics
        </div>
      </div>
    </div>
  );
};

export default PredictiveMetricsCard;
