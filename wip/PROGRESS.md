# North Rhine-Westphalia (germany-north-rhine-westphalia-law) - private

State 2026-10-30 11:25 UTC (gitlaw-scraper-dell, NRW fork):
- Source RECHT.NRW (recht.nrw.de). Gates pass: robots Drupal defaults (no AI rules, no Crawl-delay), no terms restricting reuse, no challenge, § 5 UrhG.
- List: 129 Gesetze in force from the site's own search middleware (POST /search-middleware/opensearch_internet/_search, filter field_document_type_name=Gesetz, field_historically=false).
- Built: Verfassung (2 structured Fassungen, 2020-07-14, 2026-01-16) + 128 Gesetze in 3 parts (20-gesetze-01..03), 237 versions, all with .PUBLISH.
- Not used: older Fassungen shown only as legacy files (/system/files/BH/*.htm or *.pdf in a pdf.js iframe). Next step for deeper history: parse the legacy .htm files (old SGV.NRW HTML); PDFs need a text layer check.
- Not yet: Rechtsverordnungen (2,372 docs in the index), Verwaltungsvorschriften.
- Cache gotcha: version pages are cached under their date prefix (v/DDMMYYYY.html) because full slugs exceeded the Windows path limit and were saved empty.
