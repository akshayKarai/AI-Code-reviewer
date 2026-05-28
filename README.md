# 🔍 CodeSage — AI Code Reviewer

> **Instant AI-powered code review — bugs, security, performance & style**
> Built with FastAPI · Claude AI · Streamlit

---

## 📸 Overview

CodeSage is a full-stack **AI Code Reviewer** that analyses any code snippet and returns structured, actionable feedback. Paste your code, choose your focus areas, and get back a quality score, categorised issues with line references, fix suggestions, and even a refactored snippet — all powered by Anthropic's Claude AI.

```
User pastes code
       │
       ▼
  Language detection (auto or manual)
       │
       ▼
  Structured prompt sent to Claude claude-sonnet-4-20250514
       │
       ▼
  Claude returns JSON: score, issues, positives, refactor
       │
       ▼
  FastAPI validates & normalises response
       │
       ▼
  Streamlit renders:
    ├── Quality score (0–100)
    ├── Issue cards (Critical / Major / Minor / Suggestion)
    ├── Positive aspects
    └── Optional refactored snippet
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Quality Score** | 0–100 rating with colour-coded feedback |
| **Issue Detection** | Bugs, security flaws, performance problems, style issues, best practice violations |
| **Severity Levels** | 🔴 Critical · 🟠 Major · 🟡 Minor · 🔵 Suggestion |
| **Line References** | Issues include exact line numbers where possible |
| **Fix Suggestions** | Every issue comes with a concrete how-to-fix |
| **Refactored Snippet** | Claude rewrites the worst section of code for you |
| **Positive Aspects** | Highlights what you did well — not just problems |
| **Code Explainer** | Plain-English explanation of what any code does |
| **16 Languages** | Python, JS, TS, Java, Go, Rust, C++, SQL, and more |
| **REST API** | Full FastAPI backend with Swagger docs at `/docs` |
| **Built-in Examples** | 4 ready-to-use examples (bad + good code) |

---

## 🏗️ Project Structure

```
ai-code-reviewer/
├── backend/
│   ├── main.py          # FastAPI routes: /review, /explain, /health, /languages
│   ├── reviewer.py      # Core engine: prompt building, Claude API, JSON parsing
│   └── requirements.txt
│
├── frontend/
│   ├── app.py           # Streamlit UI: review tab, explain tab, examples tab
│   └── requirements.txt
│
├── examples/
│   ├── bad_python_example.py   # Intentionally flawed code (SQL injection, weak crypto…)
│   └── good_python_example.py  # Clean, idiomatic Python for comparison
│
├── scripts/
│   └── start.sh         # One-command launcher for both services
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-code-reviewer.git
cd ai-code-reviewer
```

### 2. Set your Anthropic API key

```bash
cp .env.example .env
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> Get your key at [https://console.anthropic.com](https://console.anthropic.com)

### 3. Launch everything

```bash
bash scripts/start.sh
```

| Service | URL |
|---|---|
| Streamlit UI | http://localhost:8501 |
| FastAPI backend | http://localhost:8000 |
| Swagger API docs | http://localhost:8000/docs |

---

## 🔧 Manual Setup (Alternative)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

---

## 📖 How to Use

### Code Review
1. Open http://localhost:8501
2. Paste any code in the editor
3. Select language and focus areas in the sidebar
4. Click **Review Code**
5. Get your score, issues, and fixes

### Code Explainer
1. Switch to the **💡 Explain Code** tab
2. Paste code you want explained
3. Click **Explain This Code**
4. Read the plain-English breakdown

### Try the Examples
- Switch to the **📂 Examples** tab
- Pick a sample snippet (vulnerable code, clean code, etc.)
- Copy it to the Review tab and hit **Review Code**

---

## 🔌 API Reference

### `GET /health`
```json
{ "status": "healthy", "model": "claude-sonnet-4-20250514" }
```

### `GET /languages`
```json
{ "languages": ["python", "javascript", "typescript", ...] }
```

### `POST /review`
```json
// Request
{
  "code": "def login(user, pwd):\n    ...",
  "language": "python",
  "focus": ["bugs", "security", "performance"],
  "severity_filter": "all"
}

// Response
{
  "language": "python",
  "overall_score": 42,
  "summary": "The code has critical security vulnerabilities...",
  "issues": [
    {
      "severity": "critical",
      "category": "security",
      "line": "5",
      "title": "SQL Injection Vulnerability",
      "description": "String concatenation used to build SQL query.",
      "suggestion": "Use parameterised queries: cursor.execute('SELECT * FROM users WHERE username = ?', (username,))"
    }
  ],
  "positive_aspects": ["Function is logically structured"],
  "refactored_snippet": "def login(user, pwd):\n    ...",
  "stats": {
    "total_issues": 3, "critical": 1, "major": 1,
    "minor": 1, "suggestions": 0, "lines_of_code": 12, "characters": 340
  }
}
```

### `POST /explain`
```json
// Request
{ "code": "...", "language": "auto" }

// Response
{ "explanation": "This function authenticates a user by...", "language": "python" }
```

---

## 🧱 Technical Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | Anthropic Claude (`claude-sonnet-4-20250514`) | Code analysis & generation |
| **API** | FastAPI + Uvicorn | High-performance REST backend |
| **Validation** | Pydantic v2 | Request/response schemas |
| **UI** | Streamlit | Interactive code editor + results dashboard |
| **Prompt Engineering** | Structured JSON prompts | Consistent, parseable Claude output |

---

## ⚙️ Configuration

Key parameters in `backend/reviewer.py`:

| Parameter | Default | Description |
|---|---|---|
| `model` | `claude-sonnet-4-20250514` | Claude model used |
| `max_tokens` (review) | `2048` | Max tokens for review response |
| `max_tokens` (explain) | `800` | Max tokens for explanation |
| Code limit | `20,000 chars` | Max code size per request |

Adjustable in `backend/main.py`:
- `severity_filter`: filter issues by minimum severity (`all` / `critical` / `major`)
- `focus`: select which categories Claude analyses

---

## 🔮 Potential Extensions

- **GitHub PR Integration**: Trigger reviews automatically on pull requests via webhooks
- **VS Code Extension**: Run reviews inline inside the editor
- **Diff Review**: Compare before/after and review only changed lines
- **History & Trends**: Store past reviews and track code quality over time
- **Multi-file Review**: Upload a full project and get cross-file analysis
- **Custom Rules**: Define team-specific coding standards for Claude to enforce
- **CI/CD Plugin**: Block merges if code scores below a threshold

---

## 🤝 Skills Demonstrated

This project showcases:

- ✅ **Prompt engineering** — structured JSON prompts for consistent LLM output
- ✅ **LLM integration** — Anthropic Python SDK with error handling & JSON parsing
- ✅ **REST API design** — FastAPI with typed Pydantic models and OpenAPI docs
- ✅ **Full-stack development** — decoupled backend + Streamlit frontend
- ✅ **Code quality analysis** — multi-dimensional review (security, perf, style)
- ✅ **Production patterns** — input validation, error handling, response normalisation
- ✅ **UX design** — IDE-themed dark UI with colour-coded severity system

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with ❤️ using Anthropic Claude, FastAPI, and Streamlit*
