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

  const renderTab = () => {
    switch (activeTab) {
      case "radon":
        return (
          <div className="tab-content">
            <h3>Cyclomatic Complexity</h3>
            <p>{results.radon?.summary || "No summary available"}</p>
            <ul className="complexity-list">
              {results.radon?.entries?.length ? (
                results.radon.entries.map((e, i) => (
                  <li key={i} className="complexity-item">
                    <span className="line-number">{i + 1}</span>
                    {e}
                  </li>
                ))
              ) : (
                <li className="complexity-item">No complexity data</li>
              )}
            </ul>
          </div>
        );

      case "cloc":
        return (
          <div className="tab-content">
            <h3>Code Metrics</h3>
            <div className="metrics-grid">
              {results.cloc ? (
                Object.entries(results.cloc).map(([key, value], index) => (
                  <div key={key} className="metric-card">
                    <span className="metric-name">{formatMetricName(key)}</span>
                    {renderMetricValue(value)}
                  </div>
                ))
              ) : (
                <div className="no-data">No CLOC data available</div>
              )}
            </div>
          </div>
        );

      case "pylint":
        return (
          <div className="tab-content">
            <h3>Code Quality Report</h3>
            {results.pylint ? (
              <>
                <p className="score">
                  <strong>Score:</strong> {results.pylint.score ?? "N/A"}
                </p>
                <div className="pylint-report">
                  <pre>
                    {results.pylint.issues?.length
                      ? results.pylint.issues.join("\n")
                      : "No pylint issues found"}
                  </pre>
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

  const formatMetricName = (name) => {
    const nameMap = {
      SUM: "Total Lines",
      code: "Code Lines",
      comment: "Comments",
      blank: "Blank Lines",
      nFiles: "Number of Files",
    };
    return nameMap[name] || name;
  };

  const renderMetricValue = (value) => {
    if (typeof value === "object" && value !== null) {
      return (
        <pre className="metric-value">{JSON.stringify(value, null, 2)}</pre>
      );
    }
    return <span className="metric-value">{value}</span>;
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
