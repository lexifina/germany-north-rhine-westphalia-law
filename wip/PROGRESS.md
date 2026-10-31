# North Rhine-Westphalia (germany-north-rhine-westphalia-law) - private

State 2026-10-30 11:25 UTC (gitlaw-scraper-dell, NRW fork):
- Source RECHT.NRW (recht.nrw.de). Gates pass: robots Drupal defaults (no AI rules, no Crawl-delay), no terms restricting reuse, no challenge, § 5 UrhG.
- List: 129 Gesetze in force from the site's own search middleware (POST /search-middleware/opensearch_internet/_search, filter field_document_type_name=Gesetz, field_historically=false).
- Built: Verfassung (2 structured Fassungen, 2020-07-14, 2026-01-16) + 128 Gesetze in 3 parts (20-gesetze-01..03), 237 versions, all with .PUBLISH.
- Not used: older Fassungen shown only as legacy files (/system/files/BH/*.htm or *.pdf in a pdf.js iframe). Next step for deeper history: parse the legacy .htm files (old SGV.NRW HTML); PDFs need a text layer check.
- Not yet: Rechtsverordnungen (2,372 docs in the index), Verwaltungsvorschriften.
- Cache gotcha: version pages are cached under their date prefix (v/DDMMYYYY.html) because full slugs exceeded the Windows path limit and were saved empty.

State 2026-10-30 ~18:00 UTC (gitlaw-scraper-dell, German Länder fork of the ordinances wave):
- robots re-read 15:45 UTC: Drupal defaults, unchanged; no AI-agent rule, no Crawl-delay; no challenge.
- Published main 118b516 / zukunft a54d72c (autopush_dell verified rebuild 4d497aa -> 118b516, standing approval, lease, old tip archived): Verfassung + 128 Gesetze + 250 Rechtsverordnungen = 379 acts, 666 versions.
- Rechtsverordnungen: `fetch.py list-vo` (same search middleware, field_document_type_name=Rechtsverordnung, field_historically=false: 250; .cache/list-vo/) then `fetch.py acts-vo` (.cache/vo-done). Parts corpus.d/40-verordnungen-01..05. Index has 2,372 Rechtsverordnung docs: 1,489 historical, 633 with no field_historically (not taken, same rule as the Gesetze; worth a look later).
- parse.py: path prefix per act from the list (/lrgv/rechtsverordnung/); VO slugs use the portal abbreviation where unique, else the title slug with the path's date (titles share their first 60 characters). Gesetze parts byte-identical.
- check_letters.py now also removes the per-provision "footnote-container" box (Fußnoten zu § ...), which some Rechtsverordnungen have; the parser already dropped it. Gesetze re-checked: 237 versions, 0.
- Verification: letters 429 VO versions, 0; scratch build check.py 379/666 all zero (world-law/de_ord_verify.py, ordverify.json).
- Not yet: Verwaltungsvorschriften, Bekanntmachungen.

State 2026-10-31 ~03:20 UTC (gitlaw-scraper-dell, coverage wave via global-law-main-composer):
- robots re-read 01:47 UTC: unchanged (Drupal defaults, /search/ disallowed only).
- The 633 Rechtsverordnung index entries with no field_historically: `fetch.py list-vo-nohist` (.cache/list-vo-nohist/). 134 are /gvnrw/ GV. NRW. issue entries (promulgated texts, not consolidated acts): not used. The other 499 are /lrgv/rechtsverordnung/ pages.
- The portal does show status on each page: an ended Fassung carries "Gültig bis" (and the Änderungshistorie "Aufgehoben durch ..."), as on a historically=true sample. `nohist.py fetch` read each landing page; `classify`: all 499 are their act's newest Fassung, none overlaps an act on the in-force lists or another entry, and none shows "Gültig bis" or an "Aufgehoben durch" on or before 2026-10-31 -> all in force (.cache/nohist-status.json). `nohist.py acts` fetched their other Fassungen (all older ones are legacy files, so each act has one structured version).
- parse.py: 40-verordnungen-06..15 (498 acts; 1 Bekanntmachung page gave no structured Fassung), sources retrieved 2026-10-31; parts 10..40-05 byte-identical (cmp). README count updated (748 Rechtsverordnungen).
- Verification (de_ord_verify.py, ordverify-nohist.json): letters 498 versions 0; scratch build 877 acts / 1,164 versions all zero; PUBLISH 06..15. autopush_dell: main 991cd7a -> 55cb516, zukunft a54d72c -> 53658cf (verified rebuild, standing approval, lease, old tips archived). (A first pass at 03:16 failed check because it ran between the parts and their PUBLISH files; the next pass passed.)
- Seen, not changed (published text must not change): three acts on the earlier in-force lists show their own end on their page: 22032017-verordnung-zur-zuweisung-weiterer-aufgaben (Gültig bis 08.12.2025, Aufgehoben 9.12.2025), 01012025-verordnung-ueber-die-erstattungen-von-auf... (Gültig bis 31.12.2025, Aufgehoben 1.1.2026), 12092023-gesetz-zur-ausfuehrung-des-baugesetzbuches (Aufgehoben 1.9.2026). The index still flags them current.
