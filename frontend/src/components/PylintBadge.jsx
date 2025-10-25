export default function PylintBadge({ score }) {
  let color, rating;

  if (score >= 9) {
    color = "var(--secondary)";
    rating = "Excellent";
  } else if (score >= 7) {
    color = "var(--warning)";
    rating = "Good";
  } else if (score >= 5) {
    color = "#f97316";
    rating = "Fair";
  } else {
    color = "var(--danger)";
    rating = "Poor";
  }

  return (
    <div className="pylint-badge">
      <div className="badge-icon">
        <i className="fas fa-shield-alt"></i>
      </div>
      <div className="badge-content">
        <span className="badge-title">Code Quality</span>
        <span className="badge-score" style={{ color }}>
          {score.toFixed(2)}/10
        </span>
        <span className="badge-rating">{rating}</span>
      </div>
    </div>
  );
}
