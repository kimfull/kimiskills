# 方法論與原則

## 1. 信任階梯（Trust curve）

目標不是「一次開很多 agent」，而是**先讓單一 agent 可被信任**，並行才會變成乘數。

| 階 | 人在做什麼 | Agent 已有什麼 | 主要風險 |
|----|------------|----------------|----------|
| 1. 盯每個 tool call | 讀每一步、手動複驗 | Model + repo | 亂猜、漏讀程式、過早宣稱完成 |
| 2. 本地驗證 | 看 agent 自己跑 App 收證 | Harness + 驗證 skill | Harness 不穩、功能難定位 |
| 3. Skills + evals | 把失敗類型做成 skill，再測 skill | Skill、rubric、盲測 eval | 過擬合單一 model／情境 |
| 4. 雲端並行 | 收報告與證據，不盯逐步 | 隔離環境 + 共用驗證標準 | 成本、環境漂移、協調 |
| 5. 有護欄的自動合併 | 主要審例外 | 強制 CI、lint、review bot、驗證 | 缺約束時錯誤仍漏網 |

**硬規則：並行是信任的結果，不是信任的替代。** 開 10 個沒有客觀完成條件的 agent，只是把「要人盯的東西」乘以 10。

判斷現在在哪一階：專案有沒有 `verify-*`、有沒有 Feature Map、agent 交付時有沒有 evidence packet。沒有就停在第 1–2 階，先補驗證，不要先開量。

## 2. 內／外迴圈

- **內迴圈**（單一任務）：實作 → 驅動真實表面 → 看證據 → 修正 → 直到過關。
- **外迴圈**（入口）：Slack／信／票單／口頭需求 → 澄清 intent → 派給內迴圈 → 回報含證據。外迴圈可以自動化（triage → reproduce → fix），但**每個 worker 都走同一套驗證契約**，否則只是把噪音加速。
- 派子代理時，brief 要標準化：目標、範圍、接受條件、驗證指令。

## 3. Verification 和傳統測試的差別

| 機制 | 回答的問題 |
|------|------------|
| Unit test | 函式／模組結果是否符合預期 |
| Integration test | 模組之間是否接得上 |
| E2E test | 預寫好的使用者流程是否跑通 |
| **Verification skill** | **Agent 在任務中能否自己找到、啟動、驅動真實表面、觀察並證明行為** |

Verification **不取代** test suite；它補上「工程師當場調查」那一層。

## 4. Build the lever

把重複的手動操作做成**小 CLI**（或同等可重跑工具），不要每次讓 agent 現場寫一次性腳本。

命令族形狀（示例，不是固定 API）：

```text
control-app doctor
control-app open settings
control-app click "Save"
control-app snapshot --json
control-app screenshot .verify-evidence/<run>/settings-after.png
control-app trace --duration 10s
control-app network-summary
control-app cleanup
```

分組：inspection（snapshot／screenshot）、navigation、interaction（send／click／press）、performance（trace／profile）、health（doctor／cleanup）。

Agent 友善 CLI 品質條：

- [ ] 可組合的深度指令，不是一堆互不相干的腳本
- [ ] 錯誤訊息告訴下一步怎麼復原
- [ ] `--help` 夠用
- [ ] 機讀輸出（JSON）
- [ ] 危險操作有 `--dry-run`，且 dry-run 行為用觀察驗證過
- [ ] 所有碰這個 App 的 agent 與人共用同一支 CLI

重點是**契約**，不是抄某個產品的實作。

## 5. 最短路徑＝正確路徑

Agent 天生選短路徑。與其在 prompt 叫它「別抄近路」，不如讓**合法的最短路徑剛好就是正確路徑**。

執法層級（強 → 弱）：

```text
架構與目錄形狀
  → 型別／編譯／靜態分析
    → lint／硬 CI
      → review bot
        → skill／文件／prompt
          → 人工評論（最弱）
```

- `AGENTS.md`／`CLAUDE.md` 裡的提醒可以被忽略；**讓 CI 失敗的規則**過不去。
- 重複出現的 review comment＝流程臭味 → 升級成機器可檢查的不變式。
- **encode-lessons-in-structure**：同一個指示寫第二次 → 改成機制（lint、檢查、腳本、目錄形狀、hook），然後刪掉文字。Claude Code 可用的機制：hooks（`settings.json`）、CI、lint 規則、型別、`verify-*` 的 Doctor 檢查。
- 修重複錯誤的順序（由強到弱）：架構 → 型別 → lint／CI → tests → 文件最後。
- 別人產品的具體禁令（例如禁某種 hook、禁註解）是**局部不變式範例**，不是通用教條。移植原則，自己量自己 codebase 的失敗類型。

## 6. 該量什麼（不要拿 PR 數當 KPI）

| 指標 | 意義 |
|------|------|
| Verification coverage | 重要使用者流程有穩定驅動方式與證據標準的比例 |
| Reproducibility rate | 報錯中 agent 能不靠人手自行 repro 的比例 |
| First-pass evidence completeness | 第一次交付就齊 baseline／action／result／side-effects 的比例 |
| Human intervention rate | 需要人中途接手或改方向的比例 |
| Regression escape rate | 驗證＋CI 後仍漏出的回歸比例 |
| Skill eval pass rate | 跨 model／情境下 skill 過 rubric 的比例 |

## 7. Evals：skill 也要測

Skill 寫得漂亮，仍可能讓 agent 變差。Eval 就是 skill 的 unit test。

1. 定要測的變體；寫 **3–6 條**具體 rubric。
2. 每個候選獨立環境；目錄名與 prompt 要**自然**，避開 `eval`、`judge`、`benchmark`、`candidate` 等洩題字。
3. 所有候選做同一個自然任務。
4. 並行跑；適合時用不同 model 家族。
5. Judge 用**另一家族**的 model，只看匿名化輸出。
6. 看 **transcript 與真實產物**，不看「我已套用原則 X」的自述。
7. 協調者複核；和 judge 不一致＝rubric 模糊或評分偏差的訊號。

要量的行為不只答案對不對：有沒有讀夠相關程式、有沒有真的做驗證、資料結構合不合適、有沒有堆多餘抽象。用觀測結果迭代 skill，不憑「新說明聽起來比較好」。

## 8. 工作流行為（移植 pstack 路由器的契約）

不必裝整包 pstack，移植的是行為：

| pstack 動作 | 在 Claude Code 的做法 |
|-------------|------------------------|
| `/poteto-mode` 路由 | 讀任務 → 選流程（本 skill 的 Create／Maintain／Prove）→ 開 todo（步驟照抄）→ 需要時叫其他 skill |
| `/in-your-own-words` | 開工前用自己的話重述目標，讓主人早點修正誤解 |
| `/how`、`/why`、`/teach` | 機制（how）、歷史意圖（why，查 git log、票單、文件）、合成說明 |
| `/architect` | 跨邊界前從 call sites、型別形狀、公開簽名出發；多方案並行 → 交叉評分 → 再實作 |
| Prototype／exhaust-the-design-space | 用便宜實驗回答**可觀測**問題；無先例時 2–3 原型並排；保留決策、丟棄草稿 |
| `/correct` | 挖重複犯錯類型，由強到弱修（見 §5） |
| `/reflect` | 長任務後把配方寫回 `verify-*` 或對應 skill |
| `/bro` | 白話重述，標出**尚未驗證**什麼 |
| `/show-me-your-work` | 可審的決策軌跡 |

Architect 紅旗（退回方案集，不要硬補）：實作時不斷加沒預期的參數、多處同一種繞法、型別系統被迫用 `any`／強制轉型才過。

規則感：

- 失敗兩次 → 升級手段；必要時 attack-the-premise。
- 合併、花錢、對外發文 → 要人核准（另依使用者規則：commit／push／部署也要）。
- 可逆的工作 → never-block-on-the-human：先做完再呈現，讓人事後修正。
- 大量閱讀／掃描 → guard-the-context-window：交給子代理，主線只留摘要。

## 9. 原則精要（官方 24 條；舊文常寫 23）

用法：看到情境就套用名稱，並在回覆寫出「這條原則改變了哪個決策」。不要空喊原則名。

**Core**

| 原則 | 實務意義 |
|------|----------|
| `laziness-protocol` | 偏向刪除與最小有效變更 |
| `foundational-thinking` | 先選核心型別／資料結構與 scaffold 順序，再寫邏輯 |
| `redesign-from-first-principles` | 新需求當作第一天就存在來設計，不外掛硬黏 |
| `attack-the-premise` | 多個修法都卡同一閘門 → 寫下並直接測共同前提 |
| `subtract-before-you-add` | 先清死重、多餘驗證、stub，再往上建 |
| `minimize-reader-load` | 減少問答之間的層數與讀者腦中的隱藏狀態 |
| `outcome-oriented-execution` | 大改／遷移對準目標架構，不用拋棄式相容層粉飾中間態 |
| `experience-first` | 使用者結果優於實作方便；少而精勝過多而糙 |
| `exhaust-the-design-space` | 無先例時做 2–3 個原型並排 |
| `build-the-lever` | 做可重跑工具／skill 來做或證明工作 |

**Architecture**

| 原則 | 實務意義 |
|------|----------|
| `model-the-domain` | 領域規則進結構，不散落在 if |
| `boundary-discipline` | 守衛集中在系統邊界；內部信任型別；業務邏輯趨向純函式 |
| `type-system-discipline` | 非法狀態不可表示；外部資料在邊界 parse；窮盡變體 |
| `make-operations-idempotent` | 重試收斂到同一終態 |
| `migrate-callers-then-delete-legacy-apis` | 遷移呼叫端與刪舊 API 同一波 |
| `separate-before-serializing-shared-state` | 先消除共享；真需要單一寫入者才序列化 |

**Verification**

| 原則 | 實務意義 |
|------|----------|
| `prove-it-works` | 對真實產物驗證；禁止代理指標與自述 |
| `fix-root-causes` | 重現並追到系統第一次出錯處；守衛只在該狀態合法時才算修 |
| `sequence-verifiable-units` | 多步驟工作切成每段結尾都可驗證 |
| `test-behavior-not-implementation` | 斷言使用者可觀測的行為 |
| `explain-the-number` | 報數字前先說瓶頸，排除測錯東西 |

**Delegation + Meta**

| 原則 | 實務意義 |
|------|----------|
| `guard-the-context-window` | 大宗工作給子代理；主線留摘要 |
| `never-block-on-the-human` | 可逆的先做；不可逆才等核准 |
| `encode-lessons-in-structure` | 重複教訓變成 lint／檢查／腳本／目錄形狀 |

## 10. 廚房比喻（記架構用）

| 角色 | 對應 |
|------|------|
| 人 | 訂標準、口味、不可逆決策（合併、花錢、對外發文） |
| Skill／CLI（lever） | 刀具與量杯：可重跑、可機讀 |
| Feature Map | 菜單與動線圖：功能在哪、怎麼走到、怎麼驅動 |
| 程式庫約束 | 廚房動線與禁區：最短合法路徑＝正確路徑 |
| Evidence packet | 出餐證明：可複驗的產物，不是「看起來像」 |
