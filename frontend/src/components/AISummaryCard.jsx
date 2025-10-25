import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

export default function AISummaryCard({ summary }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!summary) return null;

  const safeSummary =
    typeof summary === "string"
      ? summary
      : summary
      ? JSON.stringify(summary, null, 2)
      : "No summary available";

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const wordCount = safeSummary.split(/\s+/).length;
  const needsExpand = wordCount > 100;

  return (
    <div className="ai-summary-card">
      <div className="ai-summary-header">
        <div className="ai-summary-title">
          <i className="fas fa-robot"></i>
          <h3>AI Code Analysis Summary</h3>
        </div>
        <div className="ai-summary-actions">
          {needsExpand && (
            <button
              className="expand-button"
              onClick={toggleExpanded}
              aria-label={isExpanded ? "Collapse summary" : "Expand summary"}
            >
              <i
                className={`fas ${isExpanded ? "fa-compress" : "fa-expand"}`}
              ></i>
            </button>
          )}
        </div>
      </div>

      <div className={`ai-summary-content ${isExpanded ? "expanded" : ""}`}>
        <ReactMarkdown
          children={safeSummary}
          components={{
            h1: ({ ...props }) => (
              <h1 className="md-heading md-h1" {...props} />
            ),
            h2: ({ ...props }) => (
              <h2 className="md-heading md-h2" {...props} />
            ),
            h3: ({ ...props }) => (
              <h3 className="md-heading md-h3" {...props} />
            ),
            h4: ({ ...props }) => (
              <h4 className="md-heading md-h4" {...props} />
            ),
            p: ({ ...props }) => <p className="md-paragraph" {...props} />,
            ul: ({ ...props }) => <ul className="md-list" {...props} />,
            ol: ({ ...props }) => <ol className="md-list" {...props} />,
            li: ({ ...props }) => <li className="md-list-item" {...props} />,
            strong: ({ ...props }) => (
              <strong className="md-strong" {...props} />
            ),
            em: ({ ...props }) => <em className="md-emphasis" {...props} />,
            blockquote: ({ ...props }) => (
              <blockquote className="md-blockquote" {...props} />
            ),
            a: ({ ...props }) => <a className="md-link" {...props} />,
            table: ({ ...props }) => (
              <div className="table-container">
                <table className="md-table" {...props} />
              </div>
            ),
            thead: ({ ...props }) => (
              <thead className="md-table-header" {...props} />
            ),
            th: ({ ...props }) => <th className="md-table-header" {...props} />,
            td: ({ ...props }) => <td className="md-table-cell" {...props} />,
            code: ({ inline, className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || "");
              const language = match ? match[1] : "";
              return !inline && language ? (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={language}
                  PreTag="div"
                  className="code-block"
                  {...props}
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              ) : (
                <code className="inline-code" {...props}>
                  {children}
                </code>
              );
            },
          }}
        />
        {needsExpand && !isExpanded && (
          <div className="summary-preview-overlay"></div>
        )}
      </div>

      <div className="ai-summary-footer">
        <div className="ai-tag">
          <i className="fas fa-brain"></i>
          AI-Powered Analysis
        </div>
      </div>
    </div>
  );
}
