# 更新紀錄 — 2026-05-11

## NotebookLM 瀏覽器自動化 — 全面重構

1. `browser.py` 的 `get_page_state()` 改用 `inner_text()` 搭配逐一剝除 `<mat-icon>` 文字，讓 buttons 只留下可見語意文字（例如原本的「add 新建」變成「新建」），避免 agent 用含圖示前綴的字串去找按鈕。

2. `click()` 和 `force_click()` 的 fallback 從 `:text('...')` CSS Selector 改為 `filter(has_text=)` + `get_by_text()`，解決含換行或特殊字元的按鈕文字導致 Playwright BADSTRING 解析錯誤。

3. `click_by_css()` 移除 `force=True`，讓 Angular CDK 的 pointer event 正常走完，`mat-select` 的 `aria-expanded` 才會切換為 `true`，overlay 的 `mat-option` 才會出現在 DOM。

4. `get_page_state()` 新增 `options` 欄位，讀取 `mat-option` 元素（CDK overlay 展開後才出現），讓 agent 能看到下拉選項再決定點哪個。

5. `upload_file()` 改用 `expect_file_chooser()` 包住按鈕點擊，Playwright 在 OS 視窗出現前就攔截 file chooser，原生檔案選擇器不再彈出。新增 `_dismiss_os_dialog()` 以 `ctypes.FindWindowW("#32770")` 精確找 Windows 通用對話框，找到才關閉，不影響瀏覽器視窗。

6. `agent.py` 改從 `prompt_browser.md` 讀取 system prompt，並載入 `browser.json` 的工具 schema，以與 chat agent 相同的 `_build_tools_context()` 邏輯動態渲染 Tools 區段，不再硬編碼。

7. `agent.py` 在 context 建立後立即呼叫 `context.grant_permissions(["clipboard-read", "clipboard-write"])`，解決 `navigator.clipboard.readText()` 因缺少權限導致 Promise 永遠 pending、整個 `get_clipboard()` 卡住的問題。

8. `agent.py` 每輪迴圈開頭檢查 `state.cancel_event`，觸發後關閉瀏覽器 context 並拋出 `InterruptedError`。

## NotebookLM Prompt 重新設計

9. `prompt_browser.md` 改為 Task / Steps / Don't / Tools 四段式結構，Steps 改為意圖描述（一句說明目標），讓 agent 自行推理要用哪個工具，而非照腳本走。

10. `browser.json` 整合 8 個瀏覽器動作的 JSON Schema（`click`、`force_click`、`click_by_css`、`upload_file`、`press_key`、`wait`、`get_clipboard`、`finish`），格式與 `search_knowledge.json` 統一。

11. Don't 補上三條從實際執行 log 歸納的禁止事項：不可在 `upload_file` 前另外 click「上傳檔案」、不可先點「儲存」再點「複製連結」（儲存後對話框關閉）、不可在 `options` 為空時就嘗試點選項。

## 任務中斷機制

12. `app_state.py` 新增 `cancel_event = threading.Event()`，作為跨執行緒的取消訊號。

13. `routers/cancel.py` 新增 `POST /cancel` endpoint，設定 `cancel_event`。

14. `chat_agent.py` 每次請求開頭執行 `state.cancel_event.clear()`，避免上一次中斷殘留影響下一次請求。

15. `api/chat.ts` 加入 `AbortController` 支援，`sendMessage()` 接收 `signal` 參數；新增 `cancelChat()` 呼叫後端 `/cancel`。

16. `stores/chat.ts` 新增 `cancel()` action：同時呼叫 `cancelChat()`（停止後端）與 `abortController.abort()`（立即終止 HTTP fetch），`isAnswering` 立刻設為 `false`。

17. `ChatPanel.vue` 執行中（`isAnswering`）時，右下角按鈕從垃圾桶換成 ■ 停止圖示，hover 變紅；閒置時恢復為清除對話按鈕。

## 上傳替換機制

18. `store.py` 新增 `reset()` — 刪除並重建 Qdrant collection，清除舊文件的所有向量。

19. `upload.py` 上傳新檔案前先執行清除流程：刪除舊的本地 PDF 檔案、呼叫 `reset()` 清空向量資料庫、將 `app_state` 的 filename / chunk_count 歸零，確保系統任何時間只有一份文件。

## DOM 觀察強化

20. `agent.py` 每步推理前先以 `log(f"DOM：{page_state}")` 廣播完整的 `page_state` JSON，讓 log 面板可以直接對照 buttons / options / selects 診斷 agent 行為。
