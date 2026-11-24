<!-- lawwatch: written from data/checks by the check trail; edit the records, not this page -->

# Monitoring: what is read and what came of it

[Deutsch](README.md)

How global-law monitors every country: [global-law monitoring/](https://github.com/lexifina/global-law/tree/main/monitoring). This page is the same for North Rhine-Westphalia only: every time an official source is read, when, and what came of it (acts added, changed and removed). The machine-readable form is [data/checks/](../data/checks/) (JSON Lines, schema `lexifina-check/1`), in `git log` as `Kind: check` commits, and month by month in [checks/](checks/).

**Last check:** 2026-11-24 07:09 UTC, RECHT.NRW (Ministry of the Interior of North Rhine-Westphalia): 12 addresses read; 0 added, 0 changed, 0 removed; no change; 14 not published, 0 of them with no reason.

## Sources

| Source | Folders | How often | Last successful check | Last result | State |
| --- | --- | --- | --- | --- | --- |
| [RECHT.NRW (Ministry of the Interior of North Rhine-Westphalia)](https://recht.nrw.de) | `<act>/` | daily | 2026-11-24 07:09 UTC | no change | watched |

## The last 30 days

| Started (UTC) | Source | Read | Added | Changed | Removed | Not published (no reason) | Result | Commits |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| [2026-11-24 07:08](checks/2026-11.md#de-recht-nrw-20261124t070848z) | recht-nrw | 12 | 0 | 0 | 0 | 14 (0) | no change | — |
| [2026-11-23 23:34](checks/2026-11.md#de-recht-nrw-20261123t233419z) | recht-nrw | 12 | 0 | 0 | 0 | 14 (0) | no change | — |
| [2026-11-23 20:34](checks/2026-11.md#de-recht-nrw-20261123t203417z) | recht-nrw | 26 | 0 | 0 | 0 | 14 (0) | no change | — |

## Check it yourself

```
python tools/checktrail.py                      # the latest check of every source
python tools/checktrail.py --day 2026-11-23     # every check of a day
python tools/checktrail.py --act <id>           # when an act was seen and published
git log --grep='^Kind: check' --format='%ci %s'  # the checks in the history
```

Only the official publication has legal force; the texts here are copies for reading and searching.
