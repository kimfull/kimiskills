# Prove：宣稱完成前收齊證據

原則：`prove-it-works`——對真實產物驗證，禁止代理指標與自述。

## 內迴圈（單一任務）

```text
實作 → 在真實 App／真實表面驅動 → 看證據 → 修正 → …直到過關
```

完成定義＝**有證據**，不是「程式看起來合理」「編譯過了」「我已套用原則 X」。

## 步驟

1. **對應功能**：這次變更碰到 Feature Map 哪幾個功能檔？沒有 Map 就自己寫一句「使用者怎麼碰到這個變更」。
2. **判斷變更類型**（見下表，可多選）→ 決定最低證據。
3. **Bug fix 先 repro**：修之前在 main 或基線重現成功並存證據；重現不了就不要宣稱修好。
4. **Launch → Doctor**：有 `verify-<app>` 就照它；沒有就用 repo 文件化的啟動指令，並記 PID 以便只清自己的東西。
5. **記 baseline**：動作前的可觀測狀態。
6. **Drive**：走真實使用者路徑，記下每個 action。
7. **記 result + side-effects**：畫面／輸出，再加持久化、網路、檔案、DB 的實際變化；儲存類要**再讀回**。
8. **Cleanup**，再確認證據仍在。
9. **寫 packet**：`.verify-evidence/<YYYYMMDD-HHMMSS>-<slug>/packet.md`。
10. **回報**：結論＋證據路徑＋**尚未驗證**清單。

## Evidence 標準

1. 走真實使用者路徑，不走捷徑。
2. 捕捉 action + resulting state，不只最後一張截圖。
3. 驗證副作用，與畫面並重。
4. Mock 只用在生產環境本來就隔離外部系統的邊界。
5. dry-run／test mode 要**觀察**實際跳過什麼（檔案、網路、git refs），不靠名稱。
6. 證據路徑寫明；Cleanup 不吃證據。

## Evidence packet 範本

```markdown
# Evidence: <變更一句話>
- 日期：YYYY-MM-DD HH:MM
- 變更類型：UI / CLI / 儲存 / 效能 / API / Bug fix / 重構
- 對應功能：features/<feature>.md

## baseline
<動作前狀態；不適用要寫原因>

## action
<指令、selector、點擊路徑，逐步>

## result
<畫面／輸出／exit code；附檔名>

## side-effects
<DB 列、檔案、網路請求、送出的訊息；或「已查，無」並說怎麼查的>

## reproduce
<別人可直接貼上重跑的指令>

## 尚未驗證
<stand-in 多做的步驟、沒覆蓋到的入口或狀態>
```

## 依變更類型的最低證明

| 變更類型 | 最低證明 |
|----------|----------|
| **UI** | 完整使用者路徑＋結果狀態（必要時含成功／取消／錯誤／空狀態／持久化路徑）；截圖、DOM 或 a11y snapshot；不要只留最後一屏 |
| **CLI／TUI** | 指令、stdout／stderr、exit code；互動流程用 PTY transcript |
| **儲存／持久化** | 寫入後**再讀回**；必要時 reload／重啟後再確認仍在 |
| **效能** | 同一方法的 baseline vs treatment；說明瓶頸（limiter）；排除測到別的東西（explain-the-number） |
| **API／服務** | HTTP／RPC 回應**加上**後端狀態（DB 列、佇列、檔案、副作用） |
| **Bug fix** | 先在基線 repro 成功 → 修 → 證明 repro 消失；兩段都附證據 |
| **重構（行為不變）** | 改前改後的對等行為證明；不能只靠「測試綠了」而沒有使用者可觀測的對照 |

## 不算證明的東西（代理指標）

- 「編譯過了」「型別檢查過了」「測試綠了」（必要，但不充分）
- 檔案 mtime 變了
- agent 自述「已完成」「已套用原則 X」
- 快取的舊截圖、別的分支的截圖
- 只看 process 有回應、health endpoint 回 200

## 卡住時

- 同一層失敗兩次 → 升級手段（換驅動方式、讀更多原始碼、加 log），不要第三次硬撞。
- 兩個以上修法都卡同一閘門 → 寫下它們共享的前提，直接測那個前提（attack-the-premise）。
- 驗證需要不可逆動作（真的扣款、對外發訊息、動正式環境 DB）→ 停下來問主人，或改用生產環境本來就有的隔離邊界（sandbox 金鑰、測試頻道）。
- 真的無法驗證 → 明說哪一段沒驗證、為什麼、主人要怎麼補驗。**不得默默當作通過。**
