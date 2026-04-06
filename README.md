# embed-google-fonts

Ersetzt Google Fonts `@import`-Referenzen in HTML-Dateien durch lokal eingebettete Schriften (Base64/woff2).

Die resultierende Datei macht **keine externen Anfragen** mehr an Google-Server – datenschutzkonform gemäss DSGVO und Schweizer DSG, und vollständig offline-fähig.

## Problem

Eine typische HTML-Datei mit Google Fonts enthält:

```css
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond...');
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

## Beispiel-Output

```
Eingabe:  meine-seite.html (45 KB)
Ausgabe:  meine-seite_offline.html

Gefundene Google Fonts @imports: 1

▶ https://fonts.googleapis.com/css2?family=EB+Garamond...
  CSS geladen (12483 Zeichen)
  ↓ https://fonts.gstatic.com/s/ebgaramond/v30/...woff2
    → 38 KB eingebettet
  ↓ https://fonts.gstatic.com/s/ebgaramond/v30/...woff2
    → 41 KB eingebettet
  [...]

✓ Fertig! 1 @import(s) ersetzt.
  45 KB → 412 KB
  Keine externen Font-Anfragen mehr.
```

## Wie es funktioniert

1. Das Script sucht alle `@import url('https://fonts.googleapis.com/...')` in der HTML-Datei
2. Für jeden gefundenen Import wird die Google Fonts CSS-Datei abgerufen
3. Aus der CSS-Datei werden alle `.woff2`-URLs extrahiert
4. Jede Schriftdatei wird heruntergeladen und als Base64-Data-URI kodiert
5. Die URLs werden im CSS durch die Data-URIs ersetzt
6. Der `@import`-Ausdruck wird durch das vollständige eingebettete CSS ersetzt

## Einschränkungen

- Funktioniert nur mit `@import url(...)` – nicht mit `<link rel="stylesheet" href="...">` (Pull Requests willkommen)
- Unterstützt nur woff2-Fonts (der aktuelle Standard; ältere Formate wie ttf/eot werden nicht eingebettet)
- Die Ausgabedatei ist deutlich grösser als das Original – das ist normal und erwünscht

## Entstehung

Entwickelt von Marco Tedaldi in Zusammenarbeit mit [Claude](https://claude.ai) (Anthropic) als Teil des [Lektionar-Register](https://github.com/mtedaldi/Lektionar-Register)-Projekts.

KI-gestützte Entwicklung wird hier bewusst transparent gemacht.

## Lizenz

MIT License – siehe [LICENSE](LICENSE)
