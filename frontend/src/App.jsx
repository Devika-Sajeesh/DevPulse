// frontend/src/App.jsx

import { useState } from "react";

// Updated Imports
import AnalysisTabs from "./components/AnalysisTabs";
import PredictiveMetricsCard from "./components/PredictiveMetricsCard"; // RENAMED COMPONENT
import RepoForm from "./components/RepoForm";
import PylintBadge from "./components/PylintBadge";
import Header from "./components/Header";
import ComplexityChart from "./components/ComplexityChart";

import "./App.css";
import "./components.css";

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeRepo = async (repoUrl) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      if (!res.ok) {
        // Attempt to read the error detail from the response body if available
        const errorData = await res
          .json()
          .catch(() => ({ detail: res.statusText }));
        throw new Error(
          `Analysis failed: ${errorData.detail || res.statusText}`
        );
      }

      const data = await res.json();
      // The `data.results` object now contains:
      // - code_health_score
      // - ai_metrics
      // - historical_risk_score
      // - git_sha
      setResults(data.results);
    } catch (err) {
      setError(err.message);
      console.error("Analysis error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />

      <main className="app-main">
        <RepoForm onAnalyze={analyzeRepo} />

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Analyzing repository and calculating predictive scores...</p>
            <p className="loading-subtext">This may take a moment</p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <i className="error-icon">⚠️</i>
            <h3>Analysis Failed</h3>
            <p>{error}</p>
            <button className="retry-button" onClick={() => setError(null)}>
              Try Again
            </button>
          </div>
        )}

        {/* Display results only when available and not loading */}
        {results && !loading && (
          <div className="results-container">
            <div className="results-header">
              {/* Display main CHS score (optional, but Pylint is good secondary metric) */}
              <h2>Analysis Results</h2>
              <div className="results-badges">
                <PylintBadge score={results?.pylint?.score || 0} />
              </div>
            </div>

            <div className="results-grid">
              <div className="main-results">
                {/* 1. Predictive Metrics Card (Sidebar) */}
                <PredictiveMetricsCard results={results} />

                {/* 2. Complexity Chart (Sidebar) - Kept it here for better grouping */}
                <ComplexityChart radon={results.radon} />
              </div>

              {/* Static Analysis Tabs (Main Content Area) */}
              <div className="sidebar-results">
                <AnalysisTabs results={results} />
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>DevPulse • Predictive Technical Debt Analysis</p>
      </footer>
    </div>
  );
}

export default App;
