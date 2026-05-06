# 01. 後端設計

> 最後更新：2026-05-06

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

**DocMind** 整合以上三項任務為單一系統。

---

## 第二部分：情境與功能

### 應用情境

使用者上傳 PDF 或 PPTX 文件，系統建立向量知識庫。透過聊天介面與 Gemini 對話，Gemini 自動判斷是否查詢知識庫或建立 NotebookLM 簡報。

```
上傳 PDF / PPTX
        ↓
Extract → Clean → Chunk → Gemini Embedding → Qdrant
        ↓
使用者輸入問題
        ↓
Gemini（Function Calling）
   ├── search_knowledge  → 搜尋知識庫 → 彙整回答
   └── create_notebook   → Playwright → NotebookLM URL
```

**對話範例**：
- 「這份文件的主要結論是什麼？」→ 搜尋知識庫後回答
- 「第三章提到了哪些技術指標？」→ 搜尋對應段落後回答
- 「幫我把這份文件整理成一份簡報」→ 建立 NotebookLM 並回傳連結
- 「建立一個可以分享給同事的筆記本」→ 同上

### 功能清單

| 功能 | 說明 |
|---|---|
| 文件上傳 | 接收 PDF 或 PPTX，觸發背景處理 |
| 處理進度 | SSE 即時回報各階段進度 |
| 聊天問答 | Gemini 根據知識庫內容回答問題 |
| 建立簡報 | 使用者提及建立簡報時，自動呼叫 `create_notebook` |
| MCP 工具 | 兩個工具供外部 Agent 連線查詢 |
| Claude Skills | 前處理四步驟包裝為 Claude Code 可呼叫的介面 |

---

## 第三部分：技術棧

| 層次 | 技術 | 說明 |
|---|---|---|
| 後端框架 | FastAPI + Uvicorn（Python 3.12+）| |
| LLM + Embedding | Gemini API（gemini-2.0-flash, text-embedding-004）| 聊天、工具呼叫、向量化 |
| 向量資料庫 | Qdrant（local 模式）| |
| PDF 解析 | pymupdf4llm | PDF → Markdown，保留表格結構 |
| PPTX 解析 | python-pptx | 逐張擷取文字 |
| MCP | FastMCP | |
| 瀏覽器自動化 | Playwright + Chromium storageState | 免重新登入操作 NotebookLM |
| 即時狀態 | SSE（Server-Sent Events）| |
| 部署 | Google Cloud e2-micro | 免費方案，不需 GPU |

---

## 第四部分：目錄結構

```
backend/
├── main.py
├── core/
│   └── config.py
├── routers/
│   ├── upload.py               文件上傳與觸發 pipeline
│   ├── chat.py                 聊天介面
│   ├── status.py               SSE 進度推播
│   └── mcp.py                  MCP Server 端點
└── services/
    ├── ingestion_pipeline/
    │   ├── parser.py            pymupdf4llm (PDF), python-pptx (PPTX)
    │   ├── cleaner.py
    │   └── chunker.py
    ├── models/
    │   ├── embedder.py          Gemini text-embedding-004
    │   └── gemini.py            Gemini 推論（聊天 + Function Calling）
    ├── data/
    │   └── store.py             Qdrant upsert + search
    ├── mcp/
    │   ├── server.py
    │   └── tools/
    │       ├── search_knowledge.py    呼叫 data/store.py
    │       └── create_notebooklm.py   驅動 Playwright
    └── chat/
        └── chat_agent.py        Gemini Function Calling，呼叫 mcp/tools/

.claude/commands/                Claude Code Skills，邏輯與 ingestion_pipeline/ 共用
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
| Parse | PDF 每頁轉 Markdown（保留表格），PPTX 逐張取標題 + 內文 |
| Clean | 去除多餘空白、頁碼殘留、清理後 < 20 字元的段落 |
| Chunk | 每頁 600 字元上限，句號切分，1 句 overlap |
| Embed | Gemini text-embedding-004，768-dim，批次 16，寫入 Qdrant |

### 聊天代理

`services/chat/agent.py` 使用 Gemini Function Calling，每輪流程：

```
使用者輸入
    ↓
Gemini 判斷（附帶工具定義）
    ├── 直接回答
    ├── 呼叫 search_knowledge → 取回 chunks → 彙整回答
    └── 呼叫 create_notebook  → Playwright 執行 → 回傳 URL
```

### MCP Server

外部 Agent（如 Claude Desktop 或測試腳本）可連線查詢知識庫，與聊天介面共用底層 `store.py`。

| 工具 | 輸入 | 輸出 |
|---|---|---|
| `search_knowledge` | query, top_k=5 | 相關段落列表 |
| `create_notebook` | title | NotebookLM 可分享 URL |

本地開發使用 `stdio`，部署後使用 `Streamable HTTP`。

### Playwright Agent

NotebookLM 無公開 API，採用 Playwright 自動化。Google 登入以 `storageState` 儲存 session，適用本機與雲端部署。

```
載入 auth.json → 啟動 Chromium（headless）
→ NotebookLM 建立 Notebook → 上傳 PDF
→ 等待索引完成 → 開啟分享 → 回傳 URL
```

### Claude Skills

`skills/` 是 `services/ingestion/` 的 Claude Code 呼叫介面，邏輯完全共用，可依序串接：

```bash
/parse-doc path/to/file.pdf
/clean-text
/chunk-doc
/build-kb collection=my_docs
```

---

## 第六部分：AI 機制

### 6.1 Embedding（`models/embedder.py`）

**模型**：Gemini `text-embedding-004`，輸出 768-dim 向量，透過 API 呼叫，不需本地 GPU。

**建檔時**（document side）：

```
chunk.text → Gemini text-embedding-004 → 768-dim 向量 → Qdrant upsert
```

payload 附帶：`{source, page, text, char_count}`，供搜尋後回傳給前端。

**查詢時**（query side）：

```
user_query → Gemini text-embedding-004 → 768-dim 向量 → Qdrant search（COSINE）
```

---

### 6.2 RAG 流程（`data/store.py` + `models/gemini.py`）

`search_knowledge` 工具呼叫時的完整 RAG 流程：

```
user_query
    ↓
embedder.embed(query) → 768-dim
    ↓
store.search(vector, top_k=5) → [{text, source, page, score}, ...]
    ↓
chunks 注入 Gemini prompt（作為 context）
    ↓
Gemini 彙整回答 → 回傳使用者
```

Prompt 結構：

```
[System]
你是一個文件助理，根據以下段落內容回答問題。
若段落中無相關資訊，請直接說明找不到。

[Context]
來源：{source}，第 {page} 頁
{chunk_text}
...（最多 5 段）

[User]
{user_query}
```

---

### 6.3 Gemini Function Calling（`chat/chat_agent.py`）

每輪對話將工具定義傳入 Gemini，由模型自行決定是否呼叫：

```
使用者輸入
    ↓
Gemini（附帶 tools 定義）
    ├── 無需工具 → 直接生成回答
    ├── 呼叫 search_knowledge
    │       → 後端執行 RAG → 回傳 chunks
    │       → Gemini 以 chunks 為 context 生成回答
    └── 呼叫 create_notebooklm
            → 後端執行 Playwright → 回傳 notebook_url
            → Gemini 將 URL 嵌入回覆訊息
```

**工具定義（傳入 Gemini）**：

```
search_knowledge
  描述：搜尋已上傳文件的知識庫，回傳相關段落
  輸入：query(str), top_k(int=5)
  輸出：[{text, source, page, score}, ...]

create_notebooklm
  描述：將已上傳的文件建立為 NotebookLM 筆記本，回傳可分享連結
  輸入：title(str)
  輸出：{notebook_url: str}
```

**觸發條件**（由 Gemini 自行判斷，非規則比對）：
- 詢問文件內容 → 傾向呼叫 `search_knowledge`
- 提及建立簡報、分享、筆記本 → 傾向呼叫 `create_notebooklm`
- 一般問候或無需文件的問題 → 直接回答

---

## 第七部分：基礎設施（SSE + 環境變數）

### SSE 事件

| 事件 | 說明 |
|---|---|
| `pipeline_start` | 開始，附帶 filename |
| `pipeline_progress` | 各階段進度（parse / clean / chunk / embed）|
| `pipeline_done` | 完成，附帶 chunk_count |
| `pipeline_error` | 失敗，附帶 message |
| `heartbeat` | 每 25 秒，維持連線 |

### 環境變數

```
GEMINI_API_KEY=
QDRANT_HOST=localhost
QDRANT_PORT=6333
```
