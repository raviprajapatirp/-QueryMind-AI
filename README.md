# 🧠 QueryMind AI

**Chat with your data. Instantly.**

QueryMind AI is a Streamlit web app that lets you upload a CSV/Excel/SQLite file
(or connect to a live MySQL/PostgreSQL database), then ask questions in plain
English. It auto-detects your schema, generates and runs SQL, builds an
executive dashboard, offers 20 chart types, automatic data cleaning, EDA,
AI-generated business insights, and PDF/CSV/Excel/SQL export — all behind a
simple username/password login.

---

## ✨ Features

| Area | What's included |
|---|---|
| **Data sources** | CSV, Excel (.xlsx), SQLite (.db), live MySQL, live PostgreSQL |
| **Schema detection** | Tables, columns, types, primary keys, foreign keys — automatic |
| **AI Chat** | English → SQL, follow-up-aware conversation, auto-execution of results |
| **SQL Generator** | English→SQL, SQL→English, explain, optimize, fix errors, format |
| **SQL Executor** | Safe execution (blocks destructive statements by default), export results |
| **Dashboard** | KPI cards, interactive date/category filters, auto-selected charts |
| **Charts** | Bar, Line, Pie, Donut, Scatter, Histogram, Box, Violin, Heatmap, Correlation Matrix, Area, Treemap, Sunburst, Waterfall, Bubble, Funnel, Geo Map, Time Series, Distribution, Pair Plot |
| **Data Cleaning** | Remove duplicates, fill/drop nulls, convert types, rename, normalize text, outlier removal |
| **Data Analysis** | Stats summary, correlation, missing-value report, duplicate finder, Isolation-Forest outliers, trend detection, category breakdown, feature importance |
| **AI Insights** | LLM-generated narrative business insights from your data's statistical profile |
| **History** | Persistent query history and starred/saved queries per user |
| **Reports** | One-click PDF report (KPIs + stats + AI insights), plus CSV/Excel/SQL/PNG export |
| **Auth** | Signup/login/forgot-password with salted+hashed passwords (local SQLite) |
| **UI** | Dark/light theme toggle, glassmorphism cards, gradient KPIs, searchable sidebar nav |

## 🧠 AI Model

Powered by the [Groq API](https://console.groq.com) (Llama 3.3, Llama 3.1, Gemma 2 — selectable
in the sidebar). AI-dependent features (Chat, SQL Generator's English↔SQL/explain/optimize/fix,
AI Insights, and the "include insights" option in Reports) require a `GROQ_API_KEY`; every other
feature works with no API key at all.

---

## 🚀 Quickstart (local)

```bash
git clone <your-repo-url> QueryMind-AI
cd QueryMind-AI
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste your GROQ_API_KEY

streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`). Sign up with any
username/password (this is a local demo auth store — see **Security notes** below), then
head to **📂 Upload Data** and try `sample_data/sample_sales.csv`, or ask the AI Chat:

- "Show top 10 customers by revenue"
- "Which product category has the highest profit margin?"
- "Monthly sales trend for 2024"
- "Find duplicate records"
- "Show missing values"

## ☁️ Deploying to Streamlit Community Cloud

1. Push this repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing at `app.py`.
3. In the app's **Settings → Secrets**, paste the contents of `.streamlit/secrets.toml.example`
   with your real `GROQ_API_KEY` filled in.
4. Deploy. `requirements.txt` and `.streamlit/config.toml` (theme) are picked up automatically.

> **Note on live databases:** MySQL/PostgreSQL connections from Streamlit Cloud require your
> database to accept inbound connections from Streamlit's IPs (or use a tunneling/proxy service).
> CSV/Excel/SQLite work with zero extra configuration anywhere.

---

## 📁 Project Structure

```
QueryMind-AI/
├── app.py                  # Main Streamlit entry point — all pages/navigation
├── config.py               # Theme, constants, secrets loading
├── database.py             # Connection engines + schema introspection + safe execution
├── ai_engine.py             # Groq client wrapper, insight generation
├── sql_generator.py        # NL→SQL, explain, optimize, fix, format
├── dashboard.py            # KPI cards, filters, auto-charts
├── charts.py               # 20 reusable Plotly chart builders
├── analysis.py             # EDA: stats, correlation, outliers, trends, feature importance
├── cleaning.py             # One-click data cleaning operations
├── report_generator.py     # CSV/Excel/SQL/PDF/PNG export
├── authentication.py       # Signup/login/forgot-password (salted+hashed, local SQLite)
├── history.py              # Query history + saved queries (persisted, per-user)
├── utils.py                # Session state, CSS theme injection, helpers
├── requirements.txt
├── .env.example
├── .streamlit/
│   ├── config.toml         # Native Streamlit theme (dark)
│   └── secrets.toml.example
├── sample_data/
│   └── sample_sales.csv    # Ready-to-use demo dataset (6,000 rows)
└── assets/
```

Two SQLite files are created automatically on first run (both git-ignored, local-only):
`users.db` (accounts) and `app_state.db` (query history / saved queries).

---

## 🔒 Security notes

- Passwords are salted and hashed with PBKDF2-HMAC-SHA256 (200,000 iterations) — never stored in plaintext.
- All SQL runs through parameterized `SQLAlchemy text()` execution; the SQL Executor blocks
  destructive keywords (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `UPDATE`, `INSERT`, etc.) and
  multi-statement queries unless you explicitly enable "Allow write statements."
- Secrets are read from `st.secrets` (Streamlit Cloud) first, then environment variables — never hardcoded.
- **This auth system is intended for demos/portfolios.** For a real production deployment with
  sensitive data, replace it with a managed identity provider and put the app behind HTTPS.

## 🛠 Tech Stack

Streamlit · Pandas · NumPy · SQLAlchemy · PyMySQL · psycopg2 · SQLite3 · Plotly · Matplotlib ·
scikit-learn · Groq · OpenPyXL · ReportLab · python-dotenv · sqlparse · kaleido

## 📄 License

Provided as-is for personal/portfolio use. Review and adapt the security notes above before
handling real or sensitive data.
