import { useState } from "react";

import AnalysisTabs from "./components/AnalysisTabs";
import AISummaryCard from "./components/AISummaryCard";
import RepoForm from "./components/RepoForm";
import PylintBadge from "./components/PylintBadge";
import Header from "./components/Header";
import ComplexityChart from "./components/ComplexityChart";

// Use these components in your main App component
import "./App.css";
import "./components.css"; // Import the new CSS file

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
        throw new Error(`Analysis failed: ${res.statusText}`);
      }

      const data = await res.json();
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
            <p>Analyzing repository...</p>
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

        {results && !loading && (
          <div className="results-container">
            <div className="results-header">
              <h2>Analysis Results</h2>
              <div className="results-badges">
                <div className="results-badges">
                  <PylintBadge score={results?.pylint?.score || 0} />
                </div>
              </div>
            </div>

            <div className="results-grid">
              <div className="main-results">
                <AnalysisTabs results={results} />
              </div>

              <div className="sidebar-results">
                <AISummaryCard summary={results?.ai_summary} />
                <ComplexityChart radon={results.radon} />
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>CodeInsight • Powered by AI Code Analysis</p>
      </footer>
    </div>
  );
}

export default App;
