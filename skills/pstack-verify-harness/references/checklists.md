# 檢查清單與常見失敗

## 附錄 A：證據檢查清單（任務宣稱完成前）

- [ ] 已對應到 Feature Map 中的功能檔（或多個）；沒有 Map 就寫明使用者怎麼碰到這個變更
- [ ] Doctor 通過（或剛 relaunch 後再 Doctor）
- [ ] 走真實使用者路徑（不是內部 setter／test-only）
- [ ] 有 baseline（或寫明為何不適用）
- [ ] 有 action 紀錄（指令／selector／步驟）
- [ ] 有 resulting state（畫面／輸出／狀態）
- [ ] 副作用已查（變更會動到持久化／網路／檔案時）
- [ ] 證據路徑寫明；Cleanup 後抽查仍在
- [ ] 證據類型符合變更類型（`prove-it-works.md` 表格）
- [ ] 白話說明裡標出**尚未驗證**的項目

## 附錄 B：Create 交付勾選

- [ ] Interview 五面向都有答案（Surface／Run／Drive／Observe／Isolate）
- [ ] `SKILL.md` 含 Launch／Doctor／Drive／Evidence／Cleanup／Helpers，沒有 placeholder
- [ ] Frontmatter 有 `name`、`description`（寫清 app、表面、何時用）
- [ ] Feature Map：README + 至少 3–5 個功能檔，四個 H2 齊全且順序正確
- [ ] 已自跑：Launch → Doctor → Drive 一個功能 → Evidence → Cleanup
- [ ] Cleanup 後證據仍在
- [ ] stand-in 多做的步驟已標「未驗證」
- [ ] `.verify-evidence/`、`.verify-run/` 已加入 `.gitignore`
- [ ] 已告知維護入口（Maintain）

## 附錄 C：Maintain 交付勾選

- [ ] 結果標成 `clean`／`changed`／`blocked` 之一
- [ ] 每個 feature 都有 source 覆蓋
- [ ] Live pass 覆蓋每個 feature（或標 `verified-unreachable` + 具體前置條件）
- [ ] 沒改產品程式碼
- [ ] 產品回歸另外回報，沒寫進「讓文件過關」的修正
- [ ] `changed` 時只有一組、且已重讀過的修正

## 常見失敗與修正

| 失敗 | 原因 | 修正 |
|------|------|------|
| 有一堆 skill 仍不可信 | 只有文字，沒有客觀完成閘 | 先建 harness＋證據標準，再加自動化 |
| 只截最後一屏 | 沒記路徑與副作用 | baseline／action／result／side-effects；必要時 reload |
| Feature Map 漂移 | 產品變了沒人維護 Map | 定期 Maintain；功能變更同一批改動更新 Map |
| Eval 結果太完美 | 候選知道自己在考試 | 盲測、清掉洩題字、跨家族 judge |
| 多 agent 難合併 | Brief 模糊、沒接受條件與驗證指令 | 標準化 brief：目標、範圍、接受條件、驗證指令 |
| CI 變成幾百條散亂規則 | 逐 bug 加規則、沒有架構 | 先定領域邊界與目錄形狀；lint 只編碼真不變式 |
| 照抄別人產品的政策 | 把局部不變式當通用最佳實務 | 留原則；自測自己的失敗模式 |
| 長計畫仍做錯 | 計畫沒回答可觀測問題 | 先 prototype／benchmark／真機驗證再鎖設計 |
| 為讓文件過關掩蓋回歸 | Maintain 時改 Map 迎合壞掉的行為 | 產品回歸單獨回報；Map 只反映真實或標 unreachable |
| 生成 verify skill 卻沒自跑 | 交付的是草稿 | Launch → Doctor → Drive → Evidence → Cleanup，且證據倖存 |
| Cleanup 殺錯 process | 依 process name 殺 | 只依 `.verify-run/` 記下的 PID 停自己啟動的東西 |
| Ready 判斷太早 | 只看 process 有回應或 health 200 | Ready 條件改成「可用狀態」（特定 log 行、能回真資料） |
