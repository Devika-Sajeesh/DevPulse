import { useState } from "react";

export default function RepoForm({ onAnalyze }) {
  const [repoUrl, setRepoUrl] = useState("");
  const [isValidUrl, setIsValidUrl] = useState(true);

  const validateUrl = (url) => {
    const githubRegex =
      /^(https?:\/\/)?(www\.)?github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+(\/)?$/;
    return githubRegex.test(url);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateUrl(repoUrl)) {
      setIsValidUrl(false);
      return;
    }

    setIsValidUrl(true);
    onAnalyze(repoUrl);
  };

  return (
    <form className="repo-form" onSubmit={handleSubmit}>
      <div className="input-container">
        <i className="fab fa-github input-icon"></i>
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => {
            setRepoUrl(e.target.value);
            if (!isValidUrl) setIsValidUrl(true);
          }}
          placeholder="https://github.com/username/repository"
          required
          className={!isValidUrl ? "input-error" : ""}
        />
        <button type="submit" className="analyze-button">
          <i className="fas fa-search"></i>
          Analyze
        </button>
      </div>
      {!isValidUrl && (
        <p className="error-message">
          Please enter a valid GitHub repository URL
        </p>
      )}
    </form>
  );
}
