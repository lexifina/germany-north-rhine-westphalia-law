<!-- lawwatch: written from data/checks by the check trail; edit the records, not this page -->

# Beobachtung: was gelesen wird und was daraus folgte

[English](README.en.md)

Wie global-law jedes Land beobachtet: [global-law monitoring/](https://github.com/lexifina/global-law/tree/main/monitoring). Diese Seite zeigt dasselbe nur für Nordrhein-Westfalen: jedes Lesen einer amtlichen Quelle, wann, und was daraus folgte (Vorschriften hinzugefügt, geändert und entfernt). Maschinenlesbar in [data/checks/](../data/checks/) (JSON Lines, Schema `lexifina-check/1`), in `git log` als Commits mit `Kind: check` und Monat für Monat in [checks/](checks/).

**Letzte Prüfung:** 2026-11-25 07:00 UTC, RECHT.NRW (Ministerium des Innern des Landes Nordrhein-Westfalen): 15 Adressen gelesen; 3 hinzugefügt, 0 geändert, 2 entfernt; Änderungen gefunden; 17 nicht veröffentlicht, davon 0 ohne Grund.

## Quellen

| Quelle | Ordner | Wie oft | Letzte erfolgreiche Prüfung | Letztes Ergebnis | Stand |
| --- | --- | --- | --- | --- | --- |
| [RECHT.NRW (Ministerium des Innern des Landes Nordrhein-Westfalen)](https://recht.nrw.de) | `<act>/` | täglich | 2026-11-25 07:00 UTC | Änderungen gefunden | beobachtet |

## Die letzten 30 Tage

| Beginn (UTC) | Quelle | Gelesen | Hinzugefügt | Geändert | Entfernt | Nicht veröffentlicht (ohne Grund) | Ergebnis | Commits |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| [2026-11-25 07:00](checks/2026-11.md#de-recht-nrw-20261125t070020z) | recht-nrw | 15 | 3 | 0 | 2 | 17 (0) | Änderungen gefunden | — |
| [2026-11-24 07:08](checks/2026-11.md#de-recht-nrw-20261124t070848z) | recht-nrw | 12 | 0 | 0 | 0 | 14 (0) | keine Änderung | — |
| [2026-11-23 23:34](checks/2026-11.md#de-recht-nrw-20261123t233419z) | recht-nrw | 12 | 0 | 0 | 0 | 14 (0) | keine Änderung | — |
| [2026-11-23 20:34](checks/2026-11.md#de-recht-nrw-20261123t203417z) | recht-nrw | 26 | 0 | 0 | 0 | 14 (0) | keine Änderung | — |

## Selbst prüfen

```
python tools/checktrail.py                      # die letzte Prüfung jeder Quelle
python tools/checktrail.py --day 2026-11-23     # jede Prüfung eines Tages
python tools/checktrail.py --act <id>           # wann eine Vorschrift gesehen und veröffentlicht wurde
git log --grep='^Kind: check' --format='%ci %s'  # die Prüfungen in der Historie
```

Rechtskraft hat nur die amtliche Verkündung; die Texte hier sind Kopien zum Lesen und Suchen.
