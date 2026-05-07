# 01. 後端設計

> 最後更新：2026-05-07

---

## 第一部分：任務說明

> **Task 1 — Unstructured Data Pipeline & Remote MCP Server**
>
> Build a data processing pipeline that ingests simulated, messy enterprise documents (e.g., a multi-page PDF containing tables/headers, and a PPTX slide deck). The script must extract, clean, and appropriately chunk the content. Next, package this searchable knowledge base into a remote Model Context Protocol (MCP) server. Expose specific tools or resources via the MCP server so that a standard LLM agent can connect and query the extracted information.

> **Task 2 — Data Preprocessing as Claude Skills**
>
> Package the unstructured data preprocessing capabilities (like parsing PDFs or PPTX files, cleaning text, and structured formatting) into reusable Skills. Ensure that these Skills have clear inputs/outputs, a safe execution boundary, and can be easily installed and invoked by Claude Code.

> **Task 3 — Browser Automation Agent**
>
> Build an agent that can reliably drive a browser workflow (e.g., generating a slide deck via NotebookLM, or another general browser task), and provide verifiable outputs plus run logs.

**Interview Practice** 整合以上三項任務為單一系統。

---

## 第二部分：情境與功能

### 應用情境

使用者上傳個人 PDF 文件（履歷、作品集、個人網站匯出），系統建立向量知識庫。透過聊天介面與 Gemini 對話，ReAct agent 自動判斷是查詢知識庫或建立 NotebookLM 筆記本。

```
上傳 PDF
    ↓
Extract → Clean → Chunk → Gemini Embedding → Qdrant
    ↓
使用者輸入問題
    ↓
Gemini ReAct Agent
   ├── search_knowledge  → 搜尋知識庫 → 彙整回答
   └── create_notebooklm → Playwright → NotebookLM URL
```

**對話範例**：
- 「作者有哪些技術能力？」→ 搜尋知識庫後回答
- 「這個系統有什麼功能？」→ 直接回答，不呼叫工具
- 「幫我建立 NotebookLM 筆記本」→ Playwright 建立並回傳連結

### 功能清單

| 功能 | 說明 |
|---|---|
| 文件上傳 | 接收 PDF，觸發背景處理 pipeline |
| 處理進度 | SSE 即時回報各階段進度 |
| 聊天問答 | Gemini ReAct agent 根據知識庫內容回答問題 |
| 建立 NotebookLM | 使用者要求時，Playwright 自動操作並回傳可分享連結 |
| MCP Server | 兩個工具供外部 Agent 連線查詢 |
| Claude Skills | 前處理四步驟包裝為 Claude Code 可呼叫的介面 |

---

## 第三部分：技術棧

| 層次 | 技術 | 說明 |
|---|---|---|
| 後端框架 | FastAPI + Uvicorn（Python 3.12+）| |
| LLM | Gemini API（gemini-2.5-flash）| 聊天推論，ReAct JSON 輸出 |
| Embedding | Gemini API（gemini-embedding-001，3072-dim）| 向量化，批次 100 |
| 向量資料庫 | Qdrant（local path 模式）| |
| PDF 解析 | pymupdf4llm | PDF → Markdown，保留表格結構 |
| MCP | FastMCP | 掛載於 FastAPI `/mcp` |
| 瀏覽器自動化 | Playwright + Edge persistent context | 免重新登入操作 NotebookLM |
| 即時狀態 | SSE（Server-Sent Events）| |

---

## 第四部分：目錄結構

```
backend/
├── main.py                          FastAPI app，掛載 MCP
├── core/
│   ├── app_state.py                 全域狀態（uploaded_file_path, last_filename）
│   └── config.py                    環境變數（Pydantic Settings）
├── routers/
│   ├── upload.py                    文件上傳與觸發 pipeline
│   ├── chat.py                      聊天介面
│   └── status.py                    SSE 進度推播
└── services/
    ├── ingestion_pipeline/
    │   ├── parser.py                pymupdf4llm，PDF → Markdown
    │   ├── cleaner.py
    │   └── chunker.py
    ├── models/
    │   ├── embedder.py              gemini-embedding-001，3072-dim
    │   └── gemini.py               gemini-2.5-flash，內建 retry
    ├── data/
    │   └── store.py                Qdrant upsert / query_points / scroll_all
    ├── mcp/
    │   ├── server.py               FastMCP，掛載兩個工具
    │   └── tools/
    │       ├── search_knowledge.py  向量搜尋實作
    │       ├── search_knowledge.json  工具 JSON Schema
    │       ├── notebooklm.py        Playwright 瀏覽器自動化
    │       └── notebooklm.json      工具 JSON Schema
    └── chat/
        ├── chat_agent.py            ReAct 推理迴圈
        ├── tools/
        │   └── __init__.py          load_tools()，讀取 mcp/tools/*.json
        └── prompts/
            ├── prompt_system.md     系統身份描述（靜態）
            └── prompt_react.md      ReAct 框架指令（含佔位符）

task2/.claude/commands/              Claude Code Skills
├── parse-doc.md
├── clean-text.md
├── chunk-doc.md
└── build-kb.md
```

---

## 第五部分：核心功能

### 文件處理 Pipeline

上傳後由 `routers/upload.py` 以 `asyncio.to_thread()` 背景執行，透過 SSE 推播進度。

| 步驟 | 說明 |
|---|---|
| Parse | PDF 每頁轉 Markdown（pymupdf4llm，保留表格） |
| Clean | 去除多餘空白、頁碼殘留、清理後 < 20 字元的段落 |
| Chunk | 每頁 600 字元上限，句號切分，1 句 overlap |
| Embed | gemini-embedding-001，3072-dim，批次 100，寫入 Qdrant |

### ReAct 聊天代理

`services/chat/chat_agent.py` 實作自製 ReAct（Reasoning + Acting）迴圈，不使用 Gemini native Function Calling。

```
使用者輸入
    ↓
組合 System Prompt（prompt_system.md + prompt_react.md）
    ↓
Gemini 輸出 JSON（每輪）
    ├── {"thought": "...", "answer": "..."}  → 直接回覆使用者
    ├── {"thought": "...", "action": "search_knowledge", "arguments": {...}}
    │       → embed_query → Qdrant query_points → 回傳 chunks → 下一輪
    └── {"thought": "...", "action": "create_notebooklm", "arguments": {...}}
            → Playwright 執行 → 回傳 notebook URL → 下一輪
```

最多 6 輪迭代。每輪 broadcast SSE log 給前端。

### 工具 Schema

工具定義存於 `mcp/tools/*.json`，格式遵循 OpenAI/Anthropic 標準：

```json
{
  "type": "function",
  "function": {
    "name": "search_knowledge",
    "description": "...",
    "examples": [...],
    "parameters": { "type": "object", "properties": {...}, "required": [...] }
  }
}
```

`chat/tools/__init__.py` 的 `load_tools()` 動態掃描所有 `.json` 檔載入，新增工具只需加 `.py` + `.json` 無需改程式碼。

### MCP Server

外部 Agent 可透過 `/mcp` 端點連線，與聊天介面共用底層 `store.py`。

| 工具 | 輸入 | 輸出 |
|---|---|---|
| `search_knowledge` | query, top_k=5 | 相關段落列表 |
| `create_notebooklm` | title | NotebookLM 可分享 URL |

### Playwright Agent

NotebookLM 無公開 API，採用 Playwright 操作 Edge 持久化 context（免重新登入）。

```
載入 Edge User Data → 啟動 Edge（headless=False）
→ 建立 Notebook → 上傳 PDF → 等待索引
→ 開啟分享連結 → 回傳 URL
```

---

## 第六部分：AI 機制

### Embedding（`models/embedder.py`）

**模型**：`gemini-embedding-001`，輸出 3072-dim 向量，透過 REST API 呼叫，不需本地 GPU。

| 用途 | task_type |
|---|---|
| 建檔（chunk） | `RETRIEVAL_DOCUMENT` |
| 查詢（query） | `RETRIEVAL_QUERY` |

批次上限 100，超過自動分批。

### RAG 流程

`search_knowledge` 工具執行時：

```
user_query
    ↓
embed_query(query) → 3072-dim
    ↓
store.query_points(vector, top_k=5) → [{text, source, page, score}, ...]
    ↓
chunks 作為 Observation 注入 ReAct 下一輪 prompt
    ↓
Gemini 彙整回答 → 回傳使用者
```

### Prompt 架構

system prompt 由兩個檔案組合：

| 檔案 | 用途 |
|---|---|
| `prompt_system.md` | 系統身份描述（靜態，說明 Interview Practice 的三個能力） |
| `prompt_react.md` | ReAct 框架指令，含佔位符 `{system_description}` `{tools_context}` `{today}` `{system_context}` |

---

## 第七部分：基礎設施

### SSE 事件

| 事件 | 說明 |
|---|---|
| `pipeline_start` | 開始，附帶 filename |
| `pipeline_progress` | 各階段進度（parse / clean / chunk / embed）|
| `pipeline_done` | 完成，附帶 chunk_count |
| `pipeline_error` | 失敗，附帶 message |
| `log` | ReAct 每輪推理步驟的即時 log |
| `heartbeat` | 每 25 秒，維持連線 |

### 環境變數

```
GEMINI_API_KEY=
EDGE_USER_DATA=C:\Users\user\AppData\Local\Microsoft\Edge\User Data
EDGE_PROFILE=Default
```
