#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
# embed-google-fonts.py
#
# Ersetzt alle Google Fonts @import-Referenzen in einer HTML-Datei durch
# lokal eingebettete Base64-kodierte Schriften (woff2).
#
# Danach macht die Datei keine externen Anfragen mehr an Google-Server –
# datenschutzkonform gemäss DSGVO/DSG, und vollständig offline-fähig.
#
# Voraussetzungen: Python 3.6+, keine externen Pakete nötig
#
# Aufruf:
#   python3 embed-google-fonts.py eingabe.html
#   python3 embed-google-fonts.py eingabe.html ausgabe.html
#   python3 embed-google-fonts.py eingabe.html --inplace
#
# Optionen:
#   --inplace   Originaldatei direkt überschreiben (kein separates Outputfile)
#   --dry-run   Nur anzeigen was gemacht würde, nichts schreiben
# ═══════════════════════════════════════════════════════════════════════════

import sys
import re
import os
import urllib.request
import base64
import argparse
import shutil
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"

GOOGLE_FONTS_PATTERN = re.compile(
    r"""@import\s+url\(['"]?(https://fonts\.googleapis\.com/[^'")]+)['"]?\)\s*;""",
    re.IGNORECASE
)

WOFF2_PATTERN = re.compile(r'(https://[^\s)]+\.woff2)')


def fetch(url, label=""):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read()
    except Exception as e:
        print(f"  FEHLER beim Laden von {label or url}: {e}", file=sys.stderr)
        return None


def embed_css(css_text):
    """Ersetzt alle woff2-URLs in einem CSS-String durch Base64-Data-URIs."""
    urls = WOFF2_PATTERN.findall(css_text)
    if not urls:
        print("  Keine woff2-Dateien in diesem CSS gefunden.")
        return css_text

    # Deduplizieren (gleiche URL kann mehrfach vorkommen für verschiedene Zeichensätze)
    seen = {}
    for url in urls:
        if url in seen:
            continue
        print(f"  ↓ {url[:72]}{'...' if len(url) > 72 else ''}")
        data = fetch(url, url[-40:])
        if data is None:
            seen[url] = None
            continue
        b64 = base64.b64encode(data).decode("ascii")
        seen[url] = f"data:font/woff2;base64,{b64}"
        print(f"    → {len(data)//1024} KB eingebettet")

    for url, data_uri in seen.items():
        if data_uri:
            css_text = css_text.replace(url, data_uri)

    return css_text


def process(html, dry_run=False):
    """Findet alle Google Fonts @imports und ersetzt sie durch eingebettetes CSS."""
    imports = GOOGLE_FONTS_PATTERN.findall(html)

    if not imports:
        print("Keine Google Fonts @import-Anweisungen gefunden.")
        return html, 0

    print(f"Gefundene Google Fonts @imports: {len(imports)}")
    replaced = 0

    for css_url in imports:
        print(f"\n▶ {css_url[:80]}{'...' if len(css_url) > 80 else ''}")

        if dry_run:
            print("  [dry-run] würde CSS laden und Fonts einbetten")
            replaced += 1
            continue

        css_data = fetch(css_url, "Google Fonts CSS")
        if css_data is None:
            print("  Übersprungen.")
            continue

        css_text = css_data.decode("utf-8")
        print(f"  CSS geladen ({len(css_text)} Zeichen)")

        embedded_css = embed_css(css_text)

        # @import-Zeile durch eingebettetes CSS ersetzen
        # Wir ersetzen den gesamten @import url(...); Ausdruck
        import_pattern = re.compile(
            r"""@import\s+url\(['"]?""" + re.escape(css_url) + r"""['"]?\)\s*;""",
            re.IGNORECASE
        )
        html = import_pattern.sub(embedded_css, html)
        replaced += 1

    return html, replaced


def main():
    parser = argparse.ArgumentParser(
        description="Google Fonts in HTML-Dateien lokal einbetten (DSGVO-konform)"
    )
    parser.add_argument("input", help="Eingabe-HTML-Datei")
    parser.add_argument("output", nargs="?", help="Ausgabe-HTML-Datei (optional)")
    parser.add_argument("--inplace", action="store_true",
                        help="Originaldatei überschreiben")
    parser.add_argument("--dry-run", action="store_true",
                        help="Nur anzeigen, nichts schreiben")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"FEHLER: Datei '{input_path}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)

    # Ausgabepfad bestimmen
    if args.inplace:
        output_path = input_path
    elif args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_stem(input_path.stem + "_offline")

    print(f"Eingabe:  {input_path} ({input_path.stat().st_size // 1024} KB)")
    if not args.dry_run:
        print(f"Ausgabe:  {output_path}")
    print()

    # HTML laden
    html = input_path.read_text(encoding="utf-8")

    # Verarbeiten
    html_out, count = process(html, dry_run=args.dry_run)

    if args.dry_run:
        print(f"\n[dry-run] {count} @import(s) würden ersetzt. Nichts geschrieben.")
        return

    if count == 0:
        print("Nichts zu tun.")
        return

    # Backup wenn inplace
    if args.inplace:
        backup = input_path.with_suffix(".bak.html")
        shutil.copy2(input_path, backup)
        print(f"\nBackup:   {backup}")

    # Schreiben
    output_path.write_text(html_out, encoding="utf-8")

    print(f"\n✓ Fertig! {count} @import(s) ersetzt.")
    print(f"  {input_path.stat().st_size // 1024} KB → {output_path.stat().st_size // 1024} KB")
    print(f"  Keine externen Font-Anfragen mehr.")


if __name__ == "__main__":
    main()
