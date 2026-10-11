# kimiskills

- 最後更新／內容確認：2026-10-12 05:48（Asia/Taipei，UTC+08:00），僅本次收錄範圍、檔案與使用說明；各工具實際安裝另驗。
- 儲存庫：`kimfull/kimiskills`；Git 基準為首次匯入，沒有既有提交。確認時為尚未初始化 Git 的候選目錄，非已部署環境。

供不同 AI 工具共用的自製技能。首批只收錄 `project-handoff`；不包含第三方技能、專案資料、金鑰或本機測試紀錄。

## 技能

| 技能 | 用途 |
| --- | --- |
| [project-handoff](skills/project-handoff/SKILL.md) | 整理 README、todo、status 與 handoff，核對事實、版本與接手範圍 |

四份文件的分工：README 介紹專案與使用方法；todo 記錄待辦與安排；status 記錄實際狀態；handoff 提供最新交接及下一個動作。按需求建立，不強制湊齊四份。

## 使用

```bash
git clone https://github.com/kimfull/kimiskills.git
```

本儲存庫初始為私有，下載需要具有存取權的 GitHub 帳號。

將完整的 `skills/project-handoff/` 資料夾放進目標 AI 工具支援的技能目錄，或讓工具明確讀取其中的 `SKILL.md`。請保留 `references/`；只複製單一 SKILL.md 會缺少細節規格。已有同名技能時先比對及備份，避免覆蓋尚未同步的修改。

支援技能載入的工具可依其介面選用 `project-handoff`。其他工具可以明確交辦：「請先讀取這份 project-handoff/SKILL.md，再依照我的要求整理專案交接。」實際自動探索、安裝位置及引用語法依各工具而定；本次沒有逐一驗證所有 LLM 的自動觸發。

`agents/openai.yaml` 是 Codex 介面中繼資料；不使用它的工具仍可讀取 SKILL.md 及 references。技能本身不依賴模型 API、Claude 專屬指令或安裝腳本。

## 同步與維護

- 這份 GitHub 儲存庫作為分發來源；更新技能時先修改、驗證並推送，再同步到需要使用的環境。
- `git pull --ff-only` 只更新 clone；不會自動覆寫各工具既有的已安裝副本。
- 本次匯入沒有變更來源主機的已安裝技能或既有連結，也沒有新增定時同步、hook 或部署工作。
- 各環境繼續遵守自己的專案規範與授權。只要求交接文件，不代表授權執行待辦、提交、推送、部署或外部筆記同步。

## 驗證範圍

本包以既有已通過 QA 的 handoff 規格為基礎，另調整環境規範及永久知識庫的固定名稱依賴。發布前核對技能格式、相對連結、完整檔案清單與獨立 QA；這些檢查不等於不同 AI 工具的實際觸發驗收。
