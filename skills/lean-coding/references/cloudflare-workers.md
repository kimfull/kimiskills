# Cloudflare Workers｜取捨與防呆

查證日期：2026-10-13（連結與關鍵敘述已對照官方文件）。這是選擇與防呆指引，不是每個專案都要全部導入的服務清單。版本、限制與計價以當前官方文件為準。

依任務選讀：

| 任務 | 章節 |
| --- | --- |
| 新建專案、選框架 | 1 |
| 改 Wrangler 設定、環境、bindings、型別、密鑰 | 2、6 |
| 選儲存或背景服務 | 3 |
| 寫一般的 API／handler | 2、4、5 |
| Webhook、佇列、重試、去重、回應後的工作 | 3、4 |
| 認證、多租戶、輸入驗證、日誌 | 5 |
| 測試、建置、遷移、部署 | 6 |

## 1. 新專案的最小起點

- **一個 Worker 起步**：優先評估一個 Worker＋TypeScript＋必要的 bindings；沒有持久化需求就不加資料庫。有獨立部署、權限、擴縮或隔離需求時，才拆多個部署單位。[2] [14]
- **路由**：少量路由直接用 Fetch handler；路由與共用 middleware 明顯增加時可選 Hono，不自己寫框架。已有框架就沿用，不為本 Skill 更換。[3]
- **目錄**：清楚的入口與功能模組即可，檔案依責任自然拆分，不預建分層目錄。前端框架、ORM 與其他工具依實際需求選，不是固定套餐。
- **用 bindings 存取 Cloudflare 資源**：已配置的 D1、KV、R2、Queues 等走 bindings；Worker 之間互相呼叫走 service bindings，不繞公開網址。管理資源等 bindings 不涵蓋的操作，才另按官方 API 處理。[2] [24]
- **靜態資源**：新專案的靜態網站或全端應用用 Workers Static Assets；既有的 Pages 專案不為此遷移。[25]

## 2. 設定、型別與執行環境

- **沿用既有設定**：讀既有的 Wrangler 設定與 lockfile，沿用相同的設定格式與工具鏈。
- **型別用生成的**：新增或改名 bindings 後，用專案內的 `wrangler types` 依適用設定重新生成；不手改生成檔，也不另建一份會漂移的 Env。[14]
- **環境各自獨立**：bindings、vars、secrets 不會從頂層繼承到具名環境，要逐環境宣告。具名環境會部署成另一個 Worker（預設名稱 `{name}-{env}`），不帶 `--env` 的命令作用在頂層那一個。動到環境或 bindings 時，依實際命令、環境變數與專案工具核對有效的設定來源、目標環境、帳號／Worker、資源識別碼，不只看頂層設定或環境名稱。[21] [26]
- **程式在哪裡跑 ≠ 資料在哪裡**：本機開發可用 remote bindings（binding 設定 `remote: true`）連到已部署的資源，`wrangler dev`、Vite 外掛與 Vitest 整合都會生效，用量照常計費。逐一檢查相關 binding 的連線模式與目標，不用 localhost 或「測試」名稱推定資料安全；`wrangler dev --local` 可暫時停用全部 remote bindings。缺少高風險設定時停止相關操作，不默默退回正式資源。[22] [27]
- **compatibility_date**：新專案選當前已支援的日期；既有專案不為無關小修順手改日期或旗標。日期會改變執行行為，更新後要驗證。[17]
- **Node API**：優先用原生 `fetch`、Request／Response、Web Crypto 等能力。需要 Node API 時查實際支援並設定 `nodejs_compat`；它不保證完整的 Linux／Node 程序環境。[4]
- **密鑰**：經 secrets 注入，本機密鑰檔排除版本控制。不放進 Wrangler 的一般 vars、前端 bundle、測試輸出或日誌。[18]
- **全域狀態**：當前使用者、租戶、Request 物件等請求狀態不放模組層全域變數。純常數與安全的可重建快取可以共用，但不是可靠的持久化或全域協調來源。[1]

## 3. 儲存與背景能力：有需求才選

以下是建議對應，不是固定架構。[5] [6] [7] [8]

| 當前需求 | 優先評估 | 不該誤用成 |
| --- | --- | --- |
| 關聯資料、條件查詢、資料約束 | D1，或沿用合適的既有資料庫 | 每個 API 都必備的服務 |
| 可接受讀到舊值的快取／低頻更新的設定 | KV | 強一致鎖、即時撤權或原子去重的依據 |
| 上傳檔案、圖片、影片等物件 | R2 | 關聯式資料庫 |
| 同一實體的狀態協調、競爭處理或即時連線 | Durable Objects | 每個請求必經的通用層 |
| 需要可靠接收與重試的非同步工作 | Queues | 保證業務副作用只執行一次的系統 |
| 多步驟、需持久化狀態並可恢復的長流程 | Workflows | 不受 CPU／記憶體限制的運算主機 |

- **D1**：簡單查詢直接用參數化的 prepared statements；已有 ORM 就沿用，不另疊通用 Repository，查詢增長到確實需要抽象時再調整。[9]
- **外部資料庫**：沿用外部 PostgreSQL／MySQL 時經 Hyperdrive 連線。[28]
- **KV 是最終一致**：不以「先 get，沒有就 put」實作競爭安全的去重、扣額或鎖，也不以快取讀到的結果推定操作權。需要時用資料庫唯一約束／原子操作，或適當的狀態協調機制。[6] [10]
- **Durable Objects**：協調以物件 ID 等邊界為基礎，仍要考慮非同步交錯與錯誤復原；加一個 DO 不代表所有外部操作都有交易保證。[5] [8]
- **等待與運算分開評估**：Queues 與 Workflows 能協調工作，不能消除每個步驟的運算限制。超出 Workers 適用範圍的處理交給合適的後端，不為統一架構硬塞進 Worker。[7] [11]

## 4. 非同步、Webhook 與重試

- **影響回應的工作要等完**：影響回應正確性的工作在回應前 `await` 完成，或明確以串流／非同步契約回傳。未處理的 Promise、`void` 或 timer 不是可靠的背景工作。[1]
- **`ctx.waitUntil()` 的定位**：HTTP 請求的 `ctx.waitUntil()` 適合短暫、可容忍失敗的回應後工作。官方目前規定回應送出或連線中斷後最多延長 30 秒，同一請求的所有呼叫共用這個額度；這不是整個 HTTP 請求的總時限，也不是可靠的任務佇列。[12]
- **先存好再說收到**：需要確認已接收工作的 API，等可靠入列或持久化成功後才回「已接收」。入列成功與工作完成分開表達；遵守 Webhook 供應者要求的回覆契約。
- **Queues 至少一次**：預設至少投遞一次，重複訊息是必須處理的情境。依實際業務定義事件鍵、重試上限、失敗去向，並測試重複事件。[13]
- **Queues 不保證順序**：涉及狀態更新或先後依賴時，驗證亂序與過期事件；用可信的版本、條件更新或重新查詢權威狀態處理，不直接以抵達順序覆寫，也不只靠未驗證的時間戳判新舊。沒有順序依賴就不額外建狀態機或協調服務。[23]
- **冪等看業務副作用**：資料庫擋下重複的事件 ID，不等於外部發訊、付款也只執行一次。依供應者支援使用冪等鍵，並處理「外部已成功、本地尚未記錄」的狀態。做不到時明說重複風險，提供可觀察、可補救的處理，不虛稱 exactly-once。
- **對外請求**：設定合理逾時，檢查非成功狀態與必要的回應欄位。逾時不代表外部沒執行——區分「確定失敗」與「結果未知」，依供應者契約用查詢結果、同一冪等鍵或補救方式處理。確認可安全重試才重試，次數與時間有上限，不疊多層無限制重試。[1] [13]

## 5. 只保留必要的安全與可觀察性

- **輸入與 Webhook**：外部輸入依契約驗證，資料查詢參數化。Webhook 依供應者規範驗簽並處理重放；一段難猜的 URL 或前端檢查不算可信。[1] [9]
- **身份與租戶**：需要認證或多租戶隔離時，由伺服器確認身份、資源歸屬與租戶範圍。請求傳入的 user_id／tenant_id 不能直接信任；CORS 不是權限檢查。
- **隨機值**：token、識別碼等安全相關的隨機值用 Web Crypto（`crypto.randomUUID()`、`crypto.getRandomValues()`），不用 `Math.random()`。[29]
- **濫用防護**：昂貴或可濫用的操作依需求限制輸入大小、批次量、併發或使用額度。驗證放在實際的風險邊界，不每層重複堆砌。[1]
- **日誌與錯誤**：保留必要的請求／事件識別碼、階段與錯誤原因，遮蔽密鑰和敏感資料。不先搭大型監控平台，先讓真實失敗可查、可區分重試與完成。`passThroughOnException()` 是出錯即放行到來源站的機制，會藏住 bug，不當成錯誤處理。[1] [19]
- **大型內容**：大型檔案或長回應優先串流，不為方便一次讀進記憶體。[11] [20]

## 6. 驗證與部署邊界

先查專案 scripts 與當前工具版本再選命令。以下是候選，不是每次全部執行的清單；依本次風險選擇驗證層級。

- **型別**：bindings 改變時重新生成型別，必要時執行 `tsc --noEmit`。打包通過不等於型別檢查通過。[14] [16]
- **行為**：純邏輯沿用現有的測試工具。涉及 Workers runtime 或 bindings 時，用能覆蓋這些行為的環境，例如官方 Vitest 整合；Node mock 不能證明 Workers 整合成功。[15]
- **Vitest 整合的兩個盲點**：它預設透過 Miniflare 在本機執行，不等於已驗證遠端資源、憑證或部署設定；它會自動注入 `nodejs_compat`，程式依賴 Node 內建模組時，另外確認 Wrangler 設定真的有這個旗標。[1] [15]
- **打包**：需要時執行專案的建置流程，或當前 Wrangler 支援的 `deploy --dry-run`。這不證明遠端資源、權限或正式流量正常。[16]
- **執行前核對目標**：依第 2 節核對有效環境、資源與命令的設定來源，使用 remote bindings 的本機開發與測試尤其要看。遠端資源操作、遷移與部署只在使用者授權範圍內做；命令名稱有 dev／test 不代表沒有副作用。[21] [22]
- **各層結果分開陳述**：本機邏輯測試、Workers runtime 整合、遠端測試環境驗證、正式部署結果，寫明實際環境與未覆蓋範圍，不互相替代。設定、binding 或真實服務整合有變動時，判斷是否需要額外的已授權遠端驗證；不足就標明缺口，並擋住相關的高風險上線步驟。
- **資料結構變動**：測試遷移本身，必要時採「先相容擴增、再移除」。程式碼回滾不代表資料遷移已回滾；依風險準備備份／還原或前向修復方案。

## 來源

編號連結指向官方文件；實作取捨是本 Skill 的建議，不是平台強制的架構。

[1]: https://developers.cloudflare.com/workers/best-practices/workers-best-practices/
[2]: https://developers.cloudflare.com/workers/runtime-apis/bindings/
[3]: https://hono.dev/docs/getting-started/cloudflare-workers
[4]: https://developers.cloudflare.com/workers/runtime-apis/nodejs/
[5]: https://developers.cloudflare.com/workers/platform/storage-options/
[6]: https://developers.cloudflare.com/kv/concepts/how-kv-works/
[7]: https://developers.cloudflare.com/workflows/
[8]: https://developers.cloudflare.com/durable-objects/
[9]: https://developers.cloudflare.com/d1/worker-api/prepared-statements/
[10]: https://www.sqlite.org/lang_createtable.html
[11]: https://developers.cloudflare.com/workers/platform/limits/
[12]: https://developers.cloudflare.com/workers/runtime-apis/context/
[13]: https://developers.cloudflare.com/queues/reference/delivery-guarantees/
[14]: https://developers.cloudflare.com/workers/languages/typescript/
[15]: https://developers.cloudflare.com/workers/testing/vitest-integration/
[16]: https://developers.cloudflare.com/workers/wrangler/commands/workers/
[17]: https://developers.cloudflare.com/workers/configuration/compatibility-dates/
[18]: https://developers.cloudflare.com/workers/configuration/secrets/
[19]: https://developers.cloudflare.com/workers/observability/logs/workers-logs/
[20]: https://developers.cloudflare.com/workers/runtime-apis/streams/
[21]: https://developers.cloudflare.com/workers/wrangler/environments/
[22]: https://developers.cloudflare.com/workers/local-development/bindings-per-env/
[23]: https://developers.cloudflare.com/queues/reference/how-queues-works/
[24]: https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/
[25]: https://developers.cloudflare.com/workers/static-assets/
[26]: https://developers.cloudflare.com/workers/wrangler/configuration/#non-inheritable-keys
[27]: https://developers.cloudflare.com/workers/local-development/#remote-bindings
[28]: https://developers.cloudflare.com/hyperdrive/
[29]: https://developers.cloudflare.com/workers/runtime-apis/web-crypto/
