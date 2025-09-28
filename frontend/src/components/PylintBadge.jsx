export default function PylintBadge({ score }) {
  let color, rating;

  if (score >= 9) {
    color = "#10b981"; // Green
    rating = "Excellent";
  } else if (score >= 7) {
    color = "#f59e0b"; // Orange
    rating = "Good";
  } else if (score >= 5) {
    color = "#f97316"; // Amber
    rating = "Fair";
  } else {
    color = "#ef4444"; // Red
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
