# kimiskills

- 最後更新：2026-10-13 06:40（Asia/Taipei，UTC+08:00）。
- 內容確認：
  - 2026-10-13 06:40（Asia/Taipei，UTC+08:00）：`lean-coding` 的收錄範圍與檔案、技能表、儲存庫可見性。
  - 2026-10-12 05:48（Asia/Taipei，UTC+08:00）：`project-handoff` 的收錄範圍、檔案與使用說明；這次沒有重新確認。
  - 各工具的實際安裝另驗。
- 儲存庫：`kimfull/kimiskills`；Git 基準 `0a780ae33dc9aca7a5a1f76a502d8a686fba6829`（dev 分支）。確認當下工作目錄有未提交的變更：新增 `skills/lean-coding/` 的兩個檔與本檔修改，隨這次提交一起進版。

供不同 AI 工具共用的自製技能。目前收錄 `project-handoff` 與 `lean-coding`；不包含第三方技能、專案資料、金鑰或本機測試紀錄。

## 技能

| 技能 | 用途 |
| --- | --- |
| [project-handoff](skills/project-handoff/SKILL.md) | 整理 README、todo、status 與 handoff，核對事實、版本與接手範圍 |
| [lean-coding](skills/lean-coding/SKILL.md) | 寫程式與改程式時的輕量準則：最小充分變更、驗證力度跟著風險走、架構有需求才加；附 Cloudflare Workers 的取捨與防呆參考 |

`project-handoff` 四份文件的分工：README 介紹專案與使用方法；todo 記錄待辦與安排；status 記錄實際狀態；handoff 提供最新交接及下一個動作。按需求建立，不強制湊齊四份。

## 使用

```bash
git clone https://github.com/kimfull/kimiskills.git
```

本儲存庫目前是公開的（2026-10-13 確認），不需要登入即可下載。預設分支是 `dev`。

將完整的技能資料夾（例如 `skills/project-handoff/` 或 `skills/lean-coding/`）放進目標 AI 工具支援的技能目錄，或讓工具明確讀取其中的 `SKILL.md`。請保留 `references/`；只複製單一 SKILL.md 會缺少細節規格。已有同名技能時先比對及備份，避免覆蓋尚未同步的修改。

支援技能載入的工具可依其介面選用技能。其他工具可以明確交辦，例如：「請先讀取這份 project-handoff/SKILL.md，再依照我的要求整理專案交接。」實際自動探索、安裝位置及引用語法依各工具而定；沒有逐一驗證所有 LLM 的自動觸發。

`skills/project-handoff/agents/openai.yaml` 是 Codex 介面中繼資料；不使用它的工具仍可讀取 SKILL.md 及 references。`lean-coding` 沒有這個檔。兩支技能本身都不依賴模型 API、Claude 專屬指令或安裝腳本。

## 同步與維護

- 這份 GitHub 儲存庫作為分發來源；更新技能時先修改、驗證並推送，再同步到需要使用的環境。
- `git pull --ff-only` 只更新 clone；不會自動覆寫各工具既有的已安裝副本。
- 首次匯入（2026-10-12）沒有變更來源主機的已安裝技能或既有連結，也沒有新增定時同步、hook 或部署工作。收錄 `lean-coding`（2026-10-13）同樣只新增檔案，各環境的安裝另行處理。
- 各環境繼續遵守自己的專案規範與授權。只要求交接文件，不代表授權執行待辦、提交、推送、部署或外部筆記同步。

## 驗證範圍

`project-handoff`（沿用 2026-10-12 的紀錄，這次沒有重新確認）：本包以既有已通過 QA 的 handoff 規格為基礎，另調整環境規範及永久知識庫的固定名稱依賴。發布前核對技能格式、相對連結、完整檔案清單與獨立 QA；這些檢查不等於不同 AI 工具的實際觸發驗收。

`lean-coding`（2026-10-13）：

- 已核對：技能格式；32 個外部連結；關鍵技術敘述對照 Cloudflare 官方文件；與前一版逐條比對規則；獨立 QA，兩項必修已修正並複驗通過。
- 已實測：三個小型測試專案上，前一版與這一版各跑一次，結果幾乎相同；在 Claude Code（Opus 5.5）上的觸發測試，該選中的 30 次全部選中，不該選中的 30 次沒有誤選。實測之後依 QA 意見改回 8 處措辭，沒有重測。
- 沒有驗證：與「不安裝這支技能」相比的效益；Codex 與其他 AI 工具的觸發；受試者能執行命令時的驗證行為。
