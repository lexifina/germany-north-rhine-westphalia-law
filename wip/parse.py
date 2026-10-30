"""North Rhine-Westphalian law from RECHT.NRW pages (.cache/act/<act>/current.html and v/<Fassung>.html) into
corpus.d/ parts.

    python -X utf8 parse.py

Reads only the cache; the same cache gives the same bytes. Parts:
  10-verfassung.json   the Verfassung für das Land Nordrhein-Westfalen
  20-gesetze-NN.json   the other Gesetze in force, in the portal's list order, about 50 acts a part
A part is written only when every act it holds is complete in the cache.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / '.cache'
BASE = 'https://recht.nrw.de'
RETRIEVED = '2026-10-30'
PART_SIZE = 50
VERF = '16012026-verfassung-fuer-das-land-nordrhein-westfalen'
MONTHS = {m: i + 1 for i, m in enumerate(['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August',
                                           'September', 'Oktober', 'November', 'Dezember'])}
VOID = {'br', 'img', 'hr', 'input', 'meta', 'link', 'col', 'wbr'}
BLOCKS = {'p', 'li', 'tr', 'dt', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'pre', 'blockquote', 'caption'}

COUNTRY = {
    'code': 'DE-NW', 'name': 'North Rhine-Westphalia', 'slug': 'germany-north-rhine-westphalia', 'lang': 'de',
    'tz': 'Europe/Berlin', 'future_branch': 'zukunft',
    'publisher': {'name': 'Ministerium des Innern des Landes Nordrhein-Westfalen (RECHT.NRW)',
                  'email': 'recht-nrw@recht.nrw.de.invalid'},
    'default_in_force_rule': {
        'text': 'Verfassung für das Land Nordrhein-Westfalen Art. 71 Abs. 3: "Jedes Gesetz und jede Rechtsverordnung '
                'soll den Tag des Inkrafttretens bestimmen." Each version here is dated by the day RECHT.NRW gives as '
                'the start of its validity ("Gültig ab").',
        'source': 'https://recht.nrw.de/lrgv/gesetz/16012026-verfassung-fuer-das-land-nordrhein-westfalen'},
    'licence_note': 'Texts: RECHT.NRW, the service portal of the Ministerium des Innern des Landes Nordrhein-Westfalen '
                    '(recht.nrw.de). Gesetze and Verordnungen are not protected by copyright (§ 5 Abs. 1 UrhG). '
                    'Non-official text: only the printed Gesetz- und Verordnungsblatt (GV. NRW.) is authoritative.',
}


class Node:
    __slots__ = ('tag', 'attrs', 'kids', 'parent')

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.kids, self.parent = tag, dict(attrs), [], parent


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root', {}, None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.kids.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        x = self.cur
        while x is not self.root and x.tag != tag:
            x = x.parent
        if x is not self.root:
            self.cur = x.parent

    def handle_data(self, data):
        self.cur.kids.append(data)


def find(n: Node, pred):
    for k in n.kids:
        if isinstance(k, Node):
            if pred(k):
                return k
            r = find(k, pred)
            if r:
                return r
    return None


def norm(s: str) -> str:
    s = s.replace(' ', ' ').replace(' ', ' ').replace(' ', ' ').replace('­', '')
    s = s.replace(',,', '„').replace('”', '“')  # one form of German quotes
    s = re.sub(r'([(\[„]) +', r'\1', s)
    return re.sub(r'[ \t\r\n]+', ' ', s).strip()


def text_of(n, br='\n') -> str:
    if isinstance(n, str):
        return n
    if skip(n):
        return ''
    if n.tag == 'br':
        return br
    return ''.join(text_of(k, br) for k in n.kids)


HAS_BLOCK = ('p', 'ol', 'ul', 'div', 'table', 'dl')


def has_block(k: Node) -> bool:
    return any(isinstance(x, Node) and x.tag in HAS_BLOCK for x in k.kids)


def item(n: Node) -> list[str]:
    """A list item or definition entry: its lines (nested lists become further lines)."""
    if has_block(n):
        return lines(n)
    s = norm(text_of(n, ' '))
    return [s] if s else []


def lines(n: Node) -> list[str]:
    """One line per paragraph, list item, table row or definition entry. A line break inside a paragraph is a space."""
    out: list[str] = []
    buf: list[str] = []

    def flush():
        s = norm(''.join(buf))
        if s:
            out.append(s)
        buf.clear()
    for k in n.kids:
        if isinstance(k, str):
            buf.append(k)
        elif skip(k):
            continue
        elif k.tag == 'tr':
            flush()
            cells = [norm(text_of(c, ' ')) for c in k.kids if isinstance(c, Node) and c.tag in ('td', 'th')]
            if any(cells):
                out.append(' | '.join(cells).strip())
        elif k.tag == 'dl':
            flush()
            dt = ''
            for x in k.kids:
                if not isinstance(x, Node) or x.tag not in ('dt', 'dd'):
                    t = norm(x if isinstance(x, str) else text_of(x, ' '))
                    if t:  # loose text in the list (a dd the page left out): the entry's text
                        out.append(f'{dt} {t}' if dt else t)
                        dt = ''
                    continue
                if x.tag == 'dt':
                    if dt:
                        out.append(dt)
                    dt = norm(text_of(x, ' '))
                elif x.tag == 'dd':
                    ls = item(x)
                    if dt:
                        ls = [f'{dt} {ls[0]}' if ls else dt] + ls[1:]
                        dt = ''
                    out += ls
            if dt:
                out.append(dt)
        elif k.tag == 'ol':
            # The browser numbers these items (1., 2., ... or a), b), ...); the number is written out.
            flush()
            typ = k.attrs.get('type') or '1'
            num = int(k.attrs.get('start') or 1)
            for x in k.kids:
                if isinstance(x, Node) and x.tag == 'li':
                    mark = (f'{chr(96 + num)})' if typ == 'a' else f'{num}.')
                    ls = item(x)
                    out += [f'{mark} {ls[0]}' if ls else mark] + ls[1:]
                    num += 1
        elif k.tag in ('section', 'table', 'tbody', 'thead', 'ul', 'header', 'footer') or k.tag in BLOCKS:
            flush()
            out += item(k) if k.tag in ('li', 'p', 'dt', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'caption') else lines(k)
        elif k.tag == 'br':
            buf.append(' ')
        else:
            buf.append(text_of(k, ' '))
    flush()
    return out




def skip(n: Node) -> bool:
    """Page furniture inside a provision: footnotes (left out), print/copy menus, alerts."""
    c = n.attrs.get('class') or ''
    return n.tag == 'button' or any(x in c for x in ('footnote-container', 'article-print', 'alert'))


def de_date(s: str) -> str | None:
    m = re.search(r'(\d{1,2})\.\s*([A-Za-zÄäÖöÜü]+)\s+(\d{4})', s)
    if not m or m.group(2) not in MONTHS:
        return None
    return f'{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}'


def dmy(s: str) -> str | None:
    m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', s)
    return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else None


def law(enacted: str, gy: str, page: str) -> tuple[str, dict]:
    y, mo, d = enacted.split('-')
    mon = [k for k, v in MONTHS.items() if v == int(mo)][0]
    return f'gvnrw-{gy}-{int(page):04d}-{enacted.replace("-", "")}', {
        'label': f'Änderung vom {int(d)}. {mon} {y} (GV. NRW. {gy} S. {int(page)})', 'title': None, 'kind': 'law',
        'enacted': enacted, 'published': None, 'url': None, 'temporary_until': None, 'restores': None, 'note': None}


DATE = r'(\d{1,2}\.\s*[A-Za-zÄäÖöÜü]+\s+\d{4})'


def history(raw: str) -> list[tuple[str, dict, list[str]]]:
    """The amending acts the page's Änderungshistorie names, each with the days it came into force."""
    out = []
    blocks = re.findall(r'(?s)<div class="change-history-item">(.*?)(?=<div class="change-history-item">|<div class="full-quote-items)', raw)
    for b in blocks:
        t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', b)).replace('&nbsp;', ' ')
        pub = re.search(r'Veröffentlichung:\s*GV\.\s*NRW\.?\s*(\d{4})\s*S\.\s*(\d+)', t)
        if pub:
            m = re.search(r'vom ' + DATE + r'.*?in Kraft getreten am ' + DATE + r'((?:\s*(?:und|sowie) am ' + DATE + r')*)', t)
            if m and de_date(m.group(1)) and de_date(m.group(2)):
                days = [de_date(m.group(2))] + [de_date(x) for x in re.findall(DATE, m.group(3) or '')]
                k, lw = law(de_date(m.group(1)), pub.group(1), pub.group(2))
                out.append((k, lw, [d for d in days if d]))
            continue
        for m in re.finditer(r'vom ' + DATE + r'\s*\(\s*GV\.\s*NRW\.?\s*(?:(\d{4})\s*)?S\.\s*(\d+)\s*\)\s*,?\s*in Kraft getreten am '
                             + DATE + r'((?:\s*(?:und|sowie) am ' + DATE + r')*)', t):
            en = de_date(m.group(1))
            if not en or not de_date(m.group(4)):
                continue
            days = [de_date(m.group(4))] + [de_date(x) for x in re.findall(DATE, m.group(5) or '')]
            k, lw = law(en, m.group(2) or en[:4], m.group(3))
            out.append((k, lw, [d for d in days if d]))
    return out


def unit_key(title: str, seen: set[str]) -> tuple[str, str]:
    m = re.match(r'^(Artikel|Art\.|§§?)\s*(\d+)\s*([a-z]?)\b(?:\s*(?:bis|-|–|und)\s*(\d+)\s*([a-z]?))?', title)
    if m:
        pre = 'art' if m.group(1).startswith('Art') else 'par'
        k = f'{pre}-{int(m.group(2)):03d}{m.group(3)}' + (f'-{int(m.group(4)):03d}{m.group(5)}' if m.group(4) else '')
        kind = pre
    elif re.match(r'^(Anlage|Anhang|Tabelle|Muster|Verzeichnis)', title):
        mm = re.match(r'^(\w+)\s*(\d*)\s*([a-z]?)', title)
        k = 'z-' + mm.group(1).lower().translate(str.maketrans('äöüß', 'aous')) + (
            f'-{int(mm.group(2)):02d}{mm.group(3)}' if mm.group(2) else '')
        kind = 'annex'
    else:
        k = 'y-' + (re.sub(r'[^a-z0-9]+', '-', title.lower().translate(str.maketrans('äöüß', 'aous'))).strip('-')[:40]
                    or 'teil')
        kind = 'other'
    base, i = k, 2
    while k in seen:
        k = f'{base}-{i}'
        i += 1
    seen.add(k)
    return k, kind


def parse_page(raw: str) -> dict | None:
    """None for a Fassung the portal shows only as a legacy file (no structured text)."""
    if '<section class="legaldoc-article">' not in raw:
        return None
    t = Tree()
    t.feed(raw)
    h1 = find(t.root, lambda n: n.tag == 'h1')
    m = re.search(r'Gültig ab</div>\s*<div class="field__item">\s*([\d.]+)', raw)
    units: dict[str, dict] = {}
    seen: set[str] = set()
    secs: list[tuple[Node, list[str]]] = []
    pending: list[str] = []
    HEADS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')

    def walk(n, depth):
        for k in n.kids:
            if not isinstance(k, Node):
                continue
            c = k.attrs.get('class') or ''
            if k.tag == 'section' and 'legaldoc-article' in c:
                secs.append((k, list(pending)))
                pending.clear()
            elif k.tag == 'section' and 'legaldoc-' in c:  # legaldoc-part, legaldoc-section, ...: a heading
                st = find(k, lambda x: 'paragraph--type--structure' in (x.attrs.get('class') or ''))
                hd = find(st, lambda x: x.tag in HEADS) if st else None
                if hd:
                    pending.append('#' * min(depth + 1, 6) + ' ' + norm(text_of(hd, ' ')))
                walk(k, depth + 1)
            else:
                walk(k, depth)
    walk(t.root, 1)
    pre = find(t.root, lambda x: 'field--name-field-preamble' in (x.attrs.get('class') or ''))
    if pre is not None and lines(pre):
        units['000-a-eingangsformel'] = {'label': 'Eingangsformel', 'kind': 'title', 'text': '\n'.join(lines(pre)) + '\n'}
        seen.add('000-a-eingangsformel')
    for s, heads in secs:
        ph = find(s, lambda x: 'paragraph-header' in (x.attrs.get('class') or ''))
        h2 = find(ph, lambda x: x.tag in HEADS) if ph else None
        head = norm(text_of(h2, ' ')) if h2 else ''
        body = find(s, lambda n: 'field--name-field-text' in (n.attrs.get('class') or ''))
        bl = lines(body) if body else []
        if not head:
            if '000-eingang' not in seen:
                key, kind, label = '000-eingang', 'title', 'Eingang'
                seen.add(key)
            else:
                key, kind = unit_key('text', seen)
                label = 'Text'
        else:
            key, kind = unit_key(head, seen)
            lm = re.match(r'^((?:Artikel|Art\.|§§?)\s*\d+\s*[a-z]?)\b', head)
            label = lm.group(1) if lm else head
        units[key] = {'label': label, 'kind': kind,
                      'text': '\n'.join(heads + ([f'# {head}'] if head else []) + bl) + '\n'}
    if pending and secs:
        last = list(units)[-1]
        units[last]['text'] += '\n'.join(pending) + '\n'
    con = find(t.root, lambda x: 'field--name-field-conclusions' in (x.attrs.get('class') or ''))
    if con is not None and lines(con):
        units['zz-schlussformel'] = {'label': 'Schlussformel', 'kind': 'other', 'text': '\n'.join(lines(con)) + '\n'}
    return {'title': norm(text_of(h1, ' ')) if h1 else '', 'from': dmy(m.group(1)) if m else None, 'units': units,
            'history': history(raw)}


def stem_day(stem: str) -> str:
    m = re.match(r'^(\d{2})(\d{2})(\d{4})', stem)
    return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''


def act_files(name: str) -> list[Path]:
    d = CACHE / 'act' / name
    files = [f for f in (d / 'v').glob('*.html')] + [d / 'current.html']
    return sorted(files, key=lambda f: stem_day(name if f.stem == 'current' else f.stem))


def act_of(name: str) -> tuple[dict | None, dict, list[str]]:
    laws: dict = {}
    problems: list[str] = []
    versions = []
    title = ''
    prev = None
    skipped = 0
    links = version_links(name)
    for f in act_files(name):
        raw = f.read_text(encoding='utf-8')
        p = parse_page(raw)
        if p is None:
            skipped += 1
            continue
        title = p['title'] or title
        if not p['from']:
            problems.append(f'{name} {f.name}: no "Gültig ab" date')
            continue
        if versions and p['from'] <= versions[-1]['from']:
            problems.append(f'{name} {f.name}: from {p["from"]} not after {versions[-1]["from"]}; left out')
            continue
        path = prefix(name) + name if f.stem == 'current' else links.get(f.stem, prefix(name) + f.stem)
        v = {'from': p['from'], 'source_url': BASE + path, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest(),
             'units': p['units'], 'credits': {}}
        if prev is not None:
            day_laws = sorted({k for k, lw, days in p['history'] if p['from'] in days})
            for k, lw, days in p['history']:
                if k in day_laws:
                    laws[k] = lw
            if day_laws:
                for k in sorted(set(prev['units']) | set(p['units'])):
                    if prev['units'].get(k, {}).get('text') != p['units'].get(k, {}).get('text'):
                        v['credits'][k] = day_laws
        versions.append(v)
        prev = p
    if skipped:
        problems.append(f'{name}: {skipped} older Fassungen are shown only as legacy files (no structured text) and are not used')
    if not versions:
        return None, laws, problems
    meta = list_meta().get(name, {})
    abbr = (meta.get('field_abbreviation') or [''])[0].strip()
    stitle = (meta.get('field_short_title') or [''])[0].strip()
    slug = 'verfassung' if name == VERF else re.sub(r'^\d{8}-', '', name)[:60].strip('-')
    if prefix(name) != '/lrgv/gesetz/':
        # Rechtsverordnungen: many share the first 60 characters of their title; the abbreviation names the act
        # where the portal gives one, else the slug carries the date prefix of the act's path (YYYYMMDD)
        ab = re.sub(r'[^a-z0-9]+', '-', abbr.lower().translate(str.maketrans('äöüß', 'aous'))).strip('-')
        slug = ab if ab and ab not in VO_SLUGS else slug
        if slug in VO_SLUGS:
            slug = f'{slug[:51].strip("-")}-{name[4:8]}{name[2:4]}{name[0:2]}'
        base, k = slug, 2
        while slug in VO_SLUGS:
            slug = f'{base}-{k}'
            k += 1
        VO_SLUGS.add(slug)
    act = {'slug': slug,
           'short': 'Verf NRW' if name == VERF else (abbr or stitle or title[:60]),
           'title': title, 'url': BASE + prefix(name) + name, 'first_law': None, 'earlier_laws': [],
           'versions': versions}
    return act, laws, problems


def write_part(name: str, acts_in: list[str], country: bool) -> None:
    acts, laws, problems = [], {}, []
    for i in acts_in:
        a, lw, pr = act_of(i)
        problems += pr
        if a:
            acts.append(a)
            laws.update(lw)
    nv = sum(len(a['versions']) for a in acts)
    out = {'acts': acts, 'laws': dict(sorted(laws.items())), 'applies': [],
           'sources': [{'name': 'RECHT.NRW (Ministerium des Innern des Landes Nordrhein-Westfalen): Landesrecht, '
                                'current and earlier Fassungen of each act',
                        'url': BASE, 'retrieved': RETRIEVED,
                        'licence': '§ 5 Abs. 1 UrhG: Gesetze, Verordnungen and amtliche Erlasse enjoy no copyright '
                                   'protection. RECHT.NRW states no terms restricting reuse.',
                        'notes': f'{len(acts)} acts, {nv} versions in this part.'}],
           'decisions': [
               'Every Fassung RECHT.NRW shows as structured text is one version here, dated by its "Gültig ab" day. '
               'Older Fassungen that the portal shows only as legacy files (PDF or old HTML) are not used, so each '
               'act starts with the oldest structured Fassung, credited to the publisher as the oldest version available.',
               'The provisions that changed between two versions are credited to the amending act(s) the newer '
               'version\'s Änderungshistorie lists as coming into force on that version\'s first day; if it lists '
               'none for that day, the change is labelled unexplained.',
               'One file per Artikel or Paragraph; headings of Teile and Abschnitte stand where the portal prints them '
               '(at the end of the provision before). Footnotes are left out; tables are one line per row, cells '
               'separated by " | "; numbered lists whose numbers the browser supplies are written with those numbers.'] + [f'Note: {p}' for p in problems],
           'ai_use': ['Claude Code (claude-opus-5-5) wrote Lexifina\'s code and chose the sources. No model output is '
                      'used as legal text, dates or credits: every word comes from the RECHT.NRW pages, and every date '
                      'and credit from the portal\'s own validity dates and Änderungshistorie.']}
    if country:
        out['country'] = COUNTRY
    d = HERE / 'corpus.d'
    d.mkdir(exist_ok=True)
    tmp = d / (name + '.json.tmp')
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    tmp.replace(d / (name + '.json'))
    print(name, len(acts), 'acts', nv, 'versions', len(problems), 'notes')


def prefix(name: str) -> str:
    """The act's path on the portal less its name: /lrgv/gesetz/ or /lrgv/rechtsverordnung/."""
    u = (list_meta().get(name, {}).get('url') or ['/lrgv/gesetz/'])[0]
    return u.strip('/').rsplit('/', 1)[0].join('//') if '/' in u.strip('/') else '/lrgv/gesetz/'


_META: dict = {}
VO_SLUGS: set = set()


def list_meta() -> dict:
    if _META:
        return _META
    meta = _META
    for f in sorted((CACHE / 'list').glob('from*.json')) + sorted((CACHE / 'list-vo').glob('from*.json')):
        for h in json.loads(f.read_text(encoding='utf-8'))['hits']['hits']:
            u = (h['_source'].get('url') or [''])[0]
            meta.setdefault(u.strip('/').rsplit('/', 1)[-1][:150], h['_source'])
    return meta


def list_names(sub: str = 'list') -> list[str]:
    names = []
    for f in sorted((CACHE / sub).glob('from*.json')):
        for h in json.loads(f.read_text(encoding='utf-8'))['hits']['hits']:
            u = (h['_source'].get('url') or [''])[0]
            if u.startswith('/lrgv/gesetz/' if sub == 'list' else '/lrgv/rechtsverordnung/'):
                n = u.strip('/').rsplit('/', 1)[-1][:150]
                if n not in names and n != VERF and 'verfassung-fuer-das-land' not in n:
                    names.append(n)
    return names


def vname(n: str) -> str:
    return n[:8] if n[:8].isdigit() else n[:60]


def version_links(name: str) -> dict:
    """Cache name of each listed Fassung -> its path on the portal."""
    cur = CACHE / 'act' / name / 'current.html'
    if not cur.exists():
        return {}
    return {vname(p.rsplit('/', 1)[-1]): p for p in
            re.findall(r"<li class=\"version-item[^\"]*\"><a href='(/lrgv/[^']+)'", cur.read_text(encoding='utf-8'))}


def complete(name: str) -> bool:
    if not (CACHE / 'act' / name / 'current.html').exists():
        return False
    return all((CACHE / 'act' / name / 'v' / f'{v}.html').exists() for v in version_links(name))


if __name__ == '__main__':
    write_part('10-verfassung', [VERF], country=True)
    names = list_names()
    for n in range(0, len(names), PART_SIZE):
        chunk = names[n:n + PART_SIZE]
        if all(complete(i) for i in chunk):
            write_part(f'20-gesetze-{n // PART_SIZE + 1:02d}', chunk, country=False)
        else:
            break
    # the Rechtsverordnungen (ordinances wave, 2026-10-30), parts of 50 in list order; the last, short part only
    # once every one is fetched (.cache/vo-done)
    names = list_names('list-vo')
    for n in range(0, len(names), PART_SIZE):
        chunk = names[n:n + PART_SIZE]
        if len(chunk) < PART_SIZE and not (CACHE / 'vo-done').exists():
            break
        if all(complete(i) for i in chunk):
            write_part(f'40-verordnungen-{n // PART_SIZE + 1:02d}', chunk, country=False)
        else:
            break
