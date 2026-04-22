# 作業：設計 Skill + 打造 AI 聊天機器人

> **繳交方式**：將你的 GitHub repo 網址貼到作業繳交區
> **作業性質**：個人作業

---

## 作業目標

使用 Antigravity Skill 引導 AI，完成一個具備前後端的 AI 聊天機器人。
重點不只是「讓程式跑起來」，而是透過設計 Skill，學會用結構化的方式與 AI 協作開發。

---

## 繳交項目

你的 GitHub repo 需要包含以下內容：

### 1. Skill 設計（`.agents/skills/`）

為以下五個開發階段＋提交方式各設計一個 SKILL.md：

| 資料夾名稱        | 對應指令          | 說明                                                                           |
| ----------------- | ----------------- | ------------------------------------------------------------------------------ |
| `prd/`          | `/prd`          | 產出 `docs/PRD.md`                                                           |
| `architecture/` | `/architecture` | 產出 `docs/ARCHITECTURE.md`                                                  |
| `models/`       | `/models`       | 產出 `docs/MODELS.md`                                                        |
| `implement/`    | `/implement`    | 產出程式碼（**需指定**：HTML 前端 + FastAPI + SQLite 後端）              |
| `test/`         | `/test`         | 產出手動測試清單                                                               |
| `commit/`       | `/commit`       | 自動 commit + push（**需指定**：使用者與 email 使用 Antigravity 預設值） |

### 2. 開發文件（`docs/`）

用你設計的 Skill 產出的文件，需包含：

- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/MODELS.md`

### 3. 程式碼

一個可執行的 AI 聊天機器人，需支援以下功能：

| 功能           | 說明                                       | 是否完成 |
| -------------- | ------------------------------------------ | -------- |
| 對話狀態管理   | 支援多聊天室（session），維持上下文        | O      |
| 訊息系統       | 訊息結構包含 role、content、timestamp      | O        |
| 對話歷史管理   | 可顯示並切換過去的對話紀錄                 | O        |
| 上傳圖片或文件 | 支援使用者上傳檔案作為對話內容             | O        |
| 回答控制       | 提供重新生成（regenerate）或中止回應的功能 | O        |
| 記憶機制       | 儲存使用者偏好，實現跨對話持續性           | O        |
| 工具整合       | 串接外部 API，使聊天機器人具備實際操作能力 | O        |

### 4. 系統截圖（`screenshots/`）

在 `screenshots/` 資料夾放入以下截圖：

- `chat.png`：聊天機器人主畫面，**需包含至少一輪完整的對話**
- `history.png`：對話歷史或多 session 切換的畫面

### 5. 心得報告（本 README.md 下方）

在本 README 的**心得報告**區填寫。

---

## 專案結構範例

```
your-repo/
├── .agents/
│   └── skills/
│       ├── prd/SKILL.md
│       ├── architecture/SKILL.md
│       ├── models/SKILL.md
│       ├── implement/SKILL.md
│       ├── test/SKILL.md
│       └── commit/SKILL.md
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── MODELS.md
├── templates/
│   └── index.html
├── screenshots/
│   ├── chat.png
│   ├── history.png
├── app.py
├── requirements.txt
├── .env.example
└── README.md          ← 本檔案（含心得報告）
```

---

## 啟動方式

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 GEMINI_API_KEY

# 4. 啟動伺服器
uvicorn app:app --reload
# 開啟瀏覽器：http://localhost:8000
```

---

## 心得報告

**姓名**：姚谷伝
**學號**：D1109866

### 問題與反思

**Q1. 你設計的哪一個 Skill 效果最好？為什麼？哪一個效果最差？你認為原因是什麼？**

> **效果最好的是 `implement`。**因為透過事先定義好明確的前後端技術棧（FastAPI + SQLite + 原生 HTML/JS）以及資料夾結構要求，AI 能夠非常精準地遵守規範產出程式碼，免去以往反覆修正專案框架的痛苦。
> 
> **效果最差的是 `prd`。**因為產品需求初期通常具備高度的「模糊性」，如果一開始給的條件過於空泛，AI 會自己腦補出太多不必要的延伸功能，反而造成了過度設計 (Over-engineering) 與範圍蔓延 (Scope Creep) 的問題。

---

**Q2. 在用 AI 產生程式碼的過程中，你遇到什麼問題是 AI 沒辦法自己解決、需要你介入處理的？**

> 1. **複雜的非同步與狀態管理**：例如利用 SSE (Server-Sent Events) 實作生成中斷控制時，前端的按鈕狀態切換與後端的 WebSocket 斷開關聯容易有落差，需要親自介入去調整 Event Loop 的跳出邏輯。
> 2. **隱含的套件相依性問題**：AI 給的 `requirements.txt` 有時不全面，像是使用 UploadFile 時，AI 有時會忘記提醒需要安裝 `python-multipart`，導致伺服器啟動出錯。
> 3. **「工具整合」的實用性判斷差**：AI 雖然能寫出工具串接的邏輯，但它常常不懂得判斷呼叫時機（例如遇到每個問題都硬要去 Query DB 一次），所以必須人工手寫 System Prompt 嚴格限縮它的呼叫條件。
