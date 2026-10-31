"""The Rechtsverordnungen in the RECHT.NRW index that carry no field_historically flag (633 on 2026-10-31): read each
one's status on its own page. Private (never published).

    python -X utf8 nohist.py fetch      # each /lrgv/ landing page (into .cache/act/<name>/current.html, as fetch.act),
                                        # and, when that page is not the newest Fassung, the newest Fassung's page
    python -X utf8 nohist.py classify   # -> .cache/nohist-status.json: in force / ended / duplicate, with the reason
    python -X utf8 nohist.py acts       # every Fassung of the in-force ones (fetch.act), then .cache/nohist-done

A page is the act's status when it is the newest Fassung the page lists ("latest-version"). The act counts as in force
on the docs date when that newest Fassung shows no "Gültig bis" on or before the docs date and its
Änderungshistorie has no "Aufgehoben durch ..." in force on or before the docs date. An entry whose Fassungen include
an act already on the in-force list, or another entry here, is a duplicate. /gvnrw/ entries (Gesetz- und
Verordnungsblatt issues, not consolidated acts) are not used.
"""
import glob, json, re, sys, time
from pathlib import Path

import fetch

HERE = Path(__file__).resolve().parent
CACHE = HERE / '.cache'
DOCS_DATE = '2026-10-31'
MONTHS = 'Januar Februar März April Mai Juni Juli August September Oktober November Dezember'.split()


def entries():
    out = []
    for f in sorted((CACHE / 'list-vo-nohist').glob('from*.json')):
        for h in json.loads(f.read_text(encoding='utf-8'))['hits']['hits']:
            u = (h['_source'].get('url') or [''])[0]
            if u.startswith('/lrgv/rechtsverordnung/') and u not in out:
                out.append(u)
    return out


def links(t):
    """[(path or None for the page itself, is_latest)] in the order the page lists them."""
    out = []
    for m in re.finditer(r'<li class="version-item([^"]*)">(?:<a href=\'(/lrgv/[^\']+)\'|<span>)', t):
        out.append((m.group(2), 'latest-version' in m.group(1)))
    return out


def latest_path(path, t):
    for p, latest in links(t):
        if latest:
            return p or path
    return path


def page_of(path):
    return CACHE / 'act' / fetch.name(path) / 'current.html'


def latest_page(path):
    """The newest Fassung's page: the landing page itself, or its newest Fassung cached under v/."""
    t = page_of(path).read_text(encoding='utf-8')
    lp = latest_path(path, t)
    if lp == path:
        return t
    f = CACHE / 'act' / fetch.name(path) / 'v' / (fetch.vname(lp) + '.html')
    return f.read_text(encoding='utf-8') if f.exists() else None


def de_day(s):
    m = re.search(r'(\d{1,2})\.\s*(' + '|'.join(MONTHS) + r')\s+(\d{4})', s)
    return f'{m.group(3)}-{MONTHS.index(m.group(2)) + 1:02d}-{int(m.group(1)):02d}' if m else None


def status(t):
    m = re.search(r'Gültig bis</div>\s*<div class="field__item">\s*(\d{2})\.(\d{2})\.(\d{4})', t)
    if m:
        bis = f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
        if bis <= DOCS_DATE:
            return False, f'Gültig bis {bis}'
    i = t.find('Änderungshistorie')
    head = t[i:i + 20000] if i >= 0 else ''
    for a in re.finditer(r'Aufgehoben durch([^<]{0,400})', head):
        d = de_day(a.group(1))
        if d is None or d <= DOCS_DATE:
            return False, 'Aufgehoben durch' + re.sub(r'\s+', ' ', a.group(1))[:160]
    return True, 'newest Fassung shows no end of validity' + (f' (Gültig bis {bis}, after the docs date)' if m else '')


def do_fetch():
    for n, path in enumerate(entries()):
        if fetch.get(fetch.BASE + path, page_of(path)) != 200:
            print('not 200', path, flush=True)
            continue
        t = page_of(path).read_text(encoding='utf-8')
        lp = latest_path(path, t)
        if lp != path:
            fetch.get(fetch.BASE + lp, CACHE / 'act' / fetch.name(path) / 'v' / (fetch.vname(lp) + '.html'))
        if n % 50 == 0:
            print(time.strftime('%H:%M:%S'), n, flush=True)
    (CACHE / 'nohist-landing-done').write_text(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')


def known_paths():
    """Every Fassung path of the acts already on the in-force lists (Gesetze and Rechtsverordnungen)."""
    out = set()
    for sub in ('list', 'list-vo'):
        for p in fetch.list_paths(sub):
            out.add(p)
            f = CACHE / 'act' / fetch.name(p) / 'current.html'
            if f.exists():
                out |= {q for q, _ in links(f.read_text(encoding='utf-8')) if q}
    return out


def classify():
    known = known_paths()
    seen, res = {}, {}
    for path in entries():
        if not page_of(path).exists():
            res[path] = {'state': 'not fetched'}
            continue
        t = page_of(path).read_text(encoding='utf-8')
        fams = {q for q, _ in links(t) if q} | {path}
        lp = latest_path(path, t)
        if fams & known:
            res[path] = {'state': 'duplicate', 'reason': 'a Fassung of an act already on the in-force list'}
            continue
        if lp in seen:
            res[path] = {'state': 'duplicate', 'reason': f'same act as {seen[lp]}'}
            continue
        seen[lp] = path
        lt = latest_page(path)
        if lt is None:
            res[path] = {'state': 'not fetched', 'reason': 'newest Fassung page missing'}
            continue
        ok, why = status(lt)
        res[path] = {'state': 'in force' if ok else 'ended', 'reason': why, 'latest': lp}
    (CACHE / 'nohist-status.json').write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    c = {}
    for v in res.values():
        c[v['state']] = c.get(v['state'], 0) + 1
    print(c)
    return res


def in_force_paths():
    """The in-force ones, by the path of their newest Fassung (what fetch.act and parse.py read), in index order."""
    res = json.loads((CACHE / 'nohist-status.json').read_text(encoding='utf-8'))
    return [v['latest'] for p, v in res.items() if v['state'] == 'in force']


if __name__ == '__main__':
    if sys.argv[1] == 'fetch':
        do_fetch()
    elif sys.argv[1] == 'classify':
        classify()
    elif sys.argv[1] == 'acts':
        for n, p in enumerate(in_force_paths()):
            fetch.act(p)
            print(n, p, flush=True)
        (CACHE / 'nohist-done').write_text(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
