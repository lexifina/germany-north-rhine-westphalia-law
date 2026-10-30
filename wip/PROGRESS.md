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
