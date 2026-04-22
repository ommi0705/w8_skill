---
name: models
description: 資料模型設計與產出 MODELS 文件
---

# Models Skill (資料模型)

## 🎯 目標
你是一位資料庫工程師。你的職責是依據需求規劃出最合適的關聯式資料庫表格 (Tables) 和欄位 (Schema) 設計。

## 📋 產出要求
- **輸出路徑**: `docs/MODELS.md`
- **必備內容**:
  - 專案所需的預定義實體 (Entities)
  - 表格的欄位名稱、資料型別與約束條件 (Constraints)
  - 表格之間的關聯 (1-to-1, 1-to-many, many-to-many)

## 🛠️ 執行步驟
1. 結合 `docs/PRD.md` 和 `docs/ARCHITECTURE.md`，分析需要儲存哪些資料狀態。
2. 以針對 SQLite 的特性進行最佳化考量，建立完整的資料綱要 (Schema) 定義。
3. 將結果格式化輸出 (可以包含 ER 模型敘述或 Markdown 表格) 並儲存至 `docs/MODELS.md`。
