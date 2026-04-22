# 系統架構設計 (ARCHITECTURE.md)

## 1. 架構概覽
本系統為輕量級的全端 Web 應用。
* **前端 (Frontend)**: 原生 HTML5, CSS3, ES6 JavaScript。處理視圖呈現、SSE 串流接收與多輪對話邏輯。
* **後端 (Backend)**: FastAPI (Python)。負責 API 處理、靜態檔案掛載與 WebSocket/SSE 發送。
* **資料庫 (Database)**: SQLite。搭配 `sqlite3` 原生模組或 `SQLAlchemy` ORM。

## 2. 目錄結構規劃
```
.
├── app.py                # FastAPI 進入點與業務邏輯
├── requirements.txt      # 依賴套件
├── docs/                 # 開發文件 (PRD, 模型, 架構)
├── templates/            # 前端 HTML 樣板
│   └── index.html
└── static/               # 靜態資源
    └── uploads/          # 上傳檔案的儲存目錄
```

## 3. 核心 API 端點設計 (Endpoints)
* `GET /` : 渲染首頁 (`templates/index.html`)
* `GET /api/sessions`: 讀取當前使用者的所有對話室列表
* `POST /api/sessions`: 建立新對話室
* `GET /api/sessions/{session_id}/messages`: 讀取某個對話室的歷史訊息
* `POST /api/chat`: 傳遞對話訊息給後端。若模擬流式輸出，可回傳 `text/event-stream` (SSE) 或提供 Task ID 供前端查詢。
* `POST /api/chat/stop`: 停止正在生成中的回應。
* `POST /api/upload`: 處理前端的上傳檔案。
* `GET /api/memory`: 取得使用者的偏好設定或記憶。

## 4. 技術細節
* **模擬回答**: 為了實作「中斷」與「生成控制」，後端 `api/chat` 會使用非同步的逐字回傳 (StreamingResponse)。
* **前端狀態**: 前端透過 JavaScript 維護當下選擇的 `currentSessionId`，並透過 `fetch` 取回對話資料動態繪製 DOM。
