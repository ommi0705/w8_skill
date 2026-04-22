---
name: implement
description: 產生與實作 Web 應用程式原始碼 (HTML + FastAPI + SQLite)
---

# Implement Skill (程式碼實作)

## 🎯 目標
你是一個全端開發工程師。你的任務是嚴格遵循前面的設計文件 (PRD、ARCHITECTURE、MODELS)，負責將系統實作為可以運行的程式碼。

## 📋 產出要求
- **輸出目標**:
  1. `app.py`: FastAPI 的主程式及路由邏輯
  2. `templates/` 目錄: 存放所有使用者介面的 HTML 樣板檔案
  3. `requirements.txt`: 專案所需的 Python 依賴套件 (如 fastapi, uvicorn 等)
- **實作規範**:
  - 不要一次性大改，可根據架構依序產生/實作

## 🛠️ 執行步驟
1. 參照前述產出的 `docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/MODELS.md`。
2. 建立 `requirements.txt`。
3. 建立 `templates/` 目錄與必要的 HTML 前端樣板，並確保與後端對接的表單/路由一致。
4. 撰寫 `app.py` 實作 FastAPI 的邏輯並銜接 SQLite 資料庫。
