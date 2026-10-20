# kimiskills

- 最後更新：2026-10-20 14:09（Asia/Taipei，UTC+08:00）。
- 內容確認：
  - 2026-10-20 14:09（Asia/Taipei，UTC+08:00）：`project-docs` 1.2 的技能表、文件分工、分組指令與相關說明（含 1.1 的 todo／handoff 點名規則、1.2 的 ARCHITECTURE.md）；只重查這個範圍。
  - 2026-10-18 18:44（Asia/Taipei，UTC+08:00）：`rvc-omm-authoring` 的收錄範圍、檔案與使用說明，以及本檔對應的技能表、使用與驗證範圍段落；只重查這個範圍。
  - 2026-10-13 21:51（Asia/Taipei，UTC+08:00）：`project-docs` 的名稱、資料夾路徑與本檔的相關連結（由 `project-handoff` 改名）；只重查這個範圍。
  - 2026-10-13 21:19（Asia/Taipei，UTC+08:00）：`project-docs` 的分組指令與 README 寫入門檻（確認時名稱是 `project-handoff`）。
  - 2026-10-13 06:40（Asia/Taipei，UTC+08:00）：`lean-coding` 的收錄範圍與檔案、技能表、儲存庫可見性。
  - 2026-10-12 05:48（Asia/Taipei，UTC+08:00）：`project-docs`（當時名稱 `project-handoff`）的收錄範圍、檔案與使用說明；這次沒有重新確認。
  - 各工具的實際安裝另驗。
- 改名紀錄：2026-10-13，`project-handoff` 改名為 `project-docs`。較早的紀錄以括號註明當時名稱。
- 儲存庫：`kimfull/kimiskills`（dev 分支）。Git 基準依確認範圍分開：
  - `project-docs` 1.2（2026-10-20 14:09）：`a93f697239867dc17268da2ee8946d4f7a67bd2a`。確認當下工作目錄 clean，只有本檔待改。
  - `rvc-omm-authoring`（2026-10-18 18:44）：`d0693389df823c303c1378a7cb182429a0c290e0`。確認當下工作目錄有未提交的變更：新增 `skills/rvc-omm-authoring/`（9 檔），以及本檔與 `AGENTS.md`。
  - `project-docs` 改名（2026-10-13 21:51）：`c6a3945253d5afc40bd0b34d6fddf2b1e4cf4b9c`。確認當下工作目錄有未提交的變更：`skills/project-handoff/` 整個資料夾改名為 `skills/project-docs/`，其中 `SKILL.md` 與 `agents/openai.yaml` 改了名稱，以及本檔。
  - 分組指令（2026-10-13 21:19）：`2032ca0ff44d1386d3677f66f7b6ee9401cec49d`。當時工作目錄有未提交的變更：`skills/project-handoff/` 的 `SKILL.md` 與 `references/` 的 `handoff.md`、`status.md`、`readme.md`，本檔、`.gitignore`，以及新增的 `AGENTS.md`、`CLAUDE.md`；已隨 `c6a3945` 進版。
  - `lean-coding`（2026-10-13 06:40）：`0a780ae33dc9aca7a5a1f76a502d8a686fba6829`。當時工作目錄有未提交的變更：新增 `skills/lean-coding/` 的兩個檔與本檔修改，已隨 `2032ca0` 進版。

供不同 AI 工具共用的自製技能。目前收錄 `project-docs`（原名 `project-handoff`）、`lean-coding` 與 `rvc-omm-authoring`；不包含第三方技能、專案資料、金鑰或本機測試紀錄。

## 技能

| 技能 | 用途 |
| --- | --- |
| [project-docs](skills/project-docs/SKILL.md) | 整理 README、todo、status、handoff 與 ARCHITECTURE，核對事實、版本與接手範圍 |
| [rvc-omm-authoring](skills/rvc-omm-authoring/SKILL.md) | 撰寫與更新 RVC（AI 圖文回覆站）的頁面：依內容選文字、流程或比較表，套用閱讀版面、範本與補 block 片段，依條件驗收畫面；需要使用者自己的 RVC 站台專案與規範 |
| [lean-coding](skills/lean-coding/SKILL.md) | 寫程式與改程式時的輕量準則：最小充分變更、驗證力度跟著風險走、架構有需求才加；附 Cloudflare Workers 的取捨與防呆參考 |

`project-docs` 各份文件的分工：README 介紹專案與使用方法；todo 記錄待辦與安排；status 記錄實際狀態、決策與等主人處理的事；handoff 提供最新交接及下一個動作；ARCHITECTURE（選配）給要改程式的人看元件地圖、資料流與不能打破的邊界。按需求建立，不強制湊齊。

- todo 與 handoff 只在使用者親口點名時讀寫，平常不讀；文件裡寫的「先讀 todo／handoff」不算點名。
- 這些文件落後於實際進度是正常的，AI 不主動提醒；只有照文件做會出錯時才講一句。
- 判斷寫 README 還是 ARCHITECTURE：照著做就能用的寫 README；改程式之前才需要知道的寫 ARCHITECTURE。

`project-docs` 的分組指令：

| 說法 | 更新 |
| --- | --- |
| 「更新交接文件」「寫交接」「交給新對話」 | todo、handoff；另把本輪的決定與等使用者處理的事寫進既有 status |
| 「更新說明文件」 | status、README |
| 「更新文件」 | 以上四份 |
| 「更新架構文件」 | 只有 ARCHITECTURE（不屬任何分組，「更新文件」也不含它） |

分組指令涵蓋的文件不存在時，有實際內容可寫才補建，沒有就跳過並回報。README 有寫入門檻：已定案、讀者用得到、不會很快失效，三項都符合才寫入；沒有符合的就不動它，並回報。ARCHITECTURE 只寫已提交的現行結構。主機若設有架構掛勾，掛勾提示時可只更新 ARCHITECTURE 受影響的段落，這是「使用者要求才寫」的唯一例外。細節以 [SKILL.md](skills/project-docs/SKILL.md) 為準。

## 使用

```bash
git clone https://github.com/kimfull/kimiskills.git
```

本儲存庫目前是公開的（2026-10-13 確認），不需要登入即可下載。預設分支是 `dev`。

將完整的技能資料夾（例如 `skills/project-docs/` 或 `skills/lean-coding/`）放進目標 AI 工具支援的技能目錄，或讓工具明確讀取其中的 `SKILL.md`。請保留 `references/`；只複製單一 SKILL.md 會缺少細節規格。已有同名技能時先比對及備份，避免覆蓋尚未同步的修改。

支援技能載入的工具可依其介面選用技能。其他工具可以明確交辦，例如：「請先讀取這份 project-docs/SKILL.md，再依照我的要求整理專案文件。」實際自動探索、安裝位置及引用語法依各工具而定；沒有逐一驗證所有 LLM 的自動觸發。

`project-docs` 與 `rvc-omm-authoring` 的 `agents/openai.yaml` 是 Codex 介面中繼資料；不使用它的工具仍可讀取 SKILL.md 及 references。`lean-coding` 沒有這個檔。三支技能本身都不依賴模型 API、Claude 專屬指令或安裝腳本。`rvc-omm-authoring` 需要使用者自己的 RVC 站台專案與規範；找不到可發布的專案時只做候選、不發布。

## 同步與維護

- 這份 GitHub 儲存庫作為分發來源；更新技能時先修改、驗證，定案後推送並同步到需要使用的環境。
- `git pull --ff-only` 只更新 clone；不會自動覆寫各工具既有的已安裝副本。
- 從舊名稱 `project-handoff` 升級：裝好 `project-docs` 之後，移除已安裝的 `project-handoff`，否則新舊兩支會同時被觸發。全域規則檔若寫了舊名稱或舊路徑，一併改掉。
- 首次匯入（2026-10-12）沒有變更來源主機的已安裝技能或既有連結，也沒有新增定時同步、hook 或部署工作。收錄 `lean-coding`（2026-10-13）同樣只新增檔案，各環境的安裝另行處理。
- 各環境繼續遵守自己的專案規範與授權。只要求交接文件，不代表授權執行待辦、提交、推送、部署或外部筆記同步。

## 驗證範圍

`project-docs`（當時名稱 `project-handoff`；沿用 2026-10-12 的紀錄，這次沒有重新確認）：本包以既有已通過 QA 的 handoff 規格為基礎，另調整環境規範及永久知識庫的固定名稱依賴。發布前核對技能格式、相對連結、完整檔案清單與獨立 QA；這些檢查不等於不同 AI 工具的實際觸發驗收。

`project-docs` 的分組指令與 README 寫入門檻（2026-10-13）：

- 已核對：方案與成品各經一次獨立 QA。方案的兩項必修已納入；成品沒有必修，採納的措辭修正改完後沒有再審。逐情境走查十種下指令的情況；相對連結與錨點。
- 沒有驗證：各 AI 工具對新說法的實際觸發；在實際專案上試跑。

`project-docs` 改名（2026-10-13）：

- 已核對：改名方案與成品各經一次獨立 QA，成品沒有必修；儲存庫內的舊名稱只剩歷史紀錄、改名紀錄與「原名」註記；技能內部的相對連結與本檔的連結都指得到。
- 沒有驗證：各 AI 工具在新名稱下的實際觸發；其他電腦的安裝。

`lean-coding`（2026-10-13）：

- 已核對：技能格式；32 個外部連結；關鍵技術敘述對照 Cloudflare 官方文件；與前一版逐條比對規則；獨立 QA，兩項必修已修正並複驗通過。
- 已實測：三個小型測試專案上，前一版與這一版各跑一次，結果幾乎相同；在 Claude Code（Opus 5.5）上的觸發測試，該選中的 30 次全部選中，不該選中的 30 次沒有誤選。實測之後依 QA 意見改回 8 處措辭，沒有重測。
- 沒有驗證：與「不安裝這支技能」相比的效益；Codex 與其他 AI 工具的觸發；受試者能執行命令時的驗證行為。

`rvc-omm-authoring`（2026-10-18）：

- 已核對：方案與成品各經獨立 QA（多輪），必修都已修正並複驗；技能格式與相對連結；在真實站台外框以 1350／450／375／640／641px 量測寬度上限、手機左右留白、各項間距、清單、程式碼、長字串與補 block，並人工看截圖。
- 沒有驗證：各 AI 工具對自然語言的實際觸發；Windows 等其他電腦的安裝與發布。
