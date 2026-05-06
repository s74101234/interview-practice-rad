# 更新紀錄 — 2026-05-06 13:25

1. NotebookLM 登入改用 Edge 本地 Profile，不再用 Chromium + auth.json，跳過 Google 登入問題
2. 啟動前強制砍掉 Edge 背景程序，避免 Profile 被佔用
3. 移除 `setup_auth.py` 與 `.gitignore` 裡的 `auth.json` 規則
4. `ECONNREFUSED /status/stream` 是 Backend 沒啟動，不是 bug
5. `.env` 路徑問題：從 `backend/` 子目錄執行時找不到根目錄的 `.env`，改用絕對路徑解決
6. 前端版面初步重構、色彩系統、排版 class、scrollbar 樣式統一調整
7. `FastMCP` 版本 API 不相容，`get_asgi_app()` 已改名，改用 `hasattr` 相容新舊版，掛載移至 `main.py`
