# 更新紀錄 — 2026-05-06 20:43

1 Pipeline log 重複顯示「開始處理」，移除前端那筆，改由後端統一廣播。各階段 log 也補上完整統計數字，切分段落新增總字元顯示。

2 修正 `parser.py` 的 `KeyError: 'page'`，改用 `meta.get()` 兼容不同版本的 metadata 欄位名稱。

3 Embedding 改用 `urllib.request` 直接呼叫 REST API，不再依賴 SDK。模型換為 `gemini-embedding-001`（3072 維），Qdrant 維度同步更新。

4 Chat 模型換為 `gemini-2.5-flash`。上述模型問題的根本原因是舊 API key 免費配額為 0，換 AI Studio key 後恢復正常。

5 頁面重新整理後知識庫狀態會遺失，後端新增 `GET /status`，前端 mount 時呼叫 `restoreState()` 修正此問題。

6 `uploads/` 啟動時自動清空，與 `data/qdrant/` 一起加入 `.gitignore`。
