# Maintain：維護驗證 skill 與 Feature Map

對應 pstack 的 `/maintain-verification-skill`。

**目的：** 讓 Map 與 harness 對得上**現況產品**，不是讓文件「看起來過關」。

## 結果三選一（必須明示）

| 結果 | 意義 |
|------|------|
| `clean` | 每個功能都做了 source + live；沒有值得交付的修正 |
| `changed` | 一組已證明的文件／harness／Map 修正（Claude Code：工作區改動，主人下令才 commit／開 PR） |
| `blocked` | 覆蓋沒跑完，或修正無法安全交付；寫清卡在哪 |

## 編輯範圍

- **只改** verification skill 自己的目錄：`.claude/skills/verify-<app>/` 內的 `SKILL.md`、`features/`、`scripts/`。
- **禁止在維護 run 改產品程式碼。**
- Map 描述的行為 App 已經不做了：
  - 是文件漂移（產品刻意改了）→ 修 Map。
  - 是產品壞掉 → 記給主人，**不進這次修正**。
  - **禁止改文件掩蓋回歸。**

---

## 流程

### 步驟 0：定位目標

- [ ] Glob `.claude/skills/verify-*/SKILL.md`（舊專案也看 `.cursor/skills/verify-*`）。
- [ ] 找不到 → 停下，指向 Create，**不要發明目標**。
- [ ] 有多個 → 問主人要維護哪一個，或全做。

### 步驟 1：Index hygiene

- [ ] `features/README.md` 列的檔案與實際 sibling 檔一一對應（不多不少）。
- [ ] 每個功能檔四個 H2 齊全、順序正確。

### 步驟 2：Source wave（並行、唯讀）

- [ ] 每個 feature 派一個唯讀子代理（Agent 工具，`subagent_type: Explore`），同一則訊息全部送出。
- [ ] 子代理只讀原始碼，回傳：
  - 功能摘要
  - 入口（route、command、選單）
  - 可能漂移處（Map 寫的 selector／指令在原始碼還在不在）
  - 一條 live recipe（怎麼驅動、什麼終態算過關）
- [ ] 子代理**不 Drive、不改檔**。

子代理 brief 範本：

```text
目標：核對 Feature Map 檔 <path> 與現況原始碼是否一致。唯讀，不執行程式、不改任何檔。
請讀：<feature 檔完整路徑>、相關原始碼（從檔內的 route／command／selector 追）。
回傳四段：1) 功能摘要 2) 入口清單 3) 可能漂移（引用檔案:行號）4) 一條 live recipe。
不讀 .env、*.pem、credentials.json。
```

### 步驟 3：Reconcile

- [ ] 合併各子代理的 recipe。
- [ ] 抽查子代理說的漂移引用（自己開檔確認，不全信摘要）。
- [ ] 掃近期 churn（`git log --since=<上次維護日> --stat`）找 Map 漏掉的使用者表面；新功能列入「待補」。

### 步驟 4：Live pass（即使 source 看起來乾淨也必做）

依 skill 的 Launch 模型，每個功能至少 Drive 一次。全程守三個不變式：

1. **沒健康檢查過的 instance 不 Drive**：先 Doctor；失敗後再 Doctor；UI 卡住就 reset／relaunch。
2. **已抓的證據在每次 Cleanup 後仍在。**
3. **Drive 產生的殘渣不活過它的用途**（暫存資料、測試帳號、上傳檔）。

到不了的功能標 `verified-unreachable`，並寫出具體缺什麼前置條件。

### 步驟 5：Triage

| 觀察 | 判斷 | 處理 |
|------|------|------|
| user-POV 描述錯誤或缺失 | 文件漂移 | 修 Map |
| 行為正常但 harness 開不到（selector 改了、port 改了） | harness 漂移 | 修 harness／Drive 段 |
| App 真的壞了 | 產品回歸 | 記給主人（含 repro 與證據路徑），**不進這次修正** |

### 步驟 6：Ship or stop

- [ ] 只有 `changed` 才交付一組改動；交付前**重讀一遍** diff。
- [ ] 跑 `checklists.md` 的「附錄 C：Maintain 交付勾選」。
- [ ] 回報：結果（clean／changed／blocked）、每個功能的 source／live 狀態、證據路徑、另報的產品回歸、`verified-unreachable` 清單。
- [ ] 不 commit、不 push，等主人下令。

## 何時該跑 Maintain

- 功能變更時，**同一批改動**順手更新對應 Map 檔（最便宜）。
- 大改版、改路由、改 CLI 參數之後。
- Prove 時發現 Map 的 recipe 跑不通。
- 定期（例如每月）一次。
