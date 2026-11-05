# Create：為專案建立驗證 skill

對應 pstack 的 `/create-verification-skill`。產出放在專案內：

```text
<repo>/.claude/skills/verify-<app>/
  SKILL.md            # Launch／Doctor／Drive／Evidence／Cleanup／Helpers
  features/
    README.md         # 功能索引
    <feature>.md      # 每個使用者可見功能一檔（先 3–5 個）
  scripts/            # helper（選用；呼叫方式必須寫在 SKILL.md）
```

範本：`../templates/verify-skill-template.md`、`../templates/features-README-template.md`、`../templates/feature-template.md`。

**寫給下一個冷讀的 agent，不是寫給人看的散文。** 沒有自己跑過一次的產物＝草稿，不是交付物。

---

## 步驟 0：前置條件

- [ ] 專案本來就能 build、能啟動嗎？不能 → 先修，或精準回報卡在哪，**不要對壞底座寫 skill**。
- [ ] 若是無關的缺失資產擋住啟動（例如缺一張圖、缺一份 seed），可在 skill 裡建立它，標成 *verification scaffolding*，並在 Cleanup 移除。
- [ ] 確認 `<app>` 名稱：用 repo 或產品名，小寫連字號，例如 `verify-myapp`。

## 步驟 1：Interview the repo（先問程式庫，少問人）

從程式庫回答五個面向；只有觀察不到的才問主人。大型 repo 用唯讀子代理（`Explore`）並行掃，主線只收結論。

| 面向 | 要釐清什麼 | 去哪找 |
|------|------------|--------|
| **Surface** | 使用者真的碰到什麼？Web UI／CLI／TUI／桌面／API／行動／函式庫。可有多個：選一個主表面，其餘註記 | routes、`package.json` 的 `bin`、README |
| **Run** | 本地怎麼啟動？ports、env、seed、auth | package scripts、Makefile、README、`docker-compose.yml`、`wrangler.toml` |
| **Drive** | Agent 怎麼程式化操作？**先用既有 harness**（Playwright、Cypress、expect、PTY helper、可 curl 的 endpoint、debug port）；沒有才選通用配方 | `e2e/`、`tests/`、`playwright.config.*`、devDependencies |
| **Observe** | 能抓什麼證據？截圖、終端機 transcript、回應 body、log、exit code、DB 狀態、網路、trace | log 設定、DB client、CLI 輸出格式 |
| **Isolate** | 兩個 instance 能否並存（ports、data dirs、profiles）？ | 設定檔裡寫死的 port、資料目錄 |

- Isolate 做不到 → 在 skill 寫明：**拒絕 double-drive 共用 instance，勝過弄髒使用者正在用的 session**。
- 記下要用到的祕密名稱（env var 名），**不讀、不輸出 `.env` 內容**。

## 步驟 2：寫 `SKILL.md` 六大段

Frontmatter 必備 `name: verify-<app>` 與 `description`（寫清 app、主表面、何時用），否則註冊不上。

### Launch

- [ ] 啟動驗證用 instance 的**精確指令**（複製貼上就能跑）。
- [ ] **Ready 條件**是「可用狀態」：特定 log 行、prompt、某個 endpoint 回出真資料。不是「process 有回應」——DB health 可能過了但 migration／seed 還在跑。
- [ ] 從**空的 data dir** 也能到可用狀態（含 migration、seed）。
- [ ] 啟動時把自己的 PID 記到 `.verify-run/`（Bash 用 `$!`；PowerShell 用 `Start-Process -PassThru` 的 `.Id`）。
- [ ] 寫明 teardown。
- [ ] 短命 CLI／TUI：沒有常駐 server。Launch＝建好 binary／裝好依賴一次，之後每次 Drive 用獨立的 PTY／tmux session。

### Doctor

- [ ] **唯讀**檢查：「這個 instance 還值得 Drive 嗎？」
- [ ] 典型項目：process 還在、版本／build 對、port 是我們開的、auth 有效。
- [ ] 寫明：任何看起來不對勁時，**先跑 Doctor**；失敗後 relaunch 再 Doctor。

### Drive

- [ ] 寫本 repo **真實的** selector、指令、route，**禁止留 placeholder 範例**。
- [ ] 優先穩定手柄：ARIA label、`data-*` attribute、prompt 字串、route path；避免座標與 Tab 順序。
- [ ] 走真實使用者路徑，不用內部 setter、test-only endpoint。

### Evidence

把下列標準寫進 skill 正文：

1. 走真實使用者路徑，不走捷徑。
2. 捕捉 **action + resulting state**，不要只留最後一張截圖。
3. 驗證副作用（檔案寫入、資料列插入、訊息送出），與畫面並重。
4. Mock 只用在生產環境本來就隔離外部系統的邊界。
5. 名稱叫 dry-run／test mode 不夠：要**觀察**它實際跳過什麼（檔案、網路、git refs）。有些 dry-run 仍會連網或開瀏覽器。
6. 證據路徑寫死（預設 `.verify-evidence/<YYYYMMDD-HHMMSS>-<feature>/`），每次附一份 `packet.md`（baseline／action／result／side-effects／reproduce）。

### Cleanup

- [ ] 只停**自己啟動**的東西（依 `.verify-run/` 記下的 PID）；**禁止依 process name 亂殺**。
- [ ] 清 instance 與 `.verify-run/` 暫存；要當證據的 log 先複製到證據目錄再清。
- [ ] 證據目錄**不在** Cleanup 範圍內。
- [ ] 每次失敗迭代後也要 Cleanup，避免卡 port、殭屍 process。

### Helpers

- [ ] 附帶的腳本必須可執行，**呼叫方式寫在 SKILL.md 正文**。
- [ ] 讀者還要反推才會用的，不算 helper。
- [ ] 重複的手動操作做成小 CLI（build-the-lever），品質條見 `principles.md` §4。

## 步驟 3：Feature Map（物化記憶）

- [ ] `features/README.md`：索引，每列一個功能檔＋一句話說明＋主表面。
- [ ] 每個使用者可見功能一檔；**先做 3–5 個主功能**（從 routes、commands、選單、文件辨識）。
- [ ] 每檔四個 H2，**順序固定**：
  1. `## Sub-features`
  2. `## How to get to it (user POV)`
  3. `## Driving it with <harness>`（真實指令／selector）
  4. `## Gotchas`
- [ ] 從使用者觀點回答：是什麼、怎麼走到、harness 怎麼開、什麼可觀測終態算過關。
- [ ] Seed 缺 precondition → journey **報失敗**，原因寫進 Gotchas；**禁止為了過關削弱 journey**。
- [ ] 功能有多個入口 → 每個入口都要能證明；只證明「最方便那一個」＝不完整。

Map 是給 agent 的壓縮索引，程式庫才是最終紀錄。App 一變 Map 就會漂，所以交付時一定要告訴主人維護入口（Maintain）。

## 步驟 4：自己 end-to-end 跑一次（交付條件）

依序：

1. Launch
2. Doctor
3. Drive **一個**已映射功能（一個就夠，其餘之後靠 Maintain 覆蓋）
4. Capture Evidence（寫 `packet.md`）
5. Cleanup
6. **確認 Cleanup 後證據仍在指名位置**（列出目錄內容當證明）

- 中途失敗：先 Cleanup，再修，再從 Launch 重來。
- 用了 stand-in（容器代替 VM、本地代替遠端）→ 列出 stand-in 多做、真實目標不會自動有的步驟；那些步驟在真實目標跑過前都標「未驗證」。

## 步驟 5：收尾

- [ ] `.verify-evidence/`、`.verify-run/` 已加入 `.gitignore`（告知主人有改這一行）。
- [ ] 跑過 `checklists.md` 的「附錄 B：Create 交付勾選」。
- [ ] 回報：skill 路徑、Feature Map 清單、自跑證據路徑、未驗證項、維護入口（說「維護 Feature Map」即可觸發）。
- [ ] 不 commit、不 push，等主人下令。
