// 範本邊界驗證：用 RVC Worker 原始碼在本機產生真實外框，逐一量每張圖並截圖。只開 1 個瀏覽器，請經工作機的共用排隊入口執行。
// 用法：node verify_templates.mjs <證據目錄> [--live] [--extra-css 檔案]
//   --live：另外用 cloudflared 的 Access 登入，比對正式站與本機外框 CSS 是否相同（權杖只留在本程序記憶體）。寫紀錄一定要用。
//   --extra-css：對照組用，故意加壞樣式，確認量測抓得到問題（結果必須失敗，也不能拿來寫紀錄）。
import { execFileSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const site = '/root/kim-rvc-site/workers';
const here = path.dirname(fileURLToPath(import.meta.url));
if (!process.argv[2] || process.argv[2].startsWith('--')) { console.error('用法：node verify_templates.mjs <證據目錄> [--live] [--extra-css 檔案]'); process.exit(2); }
const evidence = path.resolve(process.argv[2]);
const live = process.argv.includes('--live');
const extraAt = process.argv.indexOf('--extra-css');
const widths = [1350, 1280, 1250, 1100, 1001, 1000, 800, 641, 640, 450, 375];
await mkdir(evidence, { recursive: true });
const req = createRequire(path.join(site, 'package.json'));
const load = name => import(pathToFileURL(req.resolve(name)).href);
const { Miniflare, convertV4MiniflareOptions } = await load('miniflare');
const { build } = await load('esbuild');
const { generateKeyPair, exportJWK, SignJWT } = await load('jose');
const sha = b => createHash('sha256').update(b).digest('hex');
const figs = (...a) => execFileSync('python3', [path.join(here, 'rvc_figs.py'), ...a], { encoding: 'utf8' });

const hashesBefore = JSON.parse(figs('hashes'));
const prodConfig = await readFile(path.join(site, 'wrangler.production.jsonc'), 'utf8');
const origin = (prodConfig.match(/"PUBLIC_ORIGIN"\s*:\s*"([^"]+)"/) || [])[1];
if (!origin) throw new Error('讀不到正式設定的 PUBLIC_ORIGIN');
const result = { widths, extraCss: extraAt > 0, live: null, hashes: hashesBefore, figures: {}, failures: [], passed: false };

if (live) {
  const token = execFileSync('cloudflared', ['access', 'token', '--app', origin], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  result.live = {};
  for (const name of ['assets/main.css', 'assets/app.css']) {
    const r = await fetch(`${origin}/${name}`, { headers: { 'cf-access-token': token }, redirect: 'manual' });
    const remote = sha(Buffer.from(await r.arrayBuffer())), local = sha(await readFile(path.join(site, 'public', name)));
    result.live[name] = { status: r.status, same: r.status === 200 && remote === local };
    if (!result.live[name].same) result.failures.push(`正式站 ${name} 和本機外框不同（${r.status}）`);
  }
}

const css = figs('css', 'rvc-omm-fixture', 'flow', 'road', 'before-after', 'zones', 'lanes', 'comparison');
const extra = extraAt > 0 ? '\n' + await readFile(process.argv[extraAt + 1], 'utf8') : '';
const html = (await readFile(path.join(here, 'template-fixture.html'), 'utf8')).replace('__CSS__', css.trimEnd() + extra);
const now = new Date(Date.now() + 8 * 3600e3).toISOString();
const slug = `${now.slice(0, 10)}-${now.slice(11, 13)}${now.slice(14, 16)}-rvc-omm-template-fixture`;
const bundled = await build({ stdin: { contents: `export {default} from './src/index.ts';`, resolveDir: site, loader: 'ts' }, bundle: true, write: false, format: 'esm', platform: 'browser', target: 'es2022' });
const { privateKey, publicKey } = await generateKeyPair('RS256'), jwk = { ...await exportJWK(publicKey), kid: 'k', alg: 'RS256', use: 'sig' };
const issuer = 'https://rvc-test.cloudflareaccess.com', aud = 'a'.repeat(64), prefix = '/__rvc-staging';
const owner = await new SignJWT({ email: 'owner@example.test' }).setProtectedHeader({ alg: 'RS256', kid: 'k' }).setSubject('t').setIssuer(issuer).setAudience(aud).setIssuedAt().setExpirationTime(Math.floor(Date.now() / 1000) + 3600).sign(privateKey);
const mime = p => ({ '.css': 'text/css', '.js': 'application/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' })[path.extname(p)] || 'application/octet-stream';
// cf:false：不向外抓請求位置資料，也不在目前目錄寫 .wrangler 快取
const mf = new Miniflare(convertV4MiniflareOptions({
  modules: true, script: bundled.outputFiles[0].text, compatibilityDate: '2026-10-12', cf: false,
  bindings: { ENVIRONMENT: 'staging', PUBLIC_ORIGIN: origin, BASE_PATH: prefix, ACCESS_ISSUER: issuer, ACCESS_AUD: aud, PUBLISHER_EMAILS: 'owner@example.test', READ_ONLY: 'false', RELEASE_ID: 'local-template-check' },
  r2Buckets: ['CONTENT'], d1Databases: ['DB'],
  serviceBindings: { ASSETS: async r => { const p = path.resolve(site, 'public', '.' + new URL(r.url).pathname); if (!p.startsWith(path.join(site, 'public') + path.sep)) return new Response(null, { status: 404 }); try { return new Response(await readFile(p), { headers: { 'Content-Type': mime(p) } }); } catch { return new Response(null, { status: 404 }); } } },
  outboundService: async r => { if (r.url === issuer + '/cdn-cgi/access/certs') return Response.json({ keys: [jwk] }); throw new Error('unexpected outbound'); },
}));
let browser, server;
try {
  const db = await mf.getD1Database('DB');
  const schema = await readFile(path.join(site, 'migrations/0001_initial.sql'), 'utf8');
  await db.batch(schema.split(';').map(s => s.trim()).filter(Boolean).map(s => db.prepare(s)));
  const csrf = 'b'.repeat(64);
  const pub = await mf.dispatchFetch(origin + prefix + '/api/publish', { method: 'POST', headers: { 'Cf-Access-Jwt-Assertion': owner, 'Content-Type': 'application/json', Origin: origin, 'X-RVC-CSRF': csrf, Cookie: '__Host-rvc-csrf=' + csrf }, body: JSON.stringify({ slug, html, expectedVersion: null, requestId: randomUUID() }) });
  if (pub.status !== 200) throw new Error('本機發布失敗 ' + pub.status + ' ' + (await pub.text()).slice(0, 200));
  server = createServer(async (rq, rs) => { try { const h = { ...rq.headers, 'Cf-Access-Jwt-Assertion': owner }; delete h.host; const r = await mf.dispatchFetch(origin + rq.url, { method: rq.method, headers: h }); rs.statusCode = r.status; for (const [k, v] of r.headers) rs.setHeader(k, v); rs.end(Buffer.from(await r.arrayBuffer())); } catch { rs.writeHead(500); rs.end('proxy error'); } });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const local = `http://127.0.0.1:${server.address().port}`;
  const { chromium } = await import('/root/.claude/skills/gstack/node_modules/playwright/index.mjs');
  browser = await chromium.launch({ headless: true });
  for (const width of widths) {
    const context = await browser.newContext({ viewport: { width, height: 1000 } }), page = await context.newPage();
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    await page.route('**/rvc-build-id.txt*', r => r.fulfill({ status: 200, body: 'local-template-check:0' }));
    await page.addInitScript(() => { const o = window.setInterval; window.setInterval = (fn, ms, ...rest) => ms === 3000 ? 0 : o(fn, ms, ...rest); });
    await page.goto(local + prefix + '/replies/' + slug + '/', { waitUntil: 'networkidle' });
    const m = await page.evaluate(() => {
      const small = new Set(['ra-ver', 'ra-zone-src', 'badge']);
      const art = document.querySelector('#rvc-omm-fixture'), out = { pageOverflow: document.documentElement.scrollWidth > innerWidth, figs: {} };
      const cols = e => getComputedStyle(e).gridTemplateColumns.split(' ').filter(Boolean).length;
      // 依數量與容器寬度算出預期版型（與 layout.md〈已驗範圍〉同一組門檻）
      const expect = (f, w) => {
        const chain = f.querySelector('.ra-chain:not(.ra-lanes)'), road = f.querySelector('.ra-road'), ba = f.querySelector('.ra-ba'), zones = f.querySelector('.ra-zones'), lanes = f.querySelector('.ra-lanes'), cmp = f.querySelector('.ra-compare'), judge = f.querySelector('.ra-judge');
        const res = [];
        if (chain) { const n = chain.children.length; res.push(['流程橫排', getComputedStyle(chain).gridAutoFlow.includes('column'), w >= (n <= 4 ? 640 : 860)]); }
        if (judge) res.push(['判斷左右分岔', cols(judge.querySelector('.ra-branches')) === 2, w >= 600]);
        if (road) { const n = road.children.length; res.push(['路線橫排', getComputedStyle(road).gridAutoFlow.includes('column'), w >= (n <= 4 ? 600 : 860)]); }
        if (ba) res.push(['前後對照橫排', cols(ba.children[1]) === 4, w >= 600]);
        if (zones) { const n = zones.querySelectorAll(':scope > .ra-zone').length; res.push(['三區橫排', cols(zones) === n, w >= (n <= 3 ? 600 : 760)]); }
        if (lanes) { const n = lanes.querySelectorAll(':scope > .ra-lstep').length; res.push(['泳道橫排', getComputedStyle(lanes.querySelector('.ra-lane-name')).display !== 'none', w >= (n <= 4 ? 680 : 880)]); }
        if (cmp) { const n = cmp.querySelectorAll('thead th').length - 1; res.push(['比較表卡片', getComputedStyle(cmp.querySelector('tbody tr')).display === 'block', w < (n <= 3 ? 600 : 760)]); }
        return res;
      };
      const srOnly = (el, f) => { for (let a = el; a && a !== f; a = a.parentElement) { if (a.classList.contains('ra-sr') || getComputedStyle(a).clip === 'rect(0px, 0px, 0px, 0px)') return true; } return false; };
      for (const sec of art.querySelectorAll('section[id^="fx-"]')) {
        const f = sec.querySelector('figure'), fr = f.getBoundingClientRect(), info = { width: Math.round(fr.width), problems: [], modes: {} };
        for (const [name, actual, want] of expect(f, fr.width)) { info.modes[name] = actual; if (actual !== want) info.problems.push(`版型不符：${name} 應為 ${want}、實際 ${actual}`); }
        const texts = [];
        for (const el of f.querySelectorAll('*')) {
          if (srOnly(el, f) || !el.getClientRects().length) continue;
          const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
          const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
          if (own && cs.visibility !== 'hidden' && (r.width < 1 || r.height < 1)) info.problems.push(`有字但沒有空間 ${el.className || el.tagName}`);
          if (!r.width || !r.height) continue;
          if (r.right > fr.right + 1 || r.left < fr.left - 1) info.problems.push(`超出圖框 ${el.className || el.tagName}`);
          const connector = el.matches('.ra-chain > li, .ra-road > li, .ra-zone, .ra-branch') && el.scrollWidth - el.clientWidth <= 40;
          if (!connector && cs.overflow === 'visible' && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 && !['TABLE', 'TBODY', 'THEAD', 'TR'].includes(el.tagName)) info.problems.push(`內容超出 ${el.className || el.tagName} ${el.scrollWidth - el.clientWidth}px`);
          if (own && cs.visibility !== 'hidden') {
            const fs = parseFloat(cs.fontSize), cls = [...el.classList];
            if (fs < 16 && !(fs >= 13.5 && cls.some(c => small.has(c)))) info.problems.push(`字太小 ${fs}px ${el.className || el.tagName}`);
            for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) { const rg = document.createRange(); rg.selectNodeContents(n); for (const b of rg.getClientRects()) if (b.width > 1) texts.push({ b, el }); }
          }
        }
        // 偽元素（箭頭字、連接線）若壓到文字也算重疊
        for (const el of f.querySelectorAll('*')) for (const pe of ['::before', '::after']) {
          const ps = getComputedStyle(el, pe); if (ps.content === 'none' || ps.content === 'normal' || ps.display === 'none' || ps.position !== 'absolute') continue;
          const er = el.getBoundingClientRect(); if (!er.width) continue;
          const px = v => parseFloat(v) || 0, w = px(ps.width) || px(ps.fontSize) * 0.8, h = px(ps.height) || px(ps.fontSize);
          const l = ps.left !== 'auto' ? er.left + px(ps.left) : ps.right !== 'auto' ? er.right - px(ps.right) - w : er.left;
          const t = ps.top !== 'auto' ? er.top + px(ps.top) : ps.bottom !== 'auto' ? er.bottom - px(ps.bottom) - h : er.top;
          const b = { left: l, right: l + Math.max(w, 2), top: t, bottom: t + Math.max(h, 2) };
          for (const x of texts) { const ox = Math.min(b.right, x.b.right) - Math.max(b.left, x.b.left), oy = Math.min(b.bottom, x.b.bottom) - Math.max(b.top, x.b.top); if (ox > 1 && oy > 1) info.problems.push(`箭頭或連接線壓到文字「${x.el.textContent.trim().slice(0, 8)}」`); }
        }
        for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
          const a = texts[i], c = texts[j]; if (a.el === c.el || a.el.contains(c.el) || c.el.contains(a.el)) continue;
          const ox = Math.min(a.b.right, c.b.right) - Math.max(a.b.left, c.b.left), oy = Math.min(a.b.bottom, c.b.bottom) - Math.max(a.b.top, c.b.top);
          if (ox > 2 && oy > 2) info.problems.push(`文字重疊「${a.el.textContent.trim().slice(0, 8)}」與「${c.el.textContent.trim().slice(0, 8)}」`);
        }
        info.problems = [...new Set(info.problems)];
        out.figs[sec.id] = info;
      }
      return out;
    });
    if (m.pageOverflow) result.failures.push(`${width}px 整頁橫向溢出`);
    if (errors.length) result.failures.push(`${width}px 頁面錯誤 ${errors.length} 個`);
    for (const [id, info] of Object.entries(m.figs)) {
      (result.figures[id] ||= {})[width] = info;
      for (const p of info.problems) result.failures.push(`${width}px ${id}：${p}`);
    }
    await page.screenshot({ path: path.join(evidence, `${width}.png`), fullPage: true });
    await context.close();
  }
} catch (e) {
  result.failures.push('執行失敗：' + e.message);
} finally {
  if (browser) await browser.close();
  if (server) await new Promise(r => server.close(r));
  await mf.dispose();
  if (JSON.stringify(JSON.parse(figs('hashes'))) !== JSON.stringify(hashesBefore)) result.failures.push('驗證途中技能、檢查工具或外框檔被改過');
  result.passed = result.failures.length === 0 && !result.extraCss && !!result.live;
  result.finishedAt = new Date(Date.now() + 8 * 3600e3).toISOString().slice(0, 16).replace('T', ' ');
  await writeFile(path.join(evidence, 'result.json'), JSON.stringify(result, null, 1));
}
console.log(result.failures.length ? result.failures.join('\n') : '全部寬度通過：版型符合預期，無溢出、無重疊、無過小文字');
if (result.live) console.log('正式站外框比對：' + JSON.stringify(result.live));
console.log(result.passed ? 'PASSED（可以寫紀錄）' : 'NOT PASSED（不能寫紀錄）');
process.exit(result.failures.length ? 1 : 0);
