<!-- 範本：複製到 <repo>/.claude/skills/verify-<app>/features/<feature>.md。四個 H2 名稱與順序固定，不得增刪改名。 -->
# <功能名稱>

## Sub-features

- <子功能 1>
- <子功能 2>

## How to get to it (user POV)

- 入口 1：<使用者怎麼走到，例：首頁 → 設定 → 通知>
- 入口 2：<其他入口；每個入口都要能證明>
- 過關終態：<可觀測的結果，例：畫面出現「已儲存」且 reload 後值仍在>

## Driving it with <harness>

```text
<真實指令／selector，逐步；不得留 placeholder>
```

- 要收的證據：<截圖／a11y snapshot／stdout／DB 查詢>
- 副作用怎麼查：<指令>

## Gotchas

- <seed 缺什麼前置條件時會失敗（照實報失敗，不削弱 journey）>
- <不穩定的地方、等待條件、已知漂移>
