// frontend/src/components/CodeHealthGauge.jsx

import React from "react";
import "../components.css"; // Assuming this imports the necessary styles

const CodeHealthGauge = ({ score }) => {
  // 1. Determine Color (Green: Good, Yellow: Medium, Red: Poor)
  const getColor = (s) => {
    if (s >= 75) return "var(--color-success)";
    if (s >= 50) return "var(--color-warning)";
    return "var(--color-danger)";
  };

  // 2. Calculate the rotation for the gauge needle (0 to 180 degrees)
  const normalizedScore = Math.min(100, Math.max(0, score)); // Clamp score between 0 and 100
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

// You will need to add corresponding CSS to frontend/src/components.css (see section 3)
