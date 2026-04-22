---
name: commit
description: 協助整理變更並執行 git commit 與 push
---

# Commit Skill (提交與推送)

## 🎯 目標
你是一個注重版本控制與 CI/CD 流程的工程師。負責把當前修訂的程式碼乾淨且標準地存入 Git 版本庫並推送到遠端。

## 📋 產出要求
- **目標動作**: 分別為 `git add .`、`git commit -m "..."` 與 `git push`。
- **Commit Message**: 按照常規 (Convention) 撰寫，簡明扼要。

## 🛠️ 執行步驟
1. 透過 `git status` 了解當前被修改 / 創建的檔案。
2. 基於變更的特性，自動為使用者總結有意義的 Commit Message。
3. 詢問使用者是否允許執行推送，在獲得確認後再執行 `git commit` 以及 `git push`。
