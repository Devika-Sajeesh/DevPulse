import React from "react";

const CodeHealthGauge = ({ score }) => {
  const getColor = (s) => {
    if (s >= 75) return "var(--success)";
    if (s >= 50) return "var(--warning)";
    return "var(--danger)";
  };

  const normalizedScore = Math.min(100, Math.max(0, score));
  const rotation = (normalizedScore / 100) * 180;
  const color = getColor(normalizedScore);

  return (
    <div className="code-health-gauge-container">
      <div className="gauge-arc" style={{ borderColor: color }}>
        <div
          className="gauge-needle"
          style={{
            transform: `rotate(${rotation}deg)`,
            backgroundColor: color,
          }}
        ></div>
      </div>
      <div className="score-value" style={{ color: color }}>
        {normalizedScore.toFixed(0)}
        <span className="score-unit">/100</span>
      </div>
      <div className="score-label">Code Health Score</div>
    </div>
  );
};

export default CodeHealthGauge;
