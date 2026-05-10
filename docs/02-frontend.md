# 02. 前端設計

> 最後更新：2026-05-11

---

## 第一部分：技術棧

| 層次 | 技術 | 說明 |
|---|---|---|
| 框架 | Vue3 + TypeScript | |
| 狀態管理 | Pinia | 兩個 Store（upload / chat）|
| 樣式 | Tailwind CSS + CSS 變數語意 token | |
| 建構工具 | Vite | |
| 路由 | Vue Router | 單頁，`/` → `MainView` |

---

## 第二部分：目錄結構

```
frontend/
├── index.html
└── src/
    ├── main.ts
    ├── App.vue
    ├── assets/
    │   └── main.css
    ├── api/
    │   ├── upload.ts
    │   └── chat.ts
    ├── stores/
    │   ├── upload.ts
    │   └── chat.ts
    ├── views/
    │   └── MainView.vue
    └── components/
        ├── UploadPanel.vue
        ├── ChatPanel.vue
        ├── ProgressPanel.vue
        ├── chat/
        │   └── PromptSuggestions.vue
        ├── layout/
        │   ├── LeftPanel.vue
        │   ├── RightPanel.vue
        │   └── SideNav.vue
        └── sections/
            ├── StatusSection.vue
            └── UploadSection.vue
```

---

## 第三部分：頁面結構

左右兩欄佈局：

```
┌──────────────┬────────────────────────────┐
│  SideNav     │  RightPanel                │
│              │  ┌──────────────────────┐  │
│  LeftPanel   │  │  ChatPanel           │  │
│  UploadPanel │  │  PromptSuggestions   │  │
│  StatusSection│  │  對話訊息列表        │  │
│              │  │  輸入框              │  │
└──────────────┴──┴──────────────────────┴──┘
```

---

## 第四部分：Store

### `stores/upload.ts`

```typescript
// State
isProcessing: boolean
currentStage: 'parse' | 'clean' | 'chunk' | 'embed' | null
chunkCount: number | null
error: string | null

// Actions
uploadFile(file: File)      // POST /upload，觸發 SSE 訂閱
startStatusStream()         // 建立 SSE 連線 /status/stream
stopStatusStream()
```

### `stores/chat.ts`

```typescript
// State
history: { role: 'user' | 'assistant'; content: string; tool?: string }[]
isAnswering: boolean

// Actions
send(message: string)    // POST /chat，內部建立 AbortController
cancel()                 // POST /cancel + abort fetch，立即停止執行中任務
clear()                  // 清除對話紀錄
```

---

## 第五部分：組件設計

### `UploadPanel.vue`

拖曳或點擊上傳 PDF（`accept=".pdf"`）。

| 狀態 | 說明 |
|---|---|
| 預設 | 虛線框，提示文字 |
| 處理中 | 按鈕 disabled |
| 完成 | 顯示已上傳文件名稱，可再次上傳 |

### `ProgressPanel.vue`

上傳後顯示，完成後自動隱藏。

```
parse   ██░░░░  20%   解析文件結構
clean   ████░░  40%   清洗文字內容
chunk   ██████  60%   切分段落
embed   ██████  80%   建立向量索引
done    ██████ 100%   知識庫就緒
```

### `ChatPanel.vue`

與 ReAct agent 對話，agent 自動判斷是否呼叫工具。

```
[使用者] 作者有哪些技術能力與專案經驗？

[助理] 根據文件內容，主要技術能力包含...
       [ 已查詢知識庫 ]

[使用者] 幫我建立 NotebookLM 筆記本

[助理] 已為您建立 NotebookLM 筆記本：
       https://notebooklm.google.com/...
       [ 已建立 NotebookLM ]
```

- 輸入框 + 送出按鈕（Enter 鍵觸發）
- 回答中顯示 loading（spinning 動畫 + 當前 thought 文字）
- 執行中右下角按鈕切換為 ■ 停止圖示，hover 變紅，點擊立即中斷任務
- 閒置時右下角為垃圾桶清除按鈕
- 知識庫未建立時輸入框 disabled

### `PromptSuggestions.vue`

知識庫就緒後顯示三個預設問題，點擊直接送出：

| 問題 | 對應能力 |
|---|---|
| 這個系統有什麼功能？ | 系統自我介紹（不呼叫工具）|
| 作者有哪些技術能力與專案經驗？ | search_knowledge |
| 幫我將這份文件建立成 NotebookLM 筆記本 | create_notebooklm |

---

## 第六部分：設計規範

### 色彩系統

```css
:root {
  --color-bg-base:        #fffef3;
  --color-bg-elevated:    #fdf6e3;
  --color-bg-surface:     #ffffff;

  --color-border:         #e3e6f0;
  --color-border-focus:   #f6c23e;

  --color-text-primary:   #1c1810;
  --color-text-secondary: #4a4030;
  --color-text-muted:     #8a7860;

  --color-primary:        #f6c23e;
  --color-primary-subtle: rgba(246, 194, 62, 0.15);
  --color-primary-text:   #6e5228;

  --color-success:        #1cc88a;
  --color-success-subtle: rgba(28, 200, 138, 0.12);
  --color-danger:         #e74a3b;
  --color-danger-subtle:  rgba(231, 74, 59, 0.12);
}
```

所有組件只使用語意 token，禁止直接寫 hex 色碼或 Tailwind 色票。

### Card 統一結構

```html
<div class="rounded-xl border border-[--color-border] overflow-hidden">
  <div class="px-4 py-3 bg-[--color-bg-elevated] border-b border-[--color-border]">
    <h3 class="ui-title text-[--color-text-primary]">Panel 名稱</h3>
  </div>
  <div class="p-4 bg-[--color-bg-surface]">
    <!-- 內容 -->
  </div>
</div>
```

### 按鈕規範

| 類型 | 用途 | 樣式 |
|---|---|---|
| Primary | 送出問題、上傳文件 | `bg-[--color-primary] text-[--color-primary-text]` |
| Secondary | 複製連結、次要動作 | `bg-[--color-bg-elevated] border border-[--color-border]` |
