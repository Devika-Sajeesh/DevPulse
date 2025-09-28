# 🚀 DevPulse – Repository Analyzer & AI Code Insights

DevPulse is a **static code analysis dashboard** powered by Python, FastAPI, and React.  
It analyzes any GitHub repository for **complexity, maintainability, and code quality**, then provides **AI-generated insights**.

<p align="center">
  <img src="frontend/public/demo.png" alt="DevPulse Dashboard" width="700"/>
</p>

---

## ✨ Features

- 📊 **Static Analysis Integration**
  - [Radon](https://pypi.org/project/radon/) → Cyclomatic complexity
  - [Cloc](https://github.com/AlDanial/cloc) → Lines of code breakdown
  - [Pylint](https://pylint.pycqa.org/) → Code quality & issues  

- 🤖 **AI Insights**
  - Summarizes analyzer output into a concise report  
  - Highlights **complexity, quality, maintainability, and recommendations**  
  - Powered by **Groq / OpenAI** LLMs  

- 🎨 **Modern UI**
  - React dashboard with tabs (Radon, CLOC, Pylint)  
  - Markdown rendering with syntax highlighting  
  - Badges, charts, and expandable summaries  

- 💾 **Persistence**
  - Stores analysis reports in SQLite (extensible to Postgres)  

---

## 🏗️ Architecture

```
┌───────────────┐        ┌─────────────┐
│   React App   │  <-->  │   FastAPI   │
│ (frontend)    │        │  (backend)  │
└───────┬───────┘        └───────┬─────┘
        │                         │
        ▼                         ▼
   Analysis UI         Static Analysis Tools
                        (Radon, Cloc, Pylint)
                               │
                               ▼
                       🤖 AI Summary Service
                         (Groq / OpenAI)
```

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Devika-Sajeesh/devpulse.git
cd devpulse
```

### 2. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
```

Create a `.env` file:
```ini
# API Keys
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here

# Tools (adjust paths as needed)
RADON_PATH=radon
PYLINT_PATH=pylint
CLOC_PATH=cloc

# Model
AI_MODEL=llama-3.1-70b-versatile
```

Run FastAPI:
```bash
uvicorn backend.main:app --reload
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm start
```

Frontend → http://localhost:3000  
Backend → http://127.0.0.1:8000  

---

## 📌 Usage

1. Enter any public GitHub repo URL.  
2. Click **Analyze**.  
3. Wait for:
   - 📊 Radon complexity breakdown  
   - 📊 Cloc metrics  
   - 📊 Pylint report  
   - 🤖 AI summary of code health  

---

## 🧩 Example Output

**AI Summary**
```json
{
  "complexity": "Mostly simple functions, few hotspots.",
  "quality": "Consistent style but some linting issues.",
  "maintainability": "Good overall but refactor recommended.",
  "recommendations": [
    "Fix pylint warnings",
    "Reduce complexity in utils.py",
    "Add more docstrings"
  ]
}
```

---

## 🛠️ Tech Stack

- **Frontend**: React, React Markdown, Syntax Highlighter  
- **Backend**: FastAPI, Python 3.11+  
- **Static Analysis**: Radon, Cloc, Pylint  
- **Database**: SQLite (upgradeable)  
- **AI Layer**: Groq LLaMA 3.1 / OpenAI GPT models  

---

## 🚧 Roadmap

- [ ] Add support for **multi-repo history & comparisons**  
- [ ] Stream analysis results live to frontend  
- [ ] Add **Docker sandboxing** for repo analysis  
- [ ] CI/CD integration (GitHub Actions)  
- [ ] Postgres + Redis for scale  
- [ ] AI model fine-tuning for structured summaries  

---

## 👩‍💻 Author

Built by **[Devika Sajeesh](https://github.com/Devika-Sajeesh)**  
BTech ECE @ College of Engineering Trivandrum  
