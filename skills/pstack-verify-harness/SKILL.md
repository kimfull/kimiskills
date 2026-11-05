---
name: pstack-verify-harness
description: 讓 agent 自己證明工作做對的驗證方法論（移植自 Lauren Tan 的 pstack，概念對齊 Launch／Doctor／Drive／Evidence／Cleanup、Feature Map、信任階梯）。三種用法：(1) 為專案建立驗證 skill 與 Feature Map；(2) 維護既有驗證 skill，讓 Feature Map 與 harness 對齊產品現況；(3) 宣稱完成前依變更類型收齊證據（prove-it-works）。主人說「建立驗證 skill」「幫這個專案做 verify skill」「維護 Feature Map」「驗證 skill 漂移了」「證明它真的能動」「拿出證據」「prove it works」「create／maintain verification skill」，或問 pstack、信任階梯、驗證方法論時使用。不用於單純寫 unit test 或只跑既有測試。
metadata:
  version: "1.0"
  source: "Lauren Tan 的 pstack 驗證方法論（2026-11-04 整理移植）"
---

# pstack-verify-harness｜讓 agent 自己證明做對

**核心命題：瓶頸在驗證，不在生成。** Agent 會寫程式、會跑測試；但只要還得靠人打開 App、重走流程、截圖、查副作用，人就是吞吐上限。本 skill 讓 agent 在任務中自己啟動真實表面、驅動功能、收可複驗的證據，人才能把流程交出去。

使用者規則與專案規則（`CLAUDE.md`、`AGENTS.md`）優先於本 skill。本 skill 不擴大任何權限：commit、push、開 PR、部署、花錢、對外發文、刪資料，一律照使用者規則等核准。

## 1. 路由：先判斷走哪條路

先在專案根目錄找既有驗證 skill：`.claude/skills/verify-*/SKILL.md`（Claude Code 慣例）。舊 Cursor 專案可能放在 `.cursor/skills/verify-*/`，只當參考讀，要移植時照 Create 流程搬到 `.claude/skills/`。

| 情境 | 走哪條 | 讀哪份 |
|------|--------|--------|
| 專案還沒有 `verify-*`，主人要「建立驗證 skill」 | **Create** | `references/create-verification.md` |
| 已有 `verify-*`，產品改過、Map 可能漂移、主人要「維護」 | **Maintain** | `references/maintain-verification.md` |
| 任何變更要宣稱「完成」 | **Prove** | `references/prove-it-works.md` |
| 問方法論、原則、信任階梯、evals、怎麼做 CLI lever | 說明 | `references/principles.md` |
| 交付前逐項勾選、對照常見失敗 | 清單 | `references/checklists.md` |

- Maintain 找不到目標 `verify-*` → 指向 Create，不要自己發明目標。
- Prove 時有 `verify-*` 就用它的 Launch／Doctor／Drive／Cleanup；沒有就照 `prove-it-works.md` 臨時驅動，但證據標準不降。同類臨時驅動第二次出現 → 建議主人走 Create（build-the-lever）。
- 建立專案驗證 skill 的範本在 `templates/`。

## 2. 六條不變式（三條路都適用）

1. **完成＝證據，不是感覺。** 「編譯過了」「測試綠了」「我已套用原則 X」、mtime、舊截圖，都不算證明。
2. **走真實使用者路徑。** 不用內部 setter、test-only endpoint、捷徑來當證明。
3. **Cleanup 不吃證據。** 證據放在寫死的位置，Cleanup 後抽查仍在。
4. **失敗兩次就升級手段**，不在同一層硬撞第三次；兩個以上修法都卡在同一閘門 → 寫下共同前提並直接測它（attack-the-premise）。**不可逆動作等人。**
5. **Maintain 不掩蓋產品回歸。** Map 描述的行為 App 不做了：要嘛修 Map（文件漂移），要嘛另報回歸；禁止改文件讓它「過關」。
6. **並行前先有本地可信任的驗證。** 並行是信任的結果，不是信任的替代。

## 3. 完成閘：Evidence packet

宣稱完成前，每項變更交出這五欄（某欄不適用要寫原因）：

| 欄位 | 內容 |
|------|------|
| baseline | 動作前可觀測狀態 |
| action | 做了什麼（指令、selector、點擊路徑） |
| result | 動作後的畫面、輸出、狀態 |
| side-effects | 持久化、網路、檔案、DB 的實際變化 |
| reproduce | 別人可重跑的指令 |

證據種類要對得上變更類型（UI／CLI／儲存／效能／API／Bug fix／重構），表格在 `references/prove-it-works.md`。

## 4. Claude Code 對應

| pstack 概念 | 在 Claude Code 怎麼落地 |
|-------------|--------------------------|
| `.cursor/skills/verify-<app>/` | 專案內 `.claude/skills/verify-<app>/SKILL.md` + `features/`（跟著 repo 版控） |
| 證據位置 | 預設 `<repo>/.verify-evidence/<YYYYMMDD-HHMMSS>-<feature>/`；暫存（PID、暫存資料目錄、log）放 `<repo>/.verify-run/`；兩者都加進 `.gitignore` |
| Drive：Web／Electron | 先用 repo 既有 Playwright／Cypress；沒有才用 chrome-devtools MCP（`take_snapshot` 拿 a11y 樹、`take_screenshot`、`list_network_requests`）或自寫 Playwright 腳本 |
| Drive：CLI | Bash／PowerShell 直接跑，記 stdout、stderr、exit code |
| Drive：TUI／互動 CLI | Linux／macOS 用 tmux；Windows 先找 repo 既有 harness，否則用 node-pty／pywinpty 腳本或 WSL 內的 tmux |
| Drive：API／服務 | `curl`／`Invoke-WebRequest` + 唯讀查後端狀態（DB、佇列、檔案） |
| Source wave、大量閱讀 | Agent 工具派唯讀子代理（`Explore`）並行；主線只收摘要（guard-the-context-window） |
| 內建 `run` skill | 它會先找「專案已有的 launch skill」；`verify-<app>` 就是那份，兩者互補 |
| pstack 的「開一個 PR」 | 在 Claude Code ＝ 工作區裡一組已重讀過的改動；主人下令才 commit／push／開 PR |

## 5. 回報格式

1. 第一行結論：做完了沒、證據在哪個路徑。
2. Evidence packet 摘要（不貼整包，給路徑）。
3. **尚未驗證的項目**逐條列出（含用了 stand-in 的步驟，例如本地代替遠端、容器代替 VM）。
4. Maintain 時標明結果 `clean`／`changed`／`blocked`。

## 6. 來源限制

方法論整理自公開貼文、pstack 官方 skill 與 README、`poteto/verification-skill-example`、blog.lionet.vn 筆記。原始 workshop 影片未完整分析；「每月約 2000 PR」等產量數字是作者自述，不是獨立 benchmark。路徑與工具已改成 Claude Code 慣例，概念與契約不變。
