export default function Header() {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="logo-container">
          <i className="fas fa-code-branch logo-icon"></i>
          <h1>DevPulse</h1>
        </div>
        <p className="header-subtitle">
          Static code analysis & AI insights dashboard
        </p>
      </div>
    </header>
  );
}
