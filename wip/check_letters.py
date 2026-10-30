"""Independent letters-and-digits check of every version against its raw RECHT.NRW page (regex, no HTML parser).

    python -X utf8 check_letters.py [part.json ...]

Private. The text of the page's provision sections (legaldoc-article) without footnotes, buttons, print menus and
alerts, reduced to letters and digits, must equal the version's provision files placed one after another in order.
"""
import html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def ld(s):
    return ''.join(ch for ch in s if ch.isalnum())


def number_items(m) -> str:
    """The numbers the browser shows for an <ol> (1., 2., ... or a), b), ...)."""
    typ = re.search(r'type="(\w)"', m.group(1))
    start = re.search(r'start="(\d+)"', m.group(1))
    n = [int(start.group(1)) if start else 1]

    def mark(_):
        x = n[0]
        n[0] += 1
        return f'<li>{chr(96 + x) if typ and typ.group(1) == "a" else x} '
    return re.sub(r'<li[^>]*>', mark, m.group(2))


def source(raw: str) -> str:
    i = raw.index('<section class="legaldoc-')
    p = raw.find('<div class="field field--field_preamble')
    if 0 <= p < i:
        i = p
    j = raw.rindex('<a', i, raw.index('id="backToTextTop"', i))
    s = raw[i:j]  # preamble, every provision and structure heading, and the closing formula, in page order
    s = re.sub(r'(?s)<ol([^>]*)>(.*?)</ol>', number_items, s)
    s = re.sub(r'(?s)<div class="field field--field_footnote_description.*?</div></div>', ' ', s)
    s = re.sub(r'(?s)<div class="footnote-container">.*?<div class="card card-body footnote-content">.*?</div>\s*</div>',
               ' ', s)  # the per-provision footnote box of some Rechtsverordnungen ("Fußnoten zu § 2 ...")
    s = re.sub(r'(?s)<div class="field field--field_reference">.*?</a>\s*</div>\s*</div>', ' ', s)
    s = re.sub(r'(?s)<div class="alert.*?</button>|<button.*?</button>|<ul class="print-copy-overlay.*?</ul>', ' ', s)
    return ld(html.unescape(re.sub(r'<[^>]+>', ' ', s)).replace('­', ''))


def main(paths):
    bad = total = 0
    for p in paths:
        c = json.load(open(p, encoding='utf-8'))
        for a in c['acts']:
            name = a['url'].rsplit('/', 1)[1]
            for v in a['versions']:
                stem = v['source_url'].rsplit('/', 1)[1]
                f = HERE / '.cache' / 'act' / name / ('current.html' if stem == name else
                                                      f'v/{stem[:8] if stem[:8].isdigit() else stem[:60]}.html')
                src = source(f.read_text(encoding='utf-8'))
                rest = {k: ld(u['text']) for k, u in v['units'].items()}
                pos = 0
                while rest:
                    hit = max((k for k, t in rest.items() if src.startswith(t, pos)), key=lambda k: len(rest[k]), default=None)
                    if hit is None:
                        break
                    pos += len(rest.pop(hit))
                total += 1
                if rest or pos != len(src):
                    bad += 1
                    print(f'MISMATCH {a["slug"]} {v["from"]}: {pos}/{len(src)}; next {src[pos:pos+70]!r}; unplaced {list(rest)[:4]}')
    print(f'{total} versions checked, {bad} mismatches')
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1:] or sorted(str(p) for p in (HERE / 'corpus.d').glob('*.json'))) else 0)
