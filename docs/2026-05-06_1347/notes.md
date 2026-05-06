# 更新紀錄 — 2026-05-06 13:47

1. 訊息泡泡文字顏色修正：使用者訊息從 `--color-primary-text` 改為 `--color-text-on-primary`，解決深棕字配深棕底幾乎看不見的問題
2. ChatPanel 輸入框改為 textarea，加入 `field-sizing: content` 自動高度、`focus:ring-2 focus:ring-[--color-primary]`，送出按鈕改為 `w-10 h-10 rounded-xl`
3. UploadPanel 加入三種狀態的圖示（預設文件圖示 / 處理中 spinner / 完成 checkmark）
4. ProgressPanel 步驟改為圓形狀態圖示（done = checkmark、active = pulse dot）
5. 前端架構對齊設計系統：新增 `SideNav.vue`（照抄 PicVault 的 nav 按鈕樣式）、`navigation.ts` store，移除 LeftPanel / RightPanel 切換按鈕設計
6. 新增 `sections/UploadSection.vue` 與 `sections/StatusSection.vue`，MainView 改用 sections 路由模式，與 SideNav 連動
7. `App.vue` 加入 backend health check：輪詢 `/health` 直到回應，未就緒時顯示全畫面 spinner
8. backend `main.py` 新增 `GET /health` 端點
