# Interview Practice

An AI-powered document Q&A system. Upload a personal PDF, ask questions about it in natural language, and generate a shareable NotebookLM notebook — all in one interface.

Built as a take-home assignment for the **AI Application Engineer** position at **瑞鼎科技 (RAD-IC)**, integrating all three tasks into a single deployable system.

---

## Task Coverage

| Task | Requirement | Implementation |
|---|---|---|
| Task 1 | Unstructured Data Pipeline & Remote MCP Server | PDF ingestion pipeline (parse → clean → chunk → embed) + FastMCP server exposing `search_knowledge` and `create_notebooklm` |
| Task 2 | Data Preprocessing as Claude Skills | `/parse-doc` `/clean-text` `/chunk-doc` `/build-kb` — Claude Code Skills defined in `.claude/commands/`, sharing the same ingestion logic as the backend pipeline |
| Task 3 | Browser Automation Agent | Playwright automates NotebookLM via Edge persistent context; implemented in `backend/services/mcp/tools/notebooklm/` and exposed as an MCP tool + chat intent |

---

## Features

| Feature | Description |
|---|---|
| Document Upload | Accepts PDF; replaces previous file and resets Qdrant — system always holds exactly one document |
| Knowledge Base | Chunked content embedded via gemini-embedding-001 (3072-dim) and stored in Qdrant |
| AI Chat | Gemini ReAct agent — queries knowledge base or creates NotebookLM based on user intent |
| Task Cancellation | Stop button (■) during execution calls `POST /cancel` + AbortController to interrupt mid-task |
| MCP Server | External agents can connect and call `search_knowledge` or `create_notebooklm` |
| NotebookLM | Playwright automates Edge to create a notebook from the uploaded PDF and returns a shareable link |

---

## Project Structure

```
interview-practice-rad/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── core/
│   ├── routers/
│   └── services/
│       ├── ingestion_pipeline/
│       ├── models/
│       ├── data/
│       ├── mcp/
│       │   └── tools/
│       │       ├── notebooklm/     # agent.py + browser.py + browser.json + prompt_browser.md
│       │       └── *.json          # MCP tool schemas
│       └── chat/
│           ├── tools/              # load_tools() reads mcp/tools/*.json
│           └── prompts/            # prompt_system.md + prompt_react.md
├── frontend/
├── .claude/
│   └── commands/               # Task 2 — Claude Code Skills
│       ├── parse-doc.md
│       ├── clean-text.md
│       ├── chunk-doc.md
│       └── build-kb.md
├── tools/
│   ├── generate_pdf.py         # helper to generate a sample PDF for testing
│   └── sample.pdf
├── docs/
│   ├── 01-backend.md
│   └── 02-frontend.md
├── .env.example
└── README.md
```

---

## Setup

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.12+ |
| Node.js | 20+ |
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/) |

### Environment Variables

Copy the template and fill in the values:

```bash
cp .env.example .env
```

Each variable in `.env.example` has an inline description. Remove the `.example` suffix when done.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
playwright install msedge
python main.py
```

API: `http://127.0.0.1:8000` · Swagger: `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: `http://localhost:5173`

---

## Contact

Yu-Cheng Kuo · s74101234@gmail.com
