"""Fetch RECHT.NRW (recht.nrw.de) into .cache/: the list of Gesetze in force, then every Fassung of each act.

    python -X utf8 fetch.py list                 # the portal's own search index: document type Gesetz, current
    python -X utf8 fetch.py acts <url-path> ...  # one act: its current page, then each listed Fassung
    python -X utf8 fetch.py acts --all           # the Verfassung first, then every Gesetz on the cached list
    python -X utf8 fetch.py list-vo              # the same index, document type Rechtsverordnung (.cache/list-vo/)
    python -X utf8 fetch.py acts-vo              # every Rechtsverordnung on that list, then .cache/vo-done
    python -X utf8 fetch.py list-vo-nohist       # Rechtsverordnungen with no field_historically (.cache/list-vo-nohist/)

Private (never published). One process, one request at a time, at least 2.5 s apart (robots.txt: Drupal defaults,
no AI-agent rules, no Crawl-delay; /search/ is not used), curl with a browser User-Agent, cached by name; stops on
403/429 or a challenge page.
"""
import hashlib, json, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / '.cache'
BASE = 'https://recht.nrw.de'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
VERF = '/lrgv/gesetz/16012026-verfassung-fuer-das-land-nordrhein-westfalen'
_last = [0.0]


def get(url: str, out: Path, data: str | None = None) -> int:
    if out.exists() and out.stat().st_size:
        return 200
    wait = 2.5 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + '.part')
    cmd = ['curl', '-s', '-L', '--compressed', '--max-time', '90', '-A', UA, '-o', str(tmp), '-w', '%{http_code}']
    if data is not None:
        cmd += ['-H', 'Content-Type: application/json', '-X', 'POST', '--data-binary', data]
    p = subprocess.run(cmd + [url], capture_output=True, text=True)
    _last[0] = time.time()
    code = int(p.stdout.strip() or 0)
    body = tmp.read_bytes() if tmp.exists() else b''
    with open(CACHE / 'requests.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps({'t': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'url': url, 'post': data is not None,
                            'code': code, 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}) + '\n')
    if code in (403, 429) or b'Just a moment' in body[:5000] or b'captcha' in body[:5000].lower():
        tmp.unlink(missing_ok=True)
        raise SystemExit(f'stop: {code} on {url}')
    if code == 200 and body:
        tmp.replace(out)
    else:
        tmp.unlink(missing_ok=True)
    return code


def name(path: str) -> str:
    return path.strip('/').rsplit('/', 1)[-1][:150]


def vname(path: str) -> str:
    """A Fassung's cache name: its date prefix (DDMMYYYY), so paths stay short on Windows."""
    n = name(path)
    return n[:8] if n[:8].isdigit() else n[:60]


def listing(doctype: str = 'Gesetz', nohist: bool = False):
    sub = ('list' if doctype == 'Gesetz' else 'list-vo') + ('-nohist' if nohist else '')
    src = ['title', 'url', 'field_abbreviation', 'field_short_title', 'field_long_title', 'field_effective_from',
           'field_historically', 'field_document_type_name']
    n = 0
    while True:
        flt = {'filter': [{'term': {'field_document_type_name': doctype}}, {'term': {'field_historically': False}}]}
        if nohist:   # the index entries with no historically flag at all
            flt = {'filter': [{'term': {'field_document_type_name': doctype}}],
                   'must_not': [{'exists': {'field': 'field_historically'}}]}
        q = {'query': {'bool': flt},
             'size': 100, 'from': n, '_source': src, 'sort': [{'_id': 'asc'}]}
        out = CACHE / sub / f'from{n:05d}.json'
        get(f'{BASE}/search-middleware/opensearch_internet/_search', out, json.dumps(q))
        hits = json.loads(out.read_text(encoding='utf-8'))['hits']['hits']
        if len(hits) < 100:
            break
        n += 100
    print('listed', n + len(hits))


def list_paths(sub: str = 'list') -> list[str]:
    paths = []
    for f in sorted((CACHE / sub).glob('from*.json')):
        for h in json.loads(f.read_text(encoding='utf-8'))['hits']['hits']:
            u = (h['_source'].get('url') or [''])[0]
            if u.startswith('/lrgv/gesetz/' if sub == 'list' else '/lrgv/') and u not in paths:
                paths.append(u)
    return paths


def act(path: str):
    d = CACHE / 'act' / name(path)
    cur = d / 'current.html'
    if get(BASE + path, cur) != 200:
        return
    for v in sorted(set(re.findall(r"<li class=\"version-item[^\"]*\"><a href='(/lrgv/[^']+)'", cur.read_text(encoding='utf-8')))):
        get(BASE + v, d / 'v' / (vname(v) + '.html'))


if __name__ == '__main__':
    if sys.argv[1] == 'list':
        listing()
    elif sys.argv[1] == 'list-vo':
        listing('Rechtsverordnung')
    elif sys.argv[1] == 'list-vo-nohist':
        listing('Rechtsverordnung', nohist=True)
    elif sys.argv[1] == 'acts-vo':
        for n, p in enumerate(list_paths('list-vo')):
            act(p)
            print(n, p, flush=True)
        (CACHE / 'vo-done').write_text(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + chr(10))
    elif sys.argv[1] == 'acts':
        paths = ([VERF] + [p for p in list_paths() if 'verfassung-fuer-das-land' not in p]) if sys.argv[2:] == ['--all'] else sys.argv[2:]
        for n, p in enumerate(paths):
            act(p)
            print(n, p, flush=True)
