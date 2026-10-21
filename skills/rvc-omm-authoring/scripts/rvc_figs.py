#!/usr/bin/env python3
"""rvc-omm-authoring 的 CSS 組裝與免驗檢查（只用標準函式庫）。路徑都相對於技能目錄。

用法：
  python3 scripts/rvc_figs.py css [--no-base] <文章ID> [flow road before-after zones lanes comparison ...]
      印出 reading.css、figure.css 加上指定圖型的 CSS（已換成文章 ID、包上標記）。lanes 會自動帶 flow。
      --no-base 只給替舊頁補 block 用：不含 reading.css（仍含 figure.css），檢查一定判「要驗畫面」。
  python3 scripts/rvc_figs.py check <文章.html> [--record 紀錄檔]
      檢查佔位符、結構、CSS 是否與技能檔一致、圖的數量與字寬是否在已驗範圍、範本驗證紀錄是否仍有效。
      最後一行是「RESULT: 免驗」「RESULT: 要驗畫面」或「RESULT: 錯誤」。
  python3 scripts/rvc_figs.py hashes
      印出目前技能片段、檢查工具、驗證固定頁與外框檔的雜湊（JSON），給範本驗證程式記錄。
  python3 scripts/rvc_figs.py record --evidence <證據目錄> [--record 紀錄檔]
      只從一份「通過」的範本驗證結果（證據目錄的 result.json）抄寫紀錄；結果失敗、用了對照組樣式、
      沒比對正式站，或驗證後技能與外框又改過，都拒絕寫入。
"""
import argparse, hashlib, html.parser, json, re, sys, time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / 'assets'
PARTS = ['flow', 'road', 'before-after', 'zones', 'lanes', 'comparison']
NEEDS = {'lanes': ['flow']}
DEFAULT_RECORD = Path('/root/kim-rvc-site/.temp/rvc-omm-template-check/record.json')
FRAME = ['/root/kim-rvc-site/workers/public/assets/main.css',
         '/root/kim-rvc-site/workers/public/assets/app.css',
         '/root/kim-rvc-site/workers/src/render.ts']
TOOLS = ['scripts/rvc_figs.py', 'scripts/verify_templates.mjs', 'scripts/template-fixture.html']
ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_-]*$')
MARK = re.compile(r'/\* rvc-omm:([a-z-]+):begin \*/\n(.*?)\n/\* rvc-omm:\1:end \*/', re.S)
# 已驗範圍（改這裡等於改了檢查工具，範本驗證紀錄會失效）
RANGES = {'flow': (2, 6), 'road': (3, 6), 'ba': (3, 8), 'zones': (2, 4), 'lanes': (2, 4), 'lane_steps': (3, 6),
          'options': (2, 4), 'criteria': (2, 5)}
TEXT_MAX = {'h4': 12, 'block': 40, 'decision': 24, 'ver': 2, 'criterion': 6, 'option': 12, 'caption': 20, 'lane': 5, 'when': 8, 'word': 32}
BADGE_WORDS = {'已完成', '進行中', '規劃中', '待決', '建議'}
BLOCK_BADGE_WORDS = {'首發', '補充'}
EXTRA_CLASSES = {'card', 'card-body', 'badge', 'badge-primary', 'badge-outline', 'badge-ghost', 'badge-sm'}
INLINE = {'span', 'b', 'strong', 'em', 'i', 'a', 'code', 'wbr', 'br', 'small', 'mark', 'sup', 'sub', 'time'}
# 文章裡只認這些標籤；其他標籤（svg、iframe、script、link、表單、details、math…）一律判要驗畫面
ALLOWED_TAGS = {'article', 'div', 'header', 'section', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'figure', 'figcaption',
                'span', 'b', 'strong', 'em', 'i', 'a', 'code', 'pre', 'br', 'wbr', 'small', 'time', 'img', 'style',
                'table', 'caption', 'thead', 'tbody', 'tr', 'th', 'td'}
# 範本裡各種節點允許的子元素（tag 或 class）；多出來的子元素判要驗畫面
# 深度 1 看子元素，深度 2 看每個 li 的子元素
CHILDREN = {'ra-chain': (2, {'ra-no', 'ra-who', 'h4', 'p'}), 'ra-road': (2, {'ra-when', 'h4', 'badge', 'p'}),
            'ra-zone': (1, {'h4', 'p', 'ra-zone-list'}), 'ra-zone-shared': (1, {'h4', 'ra-zone-links'}),
            'ra-bcard': (1, {'h4', 'p'}), 'ra-branch': (1, {'ra-ans', 'ra-bcard'}),
            'ra-zone-list': (2, INLINE), 'ra-zone-links': (2, INLINE)}
# 放字的格子只收行內元素（格子裡塞區塊元素就判要驗畫面）
TEXT_CELLS = {'p', 'h4', 'td', 'th', 'caption'}
LANE_STYLE = {'ra-lanes': r'--steps', 'ra-lane-name': r'--r', 'ra-lstep': r'--r\s*:\s*\d+\s*;\s*--c'}


def version():
    m = re.search(r'version:\s*"([^"]+)"', (SKILL / 'SKILL.md').read_text(encoding='utf8'))
    return m.group(1) if m else '?'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hashes():
    return {'skill_version': version(),
            'assets': {p.name: sha(p) for p in sorted(ASSETS.glob('*.css'))},
            'tools': {t: sha(SKILL / t) for t in TOOLS},
            'frame': {p: sha(p) if Path(p).exists() else None for p in FRAME}}


def part_css(name, art_id):
    return (ASSETS / f'{"reading" if name == "base" else name}.css').read_text(encoding='utf8').rstrip('\n').replace('__RVC_ID__', art_id)


def build(art_id, parts, base=True):
    if not ID_RE.match(art_id):
        sys.exit('文章 ID 只能用英文字母開頭，後面接英數、底線或連字號')
    want = []
    for p in parts:
        if p not in PARTS:
            sys.exit(f'不認得的圖型：{p}（可用：{" ".join(PARTS)}）')
        for d in NEEDS.get(p, []) + [p]:
            if d not in want:
                want.append(d)
    ordered = (['base'] if base else []) + (['figure'] if want or not base else []) + [p for p in PARTS if p in want]
    return '\n'.join(f'/* rvc-omm:{p}:begin */\n{part_css(p, art_id)}\n/* rvc-omm:{p}:end */' for p in ordered)


def known_classes():
    found = set(EXTRA_CLASSES)
    for p in ASSETS.glob('*.css'):
        found |= set(re.findall(r'\.([A-Za-z_][A-Za-z0-9_-]*)', p.read_text(encoding='utf8')))
    return found


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.children, self.parts = tag, dict(attrs), parent, [], []

    @property
    def cls(self):
        return set((self.attrs.get('class') or '').split())

    def walk(self):
        for c in self.children:
            yield c
            yield from c.walk()

    def text(self, skip=lambda n: False):
        out = ''
        for p in self.parts:
            if isinstance(p, str):
                out += p
            elif not skip(p):
                out += p.text(skip)
        return out

    def inline_text(self):
        # 自己的字加上行內子元素的字；遇到區塊子元素就停（那一段另外算）
        out = ''
        for p in self.parts:
            if isinstance(p, str):
                out += p
            elif p.tag in INLINE:
                out += p.inline_text()
        return out


class Tree(html.parser.HTMLParser):
    VOID = {'br', 'img', 'meta', 'link', 'hr', 'input', 'source', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root', [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        self.cur.parts.append(n)
        if tag not in self.VOID:
            self.cur = n

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.parts.append(data)


def width(text):
    w = 0
    for ch in text.strip():
        o = ord(ch)
        w += 1 if o > 0x2E7F else 0.65 if (ch.isupper() or ch.isdigit()) else 0.3 if ch.isspace() else 0.55
    return w


def kids(n, cls=None, tag=None):
    return [c for c in n.children if (cls is None or cls in c.cls) and (tag is None or c.tag == tag)]


def var(n, name):
    m = re.search(rf'--{name}\s*:\s*(\d+)', n.attrs.get('style') or '')
    return int(m.group(1)) if m else None


def in_figure(n):
    while n is not None:
        if n.tag == 'figure' and 'ra-figure' in n.cls:
            return True
        n = n.parent
    return False


def child_ok(child, allowed):
    return child.tag in allowed or bool(child.cls & allowed)


def check(path, record_path):
    src = Path(path).read_text(encoding='utf8')
    errors, need = [], []
    # 只認範本自己的佔位符；正文裡其他雙底線大寫字（例：環境變數名）不算
    names = {m for f in sorted(ASSETS.glob('*')) if f.suffix in ('.html', '.css') for m in re.findall(r'__[A-Z_]+__', f.read_text(encoding='utf8'))}
    ph = sorted(n for n in names if n in src)
    if ph:
        errors.append('佔位符沒換掉：' + ' '.join(ph))
    tree = Tree()
    tree.feed(src)
    arts = [n for n in tree.root.walk() if n.tag == 'article']
    # 沒用 base CSS 的舊頁：舊寫法可能撞到 1.4 的規則，除了下面幾項基本錯誤，其他都只判要驗畫面，不逼改舊區塊
    old = not any(name == 'base' for name, _ in MARK.findall(src))
    if len(arts) != 1 or (not old and not ID_RE.match(arts[0].attrs.get('id') or '')):
        errors.append('要剛好一個 article，且 id 符合格式')
        return report(errors, need, [])
    art, art_id = arts[0], arts[0].attrs.get('id') or ''
    if not ID_RE.match(art_id):
        need.append('舊頁的 article id 不能直接當 CSS 選擇器（沒有 id 或不是字母開頭），1.4 圖型的 CSS 會選不到')
    # Worker 會把整份原稿嵌進頁面，article 外面的任何內容都會影響整頁
    outside = [p for p in tree.root.parts if p is not art and not (isinstance(p, str) and not p.strip())]
    if outside:
        errors.append('article 外面還有內容（原稿只能有一個 article）')
    if not re.match(r'\s*<article\b', src) or not re.search(r'</article>\s*$', src) or src.count('</article>') != 1:
        errors.append('原稿要從 <article> 開始、以 </article> 結束，而且只有一個 article')
    base_errors = len(errors)
    styles = [n for n in art.walk() if n.tag == 'style']
    if len(styles) != 1:
        need.append(f'文章裡有 {len(styles)} 個 style，範本只用一個')
    css = '\n'.join(s.text() for s in styles)
    used = []
    for name, body in MARK.findall(css):
        used.append(name)
        if name not in ['base', 'figure'] + PARTS:
            need.append(f'CSS 有不認得的片段：{name}')
        elif body != part_css(name, art_id):
            need.append(f'CSS 片段 {name} 和技能檔不同（改過或版本不同）')
    if MARK.sub('', css).strip():
        need.append('有技能片段以外的自訂 CSS')
    if 'base' not in used:
        need.append('沒有用技能的 base CSS（reading.css）')
    known = known_classes()
    figs = set()
    for n in art.walk():
        c = n.cls
        if n.tag not in ALLOWED_TAGS:
            need.append(f'有 {n.tag} 元素，範本沒驗過')
        if n.tag == 'img':
            a = n.attrs
            placed = (n.parent.tag == 'p' and n.parent.parent is not None and 'ra-prose' in n.parent.parent.cls) or ('ra-figure' in n.parent.cls)
            if not (a.get('alt') or '').strip() or any(k in a for k in ('width', 'height', 'style', 'class', 'srcset')) or not placed:
                need.append('圖片要有 alt、不寫尺寸／樣式／class，並直接放在 .ra-prose 的段落或 figure.ra-figure 裡才算驗過')
            if not (a.get('src') or '').startswith('/images/'):
                need.append('圖片要先用上傳工具放到 /images/，外連或內嵌圖片要驗畫面')
        if n.tag == 'pre' and 'ra-prose' not in (n.parent.cls if n.parent else set()):
            need.append('pre 只有直接放在 .ra-prose 裡才驗過')
        if n.tag == 'table':
            extra = [x.tag for x in n.children if x.tag not in ('caption', 'thead', 'tbody')]
            if extra:
                need.append(f'比較表有範本以外的部分：{" ".join(extra)}')
        for key, (depth, allowed) in CHILDREN.items():
            if key in c:
                holders = [n] if depth == 1 else [x for x in n.children if 'ra-lane-name' not in x.cls]
                if any(not child_ok(y, allowed) for x in holders for y in x.children):
                    need.append(f'{key} 裡放了範本以外的元素')
                if depth == 2 and key in ('ra-chain', 'ra-road') and any(isinstance(t, str) and t.strip() for x in holders for t in x.parts):
                    need.append(f'{key} 的每一項要把字放進 h4 或 p，不能直接寫在 li 裡')
                if depth == 1 and any(isinstance(t, str) and t.strip() for t in n.parts):
                    need.append(f'{key} 裡的字要放進 h4 或 p')
        if in_figure(n) and (n.tag in TEXT_CELLS or c & {'ra-ans', 'ra-when'}) and any(x.tag not in INLINE for x in n.children):
            need.append(f'{n.tag} 格子裡放了區塊元素，範本只驗過文字與行內元素')
        if 'badge' in c:
            words = BADGE_WORDS if in_figure(n) else BLOCK_BADGE_WORDS if (n.parent is not None and 'ra-block-meta' in n.parent.cls) else BADGE_WORDS | BLOCK_BADGE_WORDS
            if n.text().strip() not in words or n.children:
                errors.append(f'標籤「{n.text().strip()[:10]}」不是固定用詞（圖裡：{"、".join(sorted(BADGE_WORDS))}；區塊標頭：首發、補充）')
        if 'ra-ver' in c:
            p, row = n.parent, n.parent.parent if n.parent is not None else None
            lead = next((x for x in p.parts if not isinstance(x, str) or x.strip()), None) if p is not None else None
            if (p is None or p.tag != 'p' or not p.cls & {'ra-before', 'ra-after'} or row is None or row.parent is None or 'ra-ba' not in row.parent.cls
                    or lead is not n or sum('ra-ver' in x.cls for x in p.walk()) != 1 or not p.text(lambda x: 'ra-ver' in x.cls).strip()):
                errors.append('ra-ver 只能放在前後對照 p.ra-before／p.ra-after 的最前面，每格一個，後面要接內容')
        if n.tag == 'td' and in_figure(n) and not n.text().strip():
            errors.append('比較表的格子不能是空的，沒有內容就寫「無」或「—」')
        if 'ra-legend' in c and any(x.tag != 'span' or [y for y in x.children if 'badge' not in y.cls] or len(x.children) != 1 for x in n.children):
            need.append('ra-legend 每一項要是 span，裡面只放一個狀態詞 badge 加說明文字')
        if n.tag == 'figure' and 'ra-figure' not in c:
            need.append('figure 沒有加 ra-figure，站台會把圖說擠到旁邊')
        if n.tag == 'table' and 'ra-compare' not in c:
            need.append('有不是 ra-compare 的表格')
        unknown = sorted(t for t in c if t not in known)
        if unknown:
            need.append('有範本以外的 class：' + ' '.join(unknown[:6]))
        st = n.attrs.get('style')
        if st is not None:
            ok = [k for k, pat in LANE_STYLE.items() if k in c and re.fullmatch(rf'\s*{pat}\s*:\s*\d+\s*;?\s*', st)]
            if not ok:
                need.append(f'有行內樣式：{n.tag} style="{st[:40]}"')
        if n.tag == 'figure' and 'ra-figure' in c:
            body = [x for x in n.children if x.tag != 'figcaption']
            caps = [x for x in n.children if x.tag == 'figcaption']
            root = body[0] if body else None
            kind = next((k for k in ('ra-flow', 'ra-road', 'ra-ba', 'ra-zones', 'ra-lanes', 'ra-compare') if root is not None and k in root.cls), 'img' if root is not None and root.tag == 'img' else None)
            legend_ok = len(body) == 2 and kind == 'ra-road' and 'ra-legend' in body[1].cls
            if kind is None or not (len(body) == 1 or legend_ok) or len(caps) > 1 or (caps and n.children[-1] is not caps[0]):
                need.append('figure 裡只能放一個範本（路線圖可再接一個 ra-legend），圖說放最後')
        roots = {'ra-flow', 'ra-chain', 'ra-road', 'ra-ba', 'ra-zones', 'ra-compare', 'ra-judge'}
        if c & roots and not in_figure(n):
            errors.append(f'{" ".join(sorted(c & roots))} 要放在 figure.ra-figure 裡')

        if 'ra-chain' in c and 'ra-lanes' not in c:
            figs.add('flow')
            if n.tag != 'ol':
                errors.append('ra-chain 要用 ol')
            k = len(kids(n, tag='li'))
            if len(n.children) != k:
                errors.append('ra-chain 裡只能放 li')
            lo, hi = RANGES['flow']
            if not lo <= k <= hi:
                need.append(f'流程 {k} 步，超出已驗的 {lo}–{hi} 步')
        if 'ra-flow' in c:
            shape = ['chain' if 'ra-chain' in x.cls else 'judge' if 'ra-judge' in x.cls else x.tag for x in n.children]
            if shape not in (['chain'], ['chain', 'judge']):
                errors.append('ra-flow 裡只能放一條 ra-chain，後面最多接一個 ra-judge')
            if sum('ra-judge' in x.cls for x in n.walk()) > 1:
                need.append('一個流程放了不只一個判斷，範本只驗過 1 個')
        if 'ra-judge' in c:
            figs.add('flow')
            dec = kids(n, 'ra-decision')
            brs = kids(n, 'ra-branches')
            if len(dec) != 1 or len(brs) != 1 or n.children.index(dec[0]) > n.children.index(brs[0]):
                errors.append('判斷要先放一個 ra-decision，再放一個 ra-branches')
            else:
                br = brs[0].children
                kinds = sorted(('yes' if 'is-yes' in b.cls else 'no' if 'is-no' in b.cls else '?') for b in br)
                if kinds != ['no', 'yes'] or not all('ra-branch' in b.cls for b in br):
                    errors.append('判斷要剛好兩個 ra-branch：一個 is-yes、一個 is-no')
                for b in br:
                    if not any('ra-goto' in x.cls and ({'is-loop', 'is-end'} & x.cls) for x in b.walk()):
                        errors.append('每個判斷結果都要寫 ra-goto（is-loop 或 is-end）')
                        break
                    ans = [x for x in b.children if 'ra-ans' in x.cls]
                    want = '是' if 'is-yes' in b.cls else '否'
                    if len(ans) != 1 or ans[0].text().strip() != want:
                        errors.append('判斷結果的標籤只能寫「是」或「否」，並和 is-yes／is-no 對應')
                        break
        if 'ra-road' in c:
            figs.add('road')
            if n.tag != 'ol' or len(kids(n, tag='li')) != len(n.children):
                errors.append('ra-road 要用 ol，裡面只放 li')
            k = len(kids(n, tag='li'))
            lo, hi = RANGES['road']
            if not lo <= k <= hi:
                need.append(f'路線圖 {k} 站，超出已驗的 {lo}–{hi} 站')
            if any(x.tag == 'time' for x in n.walk()):
                errors.append('路線圖裡用了 time，請改用 span.ra-when')
        if 'ra-ba' in c:
            figs.add('before-after')
            rows = n.children
            if n.tag != 'ul' or not rows or 'ra-ba-head' not in rows[0].cls or sum('ra-ba-head' in r.cls for r in rows) != 1:
                errors.append('前後對照要用 ul，第一列是唯一的 li.ra-ba-head')
            data = [r for r in rows if 'ra-ba-head' not in r.cls]
            lo, hi = RANGES['ba']
            if not lo <= len(data) <= hi:
                need.append(f'前後對照 {len(data)} 列，超出已驗的 {lo}–{hi} 列')
            for r in data:
                shape = [x.tag if x.tag == 'h4' else next(iter(x.cls & {'ra-before', 'ra-ba-arrow', 'ra-after'}), x.tag) for x in r.children]
                if shape != ['h4', 'ra-before', 'ra-ba-arrow', 'ra-after']:
                    errors.append('前後對照每列依序放 h4、p.ra-before、span.ra-ba-arrow、p.ra-after')
                    break
        if 'ra-zones' in c:
            figs.add('zones')
            z = kids(n, 'ra-zone')
            sh = kids(n, 'ra-zone-shared')
            if len(z) + len(sh) != len(n.children) or len(sh) > 1 or (sh and n.children[-1] is not sh[0]) or (z and n.children[:len(z)] != z):
                errors.append('三區圖先放各區 .ra-zone，共同帶 .ra-zone-shared 最多一個、放最後')
            lo, hi = RANGES['zones']
            if not lo <= len(z) <= hi:
                need.append(f'三區圖 {len(z)} 區，超出已驗的 {lo}–{hi} 區')
            for s in sh:
                links = [x for x in s.walk() if 'ra-zone-links' in x.cls]
                if links and len(kids(links[0], tag='li')) != len(z):
                    errors.append('共同帶的項數要和上方區數一樣、同順序')
        if 'ra-lanes' in c:
            figs.add('lanes')
            if n.tag != 'ol' or 'ra-chain' not in c:
                errors.append('泳道要寫成 ol.ra-chain.ra-lanes')
            names, steps = kids(n, 'ra-lane-name'), kids(n, 'ra-lstep')
            if n.children != names + steps:
                errors.append('泳道先放全部 li.ra-lane-name，再依步驟順序放 li.ra-lstep')
            lo, hi = RANGES['lanes']
            if not lo <= len(names) <= hi:
                need.append(f'泳道 {len(names)} 道，超出已驗的 {lo}–{hi} 道')
            lo, hi = RANGES['lane_steps']
            if not lo <= len(steps) <= hi:
                need.append(f'泳道 {len(steps)} 步，超出已驗的 {lo}–{hi} 步')
            if var(n, 'steps') != len(steps):
                errors.append('泳道 ol 的 --steps 要等於步數')
            if [var(x, 'r') for x in names] != list(range(1, len(names) + 1)):
                errors.append('道名的 --r 要依序是 1 到道數')
            if [var(x, 'c') for x in steps] != list(range(1, len(steps) + 1)):
                errors.append('泳道每步的 --c 要依序是 1 到步數')
            if any(not (var(x, 'r') or 0) or not 1 <= var(x, 'r') <= len(names) for x in steps):
                errors.append('泳道每步的 --r 要在 1 到道數之間')
        if 'ra-compare' in c:
            figs.add('comparison')
            heads = [x for x in n.walk() if x.tag == 'thead']
            cols = [x for x in heads[0].walk() if x.tag == 'th'] if len(heads) == 1 else []
            rows = [x for x in n.walk() if x.tag == 'tr' and x.parent.tag == 'tbody']
            if not cols:
                errors.append('比較表要有一個 thead')
            lo, hi = RANGES['options']
            if not lo <= len(rows) <= hi:
                need.append(f'比較表 {len(rows)} 個選項，超出已驗的 {lo}–{hi} 個')
            lo, hi = RANGES['criteria']
            if cols and not lo <= len(cols) - 1 <= hi:
                need.append(f'比較表 {len(cols) - 1} 個判準，超出已驗的 {lo}–{hi} 個')
            labels = [x.text().strip() for x in cols[1:]]
            for r in rows:
                if not r.children or r.children[0].tag != 'th' or [t.attrs.get('data-label', '') for t in r.children[1:]] != labels or any(t.tag != 'td' for t in r.children[1:]):
                    errors.append('比較表每列先放 th（選項），其餘 td 的 data-label 要和欄頭同名、同順序')
                    break

    # 字寬：每一段文字（區塊元素自己的字加行內子元素）都要在已驗範圍
    for f in (x for x in art.walk() if x.tag == 'figure' and 'ra-figure' in x.cls):
        for x in f.walk():
            if x.tag == 'figcaption' or x.tag in INLINE:
                continue
            if x.tag == 'th' and x.parent and x.parent.parent and x.parent.parent.tag == 'tbody':
                t, lim = x.text(lambda n: 'badge' in n.cls), TEXT_MAX['option']
            else:
                t = x.inline_text()
                lim = (TEXT_MAX['h4'] if x.tag == 'h4' else TEXT_MAX['decision'] if 'ra-decision' in x.cls else TEXT_MAX['criterion'] if x.tag == 'th'
                       else TEXT_MAX['caption'] if x.tag == 'caption' else TEXT_MAX['lane'] if 'ra-lane-name' in x.cls
                       else TEXT_MAX['block'])
            if t.strip() and width(t) > lim:
                need.append(f'圖內文字「{t.strip()[:16]}…」超過已驗的 {lim} 字寬')
        for x in f.walk():
            for cls_name, lim in (('ra-when', TEXT_MAX['when']), ('ra-who', TEXT_MAX['lane']), ('ra-ver', TEXT_MAX['ver'])):
                if cls_name in x.cls and width(x.text()) > lim:
                    need.append(f'「{x.text().strip()[:12]}」超過已驗的 {lim} 字寬')
        for w in re.findall(r'[A-Za-z0-9_./:-]+', f.text()):
            if len(w) > TEXT_MAX['word']:
                need.append(f'圖內英數長字「{w[:20]}…」超過已驗的 {TEXT_MAX["word"]} 字元')
    if figs and 'figure' not in used:
        errors.append('用了圖卻沒放 figure 共用片段')
    missing = sorted(figs - set(used))
    if missing:
        errors.append('用了圖卻沒放對應 CSS：' + ' '.join(missing))
    if old:
        need += errors[base_errors:]
        del errors[base_errors:]

    rec = Path(record_path)
    if not rec.exists():
        need.append(f'找不到範本驗證紀錄：{rec}')
    else:
        r = json.loads(rec.read_text(encoding='utf8'))
        now = hashes()
        if r.get('skill_version') != now['skill_version']:
            need.append(f'範本驗證紀錄是 {r.get("skill_version")} 版，技能是 {now["skill_version"]} 版')
        for group, label in (('assets', '技能 CSS'), ('tools', '檢查工具或驗證固定頁'), ('frame', '外框檔')):
            if r.get(group) != now[group]:
                changed = sorted(k for k in set(now[group]) | set(r.get(group, {})) if now[group].get(k) != r.get(group, {}).get(k))
                need.append(f'{label}在範本驗證後改過（{" ".join(Path(k).name for k in changed)}），先重驗範本')
    return report(errors, need, used)


def report(errors, need, used):
    for e in dict.fromkeys(errors):
        print('錯誤：' + e)
    for n in dict.fromkeys(need):
        print('要驗：' + n)
    print('用到的片段：' + (' '.join(used) or '無'))
    if errors:
        print('RESULT: 錯誤')
        return 1
    if need:
        print('RESULT: 要驗畫面')
        return 3
    print('RESULT: 免驗')
    return 0


def record(evidence, record_path):
    res_path = Path(evidence) / 'result.json'
    if not res_path.exists():
        sys.exit(f'找不到 {res_path}，先跑 verify_templates.mjs')
    res = json.loads(res_path.read_text(encoding='utf8'))
    problems = []
    if not res.get('passed'):
        problems.append('這次範本驗證沒有通過')
    if res.get('extraCss'):
        problems.append('這次是加了 --extra-css 的對照組')
    if not res.get('live') or not all(v.get('same') for v in res['live'].values()):
        problems.append('沒有用 --live 比對正式站，或正式站外框不同')
    if res.get('hashes') != hashes():
        problems.append('驗證之後技能、檢查工具或外框又改過，要重跑驗證')
    if problems:
        sys.exit('不寫紀錄：' + '；'.join(problems))
    rec = dict(res['hashes'], verified_at=res.get('finishedAt') or time.strftime('%Y-%m-%d %H:%M'),
               evidence=str(Path(evidence).resolve()))
    Path(record_path).parent.mkdir(parents=True, exist_ok=True)
    Path(record_path).write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n', encoding='utf8')
    print(f'已寫入範本驗證紀錄：{record_path}')


def main():
    ap = argparse.ArgumentParser(description='rvc-omm-authoring CSS 組裝與免驗檢查')
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('css'); a.add_argument('--no-base', action='store_true'); a.add_argument('id'); a.add_argument('parts', nargs='*')
    b = sub.add_parser('check'); b.add_argument('html'); b.add_argument('--record', default=str(DEFAULT_RECORD))
    sub.add_parser('hashes')
    c = sub.add_parser('record'); c.add_argument('--evidence', required=True); c.add_argument('--record', default=str(DEFAULT_RECORD))
    args = ap.parse_args()
    if args.cmd == 'css':
        print(build(args.id, args.parts, not args.no_base))
    elif args.cmd == 'check':
        sys.exit(check(args.html, args.record))
    elif args.cmd == 'hashes':
        print(json.dumps(hashes(), ensure_ascii=False))
    else:
        record(args.evidence, args.record)


if __name__ == '__main__':
    main()
