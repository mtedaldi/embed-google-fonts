# GitHub Actions Integration

`embed-google-fonts.py` lässt sich als GitHub Action in einen Build-Workflow einbinden, sodass Fonts bei jedem Push automatisch eingebettet werden.

## Grundprinzip

Der Workflow läuft bei jedem Push, führt das Script aus und committet das Ergebnis zurück ins Repository – oder deployt es direkt auf GitHub Pages.

---

## Beispiel 1 – Einfach: Script ausführen und committen

Geeignet wenn die Quelldatei (`index.html`) im Repository liegt und das Ergebnis (`index_offline.html`) ebenfalls eingecheckt werden soll.

```yaml
# .github/workflows/embed-fonts.yml
name: Embed Google Fonts

on:
  push:
    branches: [main]
    paths:
      - "index.html"          # Nur auslösen wenn index.html geändert wurde
      - "embed-google-fonts.py"

jobs:
  embed:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Python einrichten
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Fonts einbetten
        run: python3 embed-google-fonts.py index.html index_offline.html

      - name: Änderungen committen
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add index_offline.html
          git diff --staged --quiet || git commit -m "chore: Google Fonts eingebettet [skip ci]"
          git push
```

---

## Beispiel 2 – Empfohlen: Direkt auf GitHub Pages deployen

Quelldatei mit `@import` bleibt im Repository, die eingebettete Version wird nur für das Deployment verwendet – kein Extra-Commit nötig.

```yaml
# .github/workflows/deploy.yml
name: Deploy mit eingebetteten Fonts

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}

    steps:
      - uses: actions/checkout@v4

      - name: Python einrichten
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Fonts einbetten
        run: |
          python3 embed-google-fonts.py index.html dist/index.html
          # Weitere Dateien ins dist-Verzeichnis kopieren falls nötig
          # cp -r assets/ dist/

      - name: GitHub Pages konfigurieren
        uses: actions/configure-pages@v4

      - name: Artefakt hochladen
        uses: actions/upload-pages-artifact@v3
        with:
          path: dist/

      - name: Auf GitHub Pages deployen
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## Beispiel 3 – Mehrere HTML-Dateien

Wenn das Projekt mehrere HTML-Dateien enthält:

```yaml
      - name: Fonts in allen HTML-Dateien einbetten
        run: |
          mkdir -p dist
          for f in *.html; do
            python3 embed-google-fonts.py "$f" "dist/$f"
          done
```

---

## Hinweise

**`[skip ci]`** im Commit-Message (Beispiel 1) verhindert dass der Workflow sich selbst auslöst und in eine Endlosschleife gerät.

**Caching** – Die Font-Dateien werden bei jedem Workflow-Lauf neu heruntergeladen. Bei häufigen Builds lohnt sich ein Cache:

```yaml
      - name: Font-Cache laden
        uses: actions/cache@v4
        with:
          path: ~/.cache/google-fonts
          key: google-fonts-${{ hashFiles('index.html') }}
```

*(Das Script müsste dazu um ein `--cache-dir`-Argument erweitert werden.)*

**Dry-run testen** – Vor dem ersten echten Einsatz empfiehlt sich ein Test:

```bash
python3 embed-google-fonts.py index.html --dry-run
```

---

## Workflow für dieses Repository (embed-google-fonts selbst)

Das Script hat keine Build-Artefakte – kein eigener Deployment-Workflow nötig. Ein einfacher CI-Check reicht:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Dry-run auf Beispieldatei
        run: python3 embed-google-fonts.py tests/example.html --dry-run
```
