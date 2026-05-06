# DocMind

An AI-powered document intelligence system. Upload a PDF or PPTX, ask questions about it in natural language, and generate a shareable NotebookLM notebook — all in one interface.

Built as a take-home assignment for the **AI Application Engineer** position at **瑞鼎科技 (RAD-IC)**, integrating all three tasks into a single deployable system.

---

## Task Coverage

| Task | Requirement | Implementation |
|---|---|---|
| Task 1 | Unstructured Data Pipeline & Remote MCP Server | Ingestion pipeline (parse → clean → chunk → embed) + FastMCP server exposing `search_knowledge` and `create_notebooklm` |
| Task 2 | Data Preprocessing as Claude Skills | `/parse-doc` `/clean-text` `/chunk-doc` `/build-kb` — Claude Code Skills sharing the same ingestion logic |
| Task 3 | Browser Automation Agent | Playwright automates NotebookLM to create a notebook from the uploaded document and returns a shareable URL |

---

## Features

| Feature | Description |
|---|---|
| Document Upload | Accepts PDF and PPTX; triggers background ingestion pipeline |
| Knowledge Base | Chunked document content embedded via Gemini and stored in Qdrant |
| AI Chat | Gemini Function Calling — automatically queries knowledge base or creates NotebookLM based on user intent |
| MCP Server | External agents can connect and call `search_knowledge` or `create_notebooklm` |
| NotebookLM | Playwright creates a notebook from the uploaded document and returns a public sharing link |

---

## Project Structure

```
docmind/
├── backend/
│   ├── main.py
│   ├── core/
│   ├── routers/
│   └── services/
│       ├── ingestion_pipeline/
│       ├── models/
│       ├── data/
│       ├── mcp/
│       │   └── tools/
│       └── chat/
├── frontend/
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

```bash
cp .env.example .env
# fill in GEMINI_API_KEY
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
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
