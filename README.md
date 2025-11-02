# 🚀 DevPulse – AI-Powered Predictive Code Health & Technical Debt Engine

<div align="center">

![DevPulse Banner](https://img.shields.io/badge/DevPulse-Predictive_Analytics-6366f1?style=for-the-badge)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)

**Transform code analysis with machine learning predictions and AI insights**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API Docs](#-api-documentation) • [Troubleshooting](#-troubleshooting)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

DevPulse is a **full-stack predictive code analysis platform** that goes beyond traditional static analysis. It uses machine learning and AI to predict future technical debt, assess code maintainability risks, and detect AI-generated code patterns.

### The DevPulse Difference

Unlike traditional code analysis tools that only report current issues, DevPulse:
- **Predicts future technical debt** using ML models trained on historical data
- **Detects AI-generated code** that may introduce maintenance risks
- **Provides actionable insights** through AI-powered recommendations
- **Combines multiple metrics** into a single Code Health Score (CHS)

### Core Metrics

| Metric | Description | Impact |
|--------|-------------|--------|
| **Code Health Score (CHS)** | Single objective score (0-100) for overall code quality | Main decision metric |
| **AI Code Probability** | Likelihood that code was AI-generated (0-100%) | Penalty factor |
| **Historical Risk Score** | ML-predicted future technical debt risk (0-100%) | Penalty factor |
| **Static Analysis** | Traditional metrics (Pylint, Radon, CLOC) | Base score component |

---

## ✨ Features

### 🔮 Predictive Analytics
- **ML-Powered Risk Prediction**: Scikit-learn Linear Regression model predicts future technical debt
- **AI Code Detection**: LLM-based analysis identifies AI-generated code patterns
- **Trend Analysis**: Historical data tracking for long-term code health monitoring

### 🛡️ Security & Isolation
- **Docker Sandboxing**: All third-party repository analysis runs in isolated containers
- **Zero Host Exposure**: Malicious code cannot compromise the host system
- **Read-Only Mounts**: Analyzed code has no write permissions

### 📊 Comprehensive Analysis
- **Cyclomatic Complexity**: Radon-based complexity metrics
- **Code Statistics**: CLOC for lines of code, comments, and blanks
- **Quality Scoring**: Pylint for code quality assessment
- **AI Insights**: GPT/Groq-powered recommendations

### 🎨 Modern UI/UX
- **Interactive Dashboard**: Real-time visualizations with Recharts
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode Support**: Automatic theme detection
- **Premium Aesthetics**: Gradient designs and smooth animations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface (React)                      │
│                    http://localhost:3000                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Docker)                       │
│                    http://localhost:8000                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Repository Cloning (GitPython)                        │   │
│  │  • ML Model Loading (Scikit-learn)                       │   │
│  │  • Database (SQLite)                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│           Analysis Sandbox (Ephemeral Docker Container)          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Radon (Complexity Analysis)                           │   │
│  │  • CLOC (Code Statistics)                                │   │
│  │  • Pylint (Quality Assessment)                           │   │
│  │  ✓ Isolated Execution                                    │   │
│  │  ✓ No Network Access                                     │   │
│  │  ✓ Read-Only File System                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External AI Services                          │
│              (Groq/OpenAI for AI Analysis)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- Scikit-learn (ML predictions)
- Docker SDK (Container orchestration)
- SQLite (Data persistence)
- GitPython (Repository handling)

**Frontend:**
- React 19
- Recharts (Visualizations)
- Axios (HTTP client)
- Framer Motion (Animations)

**Analysis Tools:**
- Radon (Complexity metrics)
- CLOC (Code statistics)
- Pylint (Quality scoring)
- Groq/OpenAI (AI insights)

---

## 📦 Prerequisites

### Required Software

- **Docker Desktop** (v20.10+)
  - [Windows/Mac Download](https://www.docker.com/products/docker-desktop)
  - Must be running and stable
  
- **Node.js** (v18+)
  - [Download](https://nodejs.org/)
  - Required for React frontend development
  
- **Python** (v3.11+)
  - [Download](https://www.python.org/)
  - Required for ML model training

### API Keys

You need at least **one** of these AI service keys:

- **Groq API Key** (Recommended - Free tier available)
  - [Sign up at console.groq.com](https://console.groq.com)
  
- **OpenAI API Key** (Alternative)
  - [Sign up at platform.openai.com](https://platform.openai.com)

---

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/devpulse.git
cd devpulse
```

### Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
# Required: AI Service Keys (at least one)
GROQ_API_KEY=your_groq_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here

# Optional: Model Selection
AI_MODEL=llama-3.1-8b-instant  # For Groq
# AI_MODEL=gpt-4o-mini          # For OpenAI

# Optional: Docker Configuration
SANDBOX_IMAGE=devpulse-sandbox
```

### Step 3: Train ML Model

```bash
# Install dependencies
pip install -r requirements.txt

# Train and save the model
python ml/train_model.py
```

Expected output:
```
Starting ML Model Training...
ML Model trained and saved to: ml/historical_risk_model.joblib
Model coefficients (Weights): [0.5 -0.3 -0.2 -0.15]
```

### Step 4: Build Docker Containers

```bash
# Build the analysis sandbox image
docker build -f Dockerfile.sandbox -t devpulse-sandbox .

# Build and start all services
docker compose up --build -d
```

Wait for the containers to start:
```bash
docker compose ps
```

Expected output:
```
NAME                    STATUS          PORTS
devpulse_api            Up              0.0.0.0:8000->8000/tcp
```

### Step 5: Start Frontend Development Server

```bash
cd frontend
npm install
npm start
```

The application will open at **http://localhost:3000**

### Step 6: Analyze Your First Repository

1. Open http://localhost:3000 in your browser
2. Enter a GitHub repository URL (e.g., `https://github.com/username/repo`)
3. Click **Analyze**
4. Wait 1-2 minutes for the analysis to complete

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes* | - | Groq API key for AI analysis |
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key (alternative) |
| `AI_MODEL` | No | `llama-3.1-8b-instant` | AI model to use |
| `SANDBOX_IMAGE` | No | `devpulse-sandbox` | Docker sandbox image name |

*At least one AI service key is required

### Supported AI Models

**Groq Models:**
- `llama-3.1-8b-instant` (Recommended - Fast & Free)
- `mixtral-8x7b-32768` (High quality)

**OpenAI Models:**
- `gpt-4o-mini` (Recommended - Cost-effective)
- `gpt-4o` (Highest quality)

### Database Configuration

DevPulse uses SQLite by default. The database file `devpulse.db` is created automatically in the project root.

**Schema:**
```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_url TEXT,
    git_sha TEXT,
    timestamp TEXT,
    radon TEXT,
    cloc TEXT,
    pylint TEXT,
    ai_metrics TEXT,
    code_health_score REAL,
    historical_risk_score REAL
)
```

---

## 💻 Usage

### Analyzing a Repository

#### Via Web Interface

1. Navigate to http://localhost:3000
2. Enter a GitHub repository URL
3. Click "Analyze"
4. View comprehensive results including:
   - Code Health Score
   - AI Code Probability
   - Historical Risk Score
   - Detailed metrics and recommendations

#### Via API (cURL)

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/username/repo"}'
```

#### Via Python

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"repo_url": "https://github.com/username/repo"}
)

results = response.json()
print(f"Code Health Score: {results['results']['code_health_score']}")
```

### Viewing Past Reports

#### List All Reports

```bash
curl http://localhost:8000/reports
```

#### Get Specific Report

```bash
curl http://localhost:8000/reports/1
```

---

## 📚 API Documentation

### Endpoints

#### `POST /analyze`

Analyze a GitHub repository.

**Request:**
```json
{
  "repo_url": "https://github.com/username/repository"
}
```

**Response:**
```json
{
  "report_id": 1,
  "results": {
    "repo_url": "https://github.com/username/repository",
    "git_sha": "abc123...",
    "code_health_score": 75.5,
    "historical_risk_score": 0.25,
    "ai_metrics": {
      "ai_probability": 0.15,
      "ai_risk_notes": "Low AI generation probability",
      "recommendations": ["Improve documentation", "Reduce complexity"]
    },
    "radon": { /* complexity data */ },
    "cloc": { /* code statistics */ },
    "pylint": { /* quality metrics */ }
  }
}
```

#### `GET /reports`

List all analysis reports.

**Response:**
```json
[
  {
    "id": 1,
    "repo_url": "https://github.com/username/repo",
    "git_sha": "abc123...",
    "timestamp": "2025-11-02T10:30:00"
  }
]
```

#### `GET /reports/{report_id}`

Get a specific report by ID.

**Response:** Same as POST /analyze results

#### `GET /status`

Health check endpoint.

**Response:**
```json
{
  "message": "Analysis complete"
}
```

#### `GET /debug-tools`

Test analysis tools (development only).

**Response:**
```json
{
  "radon": {
    "status": "success",
    "output_length": 1234
  },
  "cloc": { /* ... */ },
  "pylint": { /* ... */ }
}
```

### Interactive API Docs

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🛠️ Development

### Project Structure

```
devpulse/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── analyzer.py         # Core analysis orchestration
│   │   ├── ai_summary.py       # AI-powered insights
│   │   ├── predictor.py        # ML predictions
│   │   └── db_service.py       # Database operations
│   └── utils/
│       ├── radon_parser.py     # Radon output parser
│       ├── cloc_parser.py      # CLOC output parser
│       ├── pylint_parser.py    # Pylint output parser
│       └── repo_downloader.py  # Git repository handler
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main application
│   │   ├── components/         # React components
│   │   └── api/                # API client
│   └── public/
├── ml/
│   └── train_model.py          # ML model training
├── Dockerfile                  # Main API container
├── Dockerfile.sandbox          # Analysis sandbox container
├── docker-compose.yml          # Multi-container orchestration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Running Tests

```bash
# Backend tests (from project root)
pytest backend/tests/

# Frontend tests
cd frontend
npm test
```

### Development Workflow

1. **Backend Development**
   ```bash
   # Start only the backend
   docker compose up devpulse-api
   
   # Or run locally for faster iteration
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm start
   ```

3. **Rebuild After Changes**
   ```bash
   # Rebuild specific service
   docker compose up --build devpulse-api
   
   # Rebuild all
   docker compose up --build
   ```

### Adding New Analysis Tools

1. Install the tool in `Dockerfile.sandbox`
2. Add command execution in `analyzer.py`
3. Create a parser in `backend/utils/`
4. Update the ML feature extraction if needed

---

## 🐛 Troubleshooting

### Common Issues

#### Docker Container Won't Start

**Symptom:** Container exits immediately or won't start

**Solutions:**
```bash
# Check logs
docker logs devpulse_api

# Verify Docker is running
docker ps

# Rebuild from scratch
docker compose down
docker system prune -a
docker compose up --build
```

#### Analysis Returns Empty Results

**Symptom:** Code Health Score is 0 or data is missing

**Solutions:**
```bash
# Check if sandbox image exists
docker images | grep devpulse-sandbox

# Rebuild sandbox image
docker build -f Dockerfile.sandbox -t devpulse-sandbox .

# Test tools manually
docker exec -it devpulse_api python -c "
from backend.services.analyzer import run_sandboxed_command
import asyncio
result = asyncio.run(run_sandboxed_command('radon', '--version', repo_path='/tmp'))
print(result)
"
```

#### AI Metrics Not Generated

**Symptom:** `ai_metrics` is null or empty

**Solutions:**
1. Verify API key in `.env` file
2. Check API quota/limits
3. Review logs for API errors:
   ```bash
   docker logs devpulse_api | grep "AI metrics"
   ```

#### Frontend Can't Connect to Backend

**Symptom:** Network errors or CORS issues

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/status`
2. Check CORS configuration in `backend/main.py`
3. Ensure frontend is using correct API URL

#### ML Model Not Found

**Symptom:** `WARNING: ML Model not found at ml/historical_risk_model.joblib`

**Solution:**
```bash
python ml/train_model.py
```

### Debug Mode

Enable verbose logging:

```bash
# In docker-compose.yml, add:
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=DEBUG
```

### Getting Help

1. Check the [Troubleshooting Guide](#-troubleshooting)
2. Review Docker logs: `docker logs -f devpulse_api`
3. Open an issue on GitHub with:
   - Error messages
   - Docker logs
   - Browser console output (F12)
   - Steps to reproduce

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest backend/tests/ && cd frontend && npm test`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Follow Airbnb style guide, use Prettier
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

### Areas for Contribution

- [ ] Additional analysis tools (ESLint, SonarQube, etc.)
- [ ] More ML models (Random Forest, Neural Networks)
- [ ] Support for other version control systems (GitLab, Bitbucket)
- [ ] Advanced visualizations
- [ ] CI/CD integration
- [ ] Performance optimizations

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **Scikit-learn** - Machine learning library
- **React** - UI framework
- **Docker** - Containerization platform
- **Radon, CLOC, Pylint** - Analysis tools

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/devpulse/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/devpulse/discussions)
- **Email**: support@devpulse.io

---

<div align="center">

**Built with ❤️ by developers, for developers**

[⭐ Star us on GitHub](https://github.com/yourusername/devpulse) | [🐦 Follow on Twitter](https://twitter.com/devpulse)

</div>