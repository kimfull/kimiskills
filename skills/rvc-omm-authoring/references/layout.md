# 閱讀版面與片段

這是 RVC 新頁的寫作預設，來自本次確認的版面；使用者另有指定或專案正本改變時依新要求調整。它不自動改寫舊文章，也不套用到官網或管理儀表板。

## 寬度與節奏

| 項目 | 桌面 | 手機（≤640px） |
|---|---:|---:|
| 文字區塊上限 | 690px | 可用寬度，最高690px |
| 圖表／整組卡片上限 | 900px | 可用寬度，最高900px |
| 內容到螢幕左右邊緣 | 依側欄與容器 | 各12px |
| 相鄰段落 | 32px | 28px |
| 新章節標題組上方 | 96px | 72px |
| 章節標題組到說明 | 24px | 20px |
| 說明到圖表 | 32px | 24px |
| 圖表到圖說 | 16px | 16px |
| header 到第一個 block、block 之間 | 96px | 72px |
| block 分隔線到 meta 列 | 32px（另加 1px 線） | 28px（另加 1px 線） |
| meta 列到 block 內第一個章節 | 24px | 20px |
| 清單項之間 | 12px | 12px |

900px 容器在主閱讀區置中，690px 文字靠左，與圖表同左緣。上限不是固定寬度；卡片邊框、內距包含在900px內。手機12px是主內容到螢幕的總距離，不是每層各加12px；圖內有意的內距另計。

表中距離是相鄰元素的最終間隔，不在兩邊各加一次。章節編號若存在，與標題視為一組；不要再加段落間距到同一個間隔上。卡片內的標題和說明保留較緊的分組，不套章節96px。

正文18px、行高1.8；圖內主要文字從16px起，必要時重排而非縮小。圖片若含字，讀者靠站上的燈箱點開看原圖；放圖前確認原圖的字在原尺寸下讀得清楚，太小就改用文字或重截。

## 使用方式

- [base.html](../assets/base.html)：新單篇外框，保留一個article與第一個h2。
- [reading.css](../assets/reading.css)：共用尺寸與排版，放入base的style。清單、pre、行內 code 的樣式只套在沒有 class 的元素；用 DaisyUI 元件時照元件本身的樣式。
- [prose.html](../assets/prose.html)：文字段落。
- [flow.html](../assets/flow.html)：完整流程及分支。
- [comparison.html](../assets/comparison.html)：同欄位比較表。
- [block.html](../assets/block.html)：替用本範本的頁補內容（多 block）。

組合步驟：

1. 為整篇選唯一、可直接用在CSS選擇器的ID：必須符合 `^[A-Za-z][A-Za-z0-9_-]*$`（英文字母起首，後續僅英數、底線或連字號），例如 `rvc-release-note`。不要用句點、冒號、空白或任意使用者原文作ID。將 base 與 CSS 的 `__RVC_ID__` 全部換成此值。
2. 依專案正本填入 `__AI__` 與 `__TOPIC__`；填 `__TITLE__`、`__INTRO__`。文字與屬性值須適當HTML跳脫，不把原始外部內容直接當HTML。
3. 將CSS插入 `__CSS__`，需要的片段插入 `__SECTIONS__`。每個片段的 `__SECTION_ID__` 都換成不同ID，且符合步驟1的同一格式；同步CSS以外的標題關聯屬性。也可自行寫符合本版面的內容。
4. 改寫片段中的示例內容，不把示例流程當成實際任務事實；移除不需要的段落。發布前確認沒有任何 `__...__` 標記殘留。

每篇輸出的HTML自帶當時CSS，便於單篇穩定呈現；後續技能調整不自動同步所有舊文。常用數值只在reading.css維護一份執行樣式，更新時同步上表並驗收。

## 正式外框的兩個陷阱

目前生成頁會有 `main > section > article`，不要把 `main:has(> #ID)` 當成一定成立。範本用 `main:has(#ID)` 限定該篇頁面；實際包裝以當前repo為準。驗收應含build注入的發布日期，不能只換掉main內容而丟失section外框。

DaisyUI 的 `.card figure` 可能設定flex，將圖說排到圖旁；reading.css對該篇figure明確設block。外層 `.card-body` 的預設padding與gap也清除，避免破壞12px與量測間距。勿把這些局部覆寫改成全站選擇器。

## 補 block

替用本範本的頁補內容時用 block 片段；外層屬性照 repo〈Block 規矩〉，不貼別處的間距 class（reading.css 會把 p 的 margin 歸零，兩邊疊加會跑版）。

1. 第一次補 block：把原本 header 以下的內容包進一個 block，`__BADGE__` 填「首發」、`__BADGE_CLASS__` 用 `badge-ghost`，時間用檔名時間；新內容放在它上面的新 block，`__BADGE__` 填「補充」、`__BADGE_CLASS__` 用 `badge-primary`。首發 block 的 `__BLOCK_AI__` 填 article 原本的 data-ai（原作者），補充 block 填這次寫的 AI。header（h2、前言）留在所有 block 之上。
2. 之後再補：新 block 一律加在最上面，舊 block 不動。
3. 開頭標籤保持 `<section data-block-time="HH:MM" data-block-title="..." data-block-ai="...">` 的順序，不寫 id（build 會自動產生 `b{HHMM}`）；`__BLOCK_TIME__` 是 HH:MM，`__BLOCK_DATETIME__` 是 YYYY-MM-DD HH:MM。
4. article 原本的 data-ai 不改；每個 block 用 `__BLOCK_AI__` 標自己的 data-block-ai。block 內的片段 ID 一樣要整篇唯一。
5. 有實質增修時照 repo 規則更新 article 的 data-updated。

## 舊頁

不是用本範本寫的既有頁，局部新增沿用該頁現有的寫法；單卡舊頁第一次補 block 時，外層照 repo〈Block 規矩〉，meta 列照抄任一篇舊的多 block 頁，不必恢復舊範本；首發 block 的 data-block-ai 同〈補 block〉第 1 步，填原作者。不要直接塞base或換整篇ID，否則舊圖、anchor與樣式可能失效。整批轉換舊頁不在本技能範圍。
