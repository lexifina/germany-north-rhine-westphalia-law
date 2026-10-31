# North Rhine-Westphalia: law history in git

The law of the Land Nordrhein-Westfalen as a git history: one file per Artikel or Paragraph, one paragraph per line, one commit per amending act on the day the new version took effect. `git blame` names the act behind each change; `git log` lists every change; picking a date gives the text in force that day. The text is German.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

## What this repository holds

Every Fassung of each act that RECHT.NRW shows as structured text, from the oldest such Fassung to the current one. Older Fassungen that the portal shows only as legacy files (PDF or old HTML pages) are not included yet, so each act's history starts with its oldest structured Fassung (for the Verfassung, 14 July 2020), which is credited to the publisher as "oldest version available".

| Folder | Act | History |
| --- | --- | --- |
| `verfassung/` | Verfassung für das Land Nordrhein-Westfalen vom 28. Juni 1950 | every structured Fassung, from 14 July 2020 |
| other folders | the Gesetze in force, one folder per act | every structured Fassung |
| other folders | the Rechtsverordnungen in force (748: the 250 the portal's index marks as current, and 498 it gives no current or historical mark, taken because each one's newest Fassung shows no end of validity and no repeal; read 31 October 2026), one folder per act (named by the portal's abbreviation where it gives one) | every structured Fassung |

Verwaltungsvorschriften are not included yet.

## Source

[RECHT.NRW](https://recht.nrw.de), the service portal of the Ministerium des Innern des Landes Nordrhein-Westfalen: the consolidated Landesrecht, with the earlier Fassungen of each act. The sha256 of each page a version was read from is in `data/versions.json`.

## Dates

Each version is dated by the day RECHT.NRW gives as the start of its validity ("Gültig ab"), at noon in Düsseldorf. Versions in force only after the retrieval date (30 October 2026) are on the `zukunft` branch.

## What "author" means

The provisions that changed between two versions are credited to the amending act(s) that the newer version's Änderungshistorie lists as coming into force on that version's first day. That act is the commit's author, with an e-mail address that cannot exist. A change for which the Änderungshistorie names no act on that day is committed by the publisher and labelled unexplained. The committer is always Lexifina.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

Each RECHT.NRW page becomes one file per provision. Headings of Teile and Abschnitte stand where the portal prints them, at the end of the provision before. Footnotes are left out; tables are one line per row, cells separated by ` | `.

## How it is checked

Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`) and must match the corpus; an independent letters-and-digits comparison of every version against its source page must show no difference. Results are in `REPRODUCE.md`.

## Limits

History only from the oldest structured Fassung; earlier Fassungen and the acts as enacted are not here. The text is not the official version: only the printed Gesetz- und Verordnungsblatt (GV. NRW.) is authoritative.

## Licence

See [LICENSE](LICENSE): the law texts are free of copyright (§ 5 Abs. 1 UrhG). Quelle: RECHT.NRW, Ministerium des Innern des Landes Nordrhein-Westfalen.
