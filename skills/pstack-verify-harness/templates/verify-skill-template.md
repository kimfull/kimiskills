---
name: verify-<app>
description: 啟動、驅動並收證 <app> 的 <主表面：Web UI／CLI／API…>。修改 <app> 後要證明變更有效、重現 bug、或維護 Feature Map 時使用。
---

<!--
範本：複製到 <repo>/.claude/skills/verify-<app>/SKILL.md 後，把所有 <…> 換成本 repo 的真實值。
frontmatter 必須留在檔案第一行。交付前不得殘留任何 <…> 或 TODO；沒自跑過一次＝草稿。本註解一併刪除。
-->

# verify-<app>

主表面：<Web UI／CLI／API>（其他表面：<…，或「無」>）
證據位置：`.verify-evidence/<YYYYMMDD-HHMMSS>-<feature>/`（Cleanup 不碰）
暫存位置：`.verify-run/`（PID、暫存資料、log；Cleanup 會清）
功能索引：`features/README.md`

## Launch

```bash
<精確啟動指令；含 env 名稱（不寫值）、port、data dir>
```

- Ready 條件：<特定 log 行／prompt／某 endpoint 回出真資料>
- 空 data dir：<migration／seed 指令>
- 記 PID：<例：`echo $! > .verify-run/app.pid`；PowerShell：`(Start-Process … -PassThru).Id | Set-Content .verify-run/app.pid`>
- Isolate：<可否並存兩個 instance；不行就寫「拒絕 double-drive，不碰使用者正在用的 instance」>

## Doctor（唯讀）

任何不對勁先跑這裡；失敗就 Cleanup → Launch → 再 Doctor。

- [ ] process 還在：<指令>
- [ ] 版本／build 對：<指令與預期輸出>
- [ ] port 是我們的：<指令>
- [ ] auth 有效：<指令>

## Drive

Harness：<Playwright／chrome-devtools MCP／PowerShell／tmux／curl>
手柄優先順序：ARIA label → `data-*` → route／prompt 字串；不用座標、Tab 順序。
各功能的真實步驟在 `features/<feature>.md`。

## Evidence

1. 走真實使用者路徑，不走 test-only 捷徑。
2. 記 action + resulting state，不只最後一張截圖。
3. 查副作用：<本 app 的 DB／檔案／網路怎麼查>。
4. Mock 只用在 <生產環境本來就隔離的邊界>。
5. dry-run 要觀察實際跳過什麼。
6. 每次寫 `packet.md`：baseline／action／result／side-effects／reproduce。

## Cleanup

```bash
<依 .verify-run/*.pid 停自己啟動的 process；不依 process name>
<刪 .verify-run/ 暫存；log 先複製到證據目錄>
```

- 證據目錄不在清理範圍內；清完列一次證據目錄確認仍在。
- 失敗迭代後也要跑。

## Helpers

| 腳本 | 用途 | 呼叫方式 |
|------|------|----------|
| <scripts/xxx> | <…> | `<完整指令>` |
