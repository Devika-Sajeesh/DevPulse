import { useState } from "react";

export default function AnalysisTabs({ results }) {
  const [activeTab, setActiveTab] = useState("radon");

  if (!results)
    return <div className="no-results">No analysis results available</div>;

  const tabs = [
    { id: "radon", name: "Radon", icon: "fas fa-chart-line" },
    { id: "cloc", name: "CLOC", icon: "fas fa-code" },
    { id: "pylint", name: "Pylint", icon: "fas fa-check-circle" },
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "error": return "#ef4444";
      case "warning": return "#f59e0b";
      case "convention": return "#3b82f6";
      case "refactor": return "#8b5cf6";
      default: return "#6b7280";
    }
  };

  const getGradeColor = (grade) => {
    switch (grade) {
      case "A": return "#22c55e";
      case "B": return "#84cc16";
      case "C": return "#f59e0b";
      case "D": return "#f97316";
      case "E": return "#ef4444";
      case "F": return "#dc2626";
      default: return "#6b7280";
    }
  };

  const renderTab = () => {
    switch (activeTab) {
      case "radon":
        return (
          <div className="tab-content">
            <h3>Cyclomatic Complexity</h3>
            {results.radon ? (
              <>
                <div className="metrics-summary" style={{ marginBottom: "1rem", display: "flex", gap: "1.5rem" }}>
                  <div><strong>Functions:</strong> {results.radon.total_functions || 0}</div>
                  <div><strong>Avg Complexity:</strong> {results.radon.average_complexity || 0}</div>
                  <div><strong>Total Complexity:</strong> {results.radon.total_complexity || 0}</div>
                </div>
                <ul className="complexity-list">
                  {results.radon.blocks?.length > 0 ? (
                    results.radon.blocks.map((block, i) => (
                      <li key={i} className="complexity-item" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span
                          className="grade-badge"
                          style={{
                            backgroundColor: getGradeColor(block.grade),
                            color: "#fff",
                            padding: "2px 8px",
                            borderRadius: "4px",
                            fontWeight: "bold",
                            fontSize: "0.85rem",
                            minWidth: "28px",
                            textAlign: "center",
                          }}
                        >
                          {block.grade}
                        </span>
                        <span style={{ fontFamily: "monospace" }}>{block.name}</span>
                        <span style={{ color: "#888", fontSize: "0.85rem" }}>
                          ({block.type}) — complexity: {block.complexity}
                        </span>
                        <span style={{ color: "#666", fontSize: "0.8rem", marginLeft: "auto" }}>
                          {block.file}
                        </span>
                      </li>
                    ))
                  ) : (
                    <li className="complexity-item">No complexity blocks found</li>
                  )}
                </ul>
              </>
            ) : (
              <p>No Radon data available</p>
            )}
          </div>
        );

      case "cloc":
        return (
          <div className="tab-content">
            <h3>Code Metrics</h3>
            {results.cloc ? (
              <>
                <div className="metrics-grid">
                  <div className="metric-card">
                    <span className="metric-name">Code Lines</span>
                    <span className="metric-value">{results.cloc.code || 0}</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-name">Comments</span>
                    <span className="metric-value">{results.cloc.comment || 0}</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-name">Blank Lines</span>
                    <span className="metric-value">{results.cloc.blank || 0}</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-name">Total Files</span>
                    <span className="metric-value">{results.cloc.total_files || 0}</span>
                  </div>
                </div>
                {results.cloc.languages && Object.keys(results.cloc.languages).length > 0 && (
                  <div style={{ marginTop: "1rem" }}>
                    <h4>Languages</h4>
                    <div className="metrics-grid">
                      {Object.entries(results.cloc.languages).map(([lang, data]) => (
                        <div key={lang} className="metric-card">
                          <span className="metric-name">{lang}</span>
                          <span className="metric-value">
                            {data.code} lines · {data.files || data.nFiles || 0} files
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="no-data">No CLOC data available</div>
            )}
          </div>
        );

      case "pylint":
        return (
          <div className="tab-content">
            <h3>Code Quality Report</h3>
            {results.pylint ? (
              <>
                <p className="score">
                  <strong>Score:</strong> {results.pylint.score ?? "N/A"} / 10
                  {results.pylint.total_issues != null && (
                    <span style={{ marginLeft: "1rem", color: "#888" }}>
                      ({results.pylint.total_issues} issues)
                    </span>
                  )}
                </p>
                {results.pylint.issue_counts && (
                  <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", flexWrap: "wrap" }}>
                    {Object.entries(results.pylint.issue_counts).map(([severity, count]) => (
                      <span
                        key={severity}
                        style={{
                          backgroundColor: getSeverityColor(severity),
                          color: "#fff",
                          padding: "4px 12px",
                          borderRadius: "12px",
                          fontSize: "0.8rem",
                          fontWeight: "500",
                        }}
                      >
                        {severity}: {count}
                      </span>
                    ))}
                  </div>
                )}
                <div className="pylint-report">
                  {results.pylint.issues?.length > 0 ? (
                    <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                      {results.pylint.issues.map((issue, i) => (
                        <li
                          key={i}
                          style={{
                            padding: "0.5rem 0",
                            borderBottom: "1px solid rgba(255,255,255,0.05)",
                            fontFamily: "monospace",
                            fontSize: "0.85rem",
                          }}
                        >
                          <span
                            style={{
                              color: getSeverityColor(issue.severity),
                              fontWeight: "bold",
                              marginRight: "0.5rem",
                            }}
                          >
                            {issue.code}
                          </span>
                          <span style={{ color: "#aaa" }}>
                            {issue.file}:{issue.line}
                          </span>
                          <span style={{ marginLeft: "0.5rem" }}>
                            {issue.message}
                          </span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>No pylint issues found ✅</p>
                  )}
                </div>
              </>
            ) : (
              <p>No Pylint data available</p>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="analysis-tabs">
      <div className="tabs-header">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-button ${activeTab === tab.id ? "active" : ""}`}
          >
            <i className={tab.icon}></i>
            {tab.name}
          </button>
        ))}
      </div>
      <div className="tab-content-container">{renderTab()}</div>
    </div>
  );
}
