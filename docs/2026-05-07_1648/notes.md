# 更新紀錄 — 2026-05-07 16:48

## MCP Server 清理

1. 移除 `create_notebooklm_tool` 及對應的 `tools/create_notebooklm.py`，該邏輯屬於 Task 3，不應放在 Task 1 MCP server。MCP 只保留 `search_knowledge_tool`，職責單純。

2. 刪除空的 `routers/mcp.py`，MCP 掛載改在 `main.py` 直接處理。

## Chat Agent 架構重構

3. 將 Gemini retry 邏輯（ServerError 重試、429 限流等待）從 `chat_agent.py` 移進 `gemini.py`，統一在 models 層處理，`_generate()` 縮減為一行 `asyncio.to_thread`。

4. Chat agent 改為自製 **ReAct 推理迴圈**（Thought → Action → Observation），不使用 Gemini native Function Calling。每輪 Gemini 輸出 JSON，後端解析後決定呼叫工具或直接回答。

5. 工具定義改為 **JSON Schema 檔案**（`mcp/tools/*.json`），格式遵循 OpenAI/Anthropic 標準，包含 `name`、`description`、`examples`、`parameters`。`chat/tools/__init__.py` 的 `load_tools()` 動態掃描載入，新增工具只需加 `.py` + `.json`，不改程式碼。

6. Prompt 拆成兩個獨立檔案：`prompt_system.md`（系統身份，靜態）與 `prompt_react.md`（ReAct 框架指令，含佔位符）。兩者在執行期組合注入 Gemini。

## 廢棄程式碼清理

7. `parser.py` 移除 `parse_pptx()` 及 `python-pptx` import，系統僅支援 PDF。`parse()` 直接合併為單一函數。

8. `store.py` 移除未使用的 `Filter`、`FieldCondition`、`MatchValue` import。

9. `app_state.py` 移除已廢棄的 `uploaded_file_path`（初始誤刪後依 notebooklm 需求補回）。

10. `upload.py` 移除對已刪屬性的 `state.uploaded_file_path` 賦值（後來補回，配合 notebooklm 工具）。

## NotebookLM 工具正確歸位

11. `notebooklm.py` 與 `notebooklm.json` 放入 `mcp/tools/`，與 `search_knowledge.py` / `search_knowledge.json` 並排，schema 與實作同資料夾。

12. `config.py` 新增 `edge_user_data`、`edge_profile` 環境變數，移除 notebooklm 內的 Windows 硬編碼路徑。

## Bug 修正

13. Qdrant `client.search()` 在新版 SDK 已移除，改用 `client.query_points(...).points`。

14. Gemini ClientError 的 `status_code` 屬性在新版 SDK 改名，改用 `getattr(e, "status_code", None) or getattr(e, "code", None)` 兼容兩版本。

## 名稱與 Prompt 統一

15. 全專案 `DocMind` 一律改為 `Interview Practice`，涵蓋 `index.html`、`README.md`、`mcp/server.py`、`docs/`。

16. `prompt_system.md` 明確列出系統三個能力：文件問答、知識庫建立、NotebookLM 建立，確保模型知道何時呼叫 `create_notebooklm`。

17. `PromptSuggestions.vue` 三個預設問題改為對應三項實際能力：系統功能介紹、文件 Q&A、建立 NotebookLM。

## Log 強化

18. ReAct 每輪透過 SSE 廣播完整步驟：使用者輸入、Thought、Action 與參數、Observation 預覽、直接回答字數、錯誤時完整模型原始輸出。

## 文件更新

19. `01-backend.md` 與 `02-frontend.md` 全面對齊現況：embedding 維度、ReAct 架構、目錄結構、工具名稱、環境變數。`README.md` 同步更新功能說明與目錄結構。
