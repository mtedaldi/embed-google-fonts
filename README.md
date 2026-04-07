# embed-google-fonts

Ersetzt Google Fonts Referenzen in HTML-Dateien durch lokal eingebettete Schriften (Base64/woff2).

Die resultierende Datei macht **keine externen Anfragen** mehr an Google-Server – datenschutzkonform gemäss DSGVO und Schweizer DSG, und vollständig offline-fähig.

## Problem

HTML-Dateien mit Google Fonts enthalten typischerweise:

```css
@import url('https://fonts.googleapis.com/css2?family=...');
```

oder:

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=...">
```

Beim Laden der Seite sendet der Browser eine Anfrage an Google-Server. Dabei wird die IP-Adresse des Benutzers übermittelt. Ein deutsches Gericht hat das 2022 als DSGVO-Verletzung eingestuft (LG München, Az. 3 O 17493/20).

## Lösung

Dieses Tool lädt die Schriften einmalig herunter und bettet sie direkt in die HTML-Datei ein. Danach ist keine Netzwerkverbindung mehr nötig.

## Voraussetzungen

- Python 3.6 oder neuer
- Keine externen Pakete nötig (nur Standardbibliothek)
- Internetverbindung beim ersten Aufruf (um die Fonts herunterzuladen)

## Verwendung

```bash
# Einfachster Aufruf – erzeugt eingabe_offline.html
python3 embed-google-fonts.py eingabe.html

# Ausgabedatei explizit angeben
python3 embed-google-fonts.py eingabe.html ausgabe.html

# Originaldatei direkt überschreiben (erstellt automatisch .bak-Backup)
python3 embed-google-fonts.py eingabe.html --inplace

# Nur anzeigen was gemacht würde, nichts schreiben
python3 embed-google-fonts.py eingabe.html --dry-run
```

## Unterstützte Referenztypen

| Typ | Beispiel |
|-----|---------|
| `@import` in `<style>` | `@import url('https://fonts.googleapis.com/...');` |
| `<link>` im `<head>` | `<link rel="stylesheet" href="https://fonts.googleapis.com/...">` |

`<link>`-Tags werden durch einen äquivalenten `<style>`-Block ersetzt.

## Beispiel-Output

```
Eingabe:  meine-seite.html (45 KB)
Ausgabe:  meine-seite_offline.html

Gefundene @import-Anweisungen: 1

  URL: https://fonts.googleapis.com/css2?family=EB+Garamond...
  CSS geladen (12483 Zeichen), bette Fonts ein...
    ↓ https://fonts.gstatic.com/s/ebgaramond/v30/...woff2
      → 38 KB eingebettet
    ↓ https://fonts.gstatic.com/s/ebgaramond/v30/...woff2
      → 41 KB eingebettet
    [...]

✓ Fertig! 1 Referenz(en) ersetzt.
  45 KB → 412 KB
  Keine externen Font-Anfragen mehr.
```

## Wie es funktioniert

1. Das Script sucht alle Google Fonts Referenzen (`@import` und `<link>`) in der HTML-Datei
2. Für jede gefundene Referenz wird die Google Fonts CSS-Datei abgerufen
3. Aus der CSS-Datei werden alle `.woff2`-URLs extrahiert
4. Jede Schriftdatei wird heruntergeladen und als Base64-Data-URI kodiert
5. Die URLs werden im CSS durch die Data-URIs ersetzt
6. Die ursprüngliche Referenz wird durch das vollständige eingebettete CSS ersetzt

## GitHub Actions

Das Tool lässt sich einfach in einen automatisierten Build-Workflow einbinden, sodass Fonts bei jedem Push automatisch eingebettet werden. Siehe [GITHUB_ACTION.md](GITHUB_ACTION.md) für Beispiele.

## Einschränkungen

- Unterstützt nur woff2-Fonts (der aktuelle Standard; ältere Formate wie ttf/eot werden nicht eingebettet)
- Die Ausgabedatei ist deutlich grösser als das Original – das ist normal und erwünscht
- Funktioniert nur mit Google Fonts – andere Font-CDNs werden nicht verarbeitet

## Entstehung

Entwickelt von Marco Tedaldi in Zusammenarbeit mit [Claude](https://claude.ai) (Anthropic) als Teil des [Lektionar-Register](https://github.com/mtedaldi/Lektionar-Register)-Projekts.

KI-gestützte Entwicklung wird hier bewusst transparent gemacht.

## Lizenz

MIT License – siehe [LICENSE](LICENSE)
