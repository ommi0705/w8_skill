# 資料模型設計 (MODELS.md)

本專案使用 SQLite，以下為各表格關聯與欄位定義。

## 1. 關聯概覽 (ER Diagram)
- User `(1)` <--> `(N)` Session
- Session `(1)` <--> `(N)` Message
- User `(1)` <--> `(N)` Memory

## 2. Table `users`
儲存基本帳號資訊。(測試會使用一組預設帳號)
| 欄位名稱 | 型態 | 約束 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY | 使用者 ID |
| `username` | TEXT | UNIQUE, NOT NULL | 使用者名稱 (預設: Antigravity) |
| `email` | TEXT | | 電子郵件 |

## 3. Table `sessions`
儲存各個不同的聊天室或「對話狀態」。
| 欄位名稱 | 型態 | 約束 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY | 聊天室 ID |
| `user_id` | INTEGER | FOREIGN KEY | 所屬使用者 |
| `title` | TEXT | | 聊天室標題 (預設可以是第一句話) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 建立時間 |

## 4. Table `messages`
儲存所有「訊息系統」的紀錄。包含角色、內容與上傳的檔案路徑。
| 欄位名稱 | 型態 | 約束 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY | 訊息 ID |
| `session_id` | INTEGER | FOREIGN KEY | 關聯的聊天室 ID |
| `role` | TEXT | NOT NULL | 角色: `user` 或 `assistant` 或 `system` |
| `content` | TEXT | | 訊息純文字內容 |
| `media_path` | TEXT | | 上傳圖片/文件的本地路徑 (如 `static/uploads/x.jpg`) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 時間戳記 |

## 5. Table `memories`
用於儲存聊天機器人的「記憶機制」，將萃取出的偏好存為 Key-Value 對。
| 欄位名稱 | 型態 | 約束 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY | 偏好 ID |
| `user_id` | INTEGER | FOREIGN KEY | 所屬使用者 |
| `key` | TEXT | NOT NULL | 記憶的鍵 (例如: `language_preference`) |
| `value` | TEXT | NOT NULL | 記憶的值 (例如: `zh-TW`) |
