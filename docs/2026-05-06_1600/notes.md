# 更新紀錄 — 2026-05-06 16:00

1. 新增 `tools/generate_pdf.py`，透過 Playwright 開啟真實網站截圖並合併成 PDF，作為測試與範例文件。初版用 Pillow 產生圖片型 PDF 導致文字無法擷取，後改用 `page.pdf()` 產生文字型 PDF，並以 `pypdf` 合併。`frontend/public/sample.pdf` 同步更新，UploadPanel 加入下載連結。

2. Qdrant 改為本地檔案模式，不再需要 Docker，資料存於 `backend/data/qdrant/`。為避免 reload 模式下雙 process 同時鎖檔，改用 lazy init，第一次使用時才初始化 client。

3. 後端 pipeline 各階段加入 `log` SSE 事件，前端 store 統一收集含時間戳的 log 訊息，包含連線、上傳、處理進度、錯誤等完整紀錄。版面移除系統資訊 Card，僅保留上傳文件、文件資訊、系統紀錄三個區塊，系統紀錄常駐顯示。

4. 上傳框從垂直置中改為橫向緊湊排版。`uploads/` 資料夾於每次後端重啟時自動清空，並加入 `.gitignore`（連同 `backend/data/`）避免進入版本控制。
