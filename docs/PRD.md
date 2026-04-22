# 全能 AI 聊天機器人 PRD

## 1. 執行摘要 (Executive Summary)
* **背景動機**: 現代的使用者需要一個高度整合、具備記憶能力且支援多文件格式的個人助理機器人，而非只能做到一次性問答的簡單文字聊天框。
* **產品目標**: 建立一個具備「對話狀態管理」、「多檔案視覺上傳」、「長期記憶機制」、「回答控制與重產」及「工具呼叫介接」功能的完整 Web 版聊天機器人系統。
* **成功指標**:
  - 能夠建立與切換多個互不干擾的對話 Session。
  - 順暢的回答中斷機制與重新生成功能。
  - 對話歷史與檔案能跨裝置（基於 DB）正確顯示。

## 2. 目標受眾 (Target Audience)
* **使用者畫像 (Persona)**:
  * ID / Name: `Antigravity` (本專案預設測試帳號)
  * 需求: 經常閱讀大量文件、需要長期討論專案，希望 AI 記得先前的偏好與設定，不用每次重新告知。

## 3. 功能需求 (Functional Requirements)
1. **對話狀態管理 (Session Management)**
   - 支援建立新聊天室與多輪對話，維持當下 Session 的上下文。
2. **訊息系統 (Message Structure)**
   - 每筆訊息須具備 `role` (user/assistant/system), `content`, `timestamp` 屬性。
3. **對話歷史管理 (Chat History)**
   - 側邊欄顯示過往對話紀錄，點擊可無縫切換並載入過去的歷史對話。
4. **上傳圖片或文件 (Multimodal Upload)**
   - 支援使用者上傳圖片或文件，將檔案做為上下文參考（初期儲存於本地 `static/uploads/`）。
5. **回答控制 (Generation Control)**
   - 提供「重新生成 (Regenerate)」上一次回答的功能。
   - 提供「中止回應 (Stop)」及時掐斷冗長生成邏輯的能力 (使用 SSE 或前端 Polling 控制)。
6. **記憶機制 (Memory)**
   - 提供隱含的機制或 API 路由，將使用者的長期偏好儲存下來，並在所有 Session 都可用。
7. **工具整合 (Tool Use)**
   - 預留呼叫外部 API 的處理邏輯與路由機制。

## 4. 非功能需求 (Non-functional Requirements)
* **技術堆疊**: FastAPI + SQLite + HTML/JS/CSS。
* **安全性**: 本地儲存無機密外洩風險，但需確保 DB 讀寫安全。

## 5. UI/UX 與設計
* 仿 ChatGPT 或 Claude 介面：左側歷史清單，右側為對話主體。
* 包含上傳按鈕、停止生成按鈕與重新生成按鈕。

## 6. 不做的範圍 (Out of Scope)
* 暫不串接真實金流。
* 暫不考慮多團隊協作 (單純個人版使用)。
