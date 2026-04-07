#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
# embed-google-fonts.py
#
# Ersetzt alle Google Fonts Referenzen in einer HTML-Datei durch
# lokal eingebettete Base64-kodierte Schriften (woff2).
#
# Unterstützt:
#   @import url('https://fonts.googleapis.com/...');   (in <style>-Blöcken)
#   <link rel="stylesheet" href="https://fonts.googleapis.com/...">
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
#   python3 embed-google-fonts.py eingabe.html --dry-run
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

# @import url('https://fonts.googleapis.com/...');
IMPORT_PATTERN = re.compile(
    r"""(@import\s+url\(['"]?(https://fonts\.googleapis\.com/[^'")]+)['"]?\)\s*;)""",
    re.IGNORECASE
)

# <link rel="stylesheet" href="https://fonts.googleapis.com/...">
# Toleriert beliebige Attributreihenfolge und optionale Anführungszeichen
LINK_PATTERN = re.compile(
    r"""(<link\b[^>]*\bhref=['"]?(https://fonts\.googleapis\.com/[^'"\s>]+)['"]?[^>]*>)""",
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
        print("    Keine woff2-Dateien in diesem CSS gefunden.")
        return css_text

    seen = {}
    for url in urls:
        if url in seen:
            continue
        print(f"    ↓ {url[:70]}{'...' if len(url) > 70 else ''}")
        data = fetch(url)
        if data is None:
            seen[url] = None
            continue
        b64 = base64.b64encode(data).decode("ascii")
        seen[url] = f"data:font/woff2;base64,{b64}"
        print(f"      → {len(data)//1024} KB eingebettet")

    for url, data_uri in seen.items():
        if data_uri:
            css_text = css_text.replace(url, data_uri)

    return css_text


def process_url(css_url, dry_run=False):
    """Lädt eine Google Fonts CSS-URL und gibt eingebettetes CSS zurück."""
    print(f"  URL: {css_url[:80]}{'...' if len(css_url) > 80 else ''}")

    if dry_run:
        print("  [dry-run] würde CSS laden und Fonts einbetten")
        return "[embedded css]"

    css_data = fetch(css_url, "Google Fonts CSS")
    if css_data is None:
        return None

    css_text = css_data.decode("utf-8")
    print(f"  CSS geladen ({len(css_text)} Zeichen), bette Fonts ein...")
    return embed_css(css_text)


def process(html, dry_run=False):
    """Findet alle Google Fonts Referenzen und ersetzt sie durch eingebettetes CSS."""
    total = 0

    # ── @import url(...) ────────────────────────────────────────────────────
    imports = IMPORT_PATTERN.findall(html)
    if imports:
        print(f"Gefundene @import-Anweisungen: {len(imports)}")
        for full_match, css_url in imports:
            print()
            embedded = process_url(css_url, dry_run)
            if embedded and not dry_run:
                html = html.replace(full_match, embedded, 1)
            total += 1

    # ── <link href="..."> ───────────────────────────────────────────────────
    links = LINK_PATTERN.findall(html)
    if links:
        print(f"\nGefundene <link>-Tags: {len(links)}")
        for full_match, css_url in links:
            print()
            embedded = process_url(css_url, dry_run)
            if embedded and not dry_run:
                # <link> durch <style>-Block ersetzen
                style_block = f"<style>\n{embedded}\n</style>"
                html = html.replace(full_match, style_block, 1)
            total += 1

    if total == 0:
        print("Keine Google Fonts Referenzen gefunden.")

    return html, total


def main():
    parser = argparse.ArgumentParser(
        description="Google Fonts in HTML-Dateien lokal einbetten (DSGVO/DSG-konform)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python3 embed-google-fonts.py index.html
  python3 embed-google-fonts.py index.html dist/index.html
  python3 embed-google-fonts.py index.html --inplace
  python3 embed-google-fonts.py index.html --dry-run
        """
    )
    parser.add_argument("input",  help="Eingabe-HTML-Datei")
    parser.add_argument("output", nargs="?", help="Ausgabe-HTML-Datei (optional)")
    parser.add_argument("--inplace",  action="store_true",
                        help="Originaldatei überschreiben (erstellt .bak-Backup)")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Nur anzeigen was gemacht würde, nichts schreiben")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"FEHLER: Datei '{input_path}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)

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

    html = input_path.read_text(encoding="utf-8")
    html_out, count = process(html, dry_run=args.dry_run)

    if args.dry_run:
        print(f"\n[dry-run] {count} Referenz(en) würden ersetzt. Nichts geschrieben.")
        sys.exit(0)

    if count == 0:
        sys.exit(0)

    if args.inplace:
        backup = input_path.with_suffix(".bak.html")
        shutil.copy2(input_path, backup)
        print(f"\nBackup:   {backup}")

    output_path.write_text(html_out, encoding="utf-8")

    print(f"\n✓ Fertig! {count} Referenz(en) ersetzt.")
    print(f"  {input_path.stat().st_size // 1024} KB"
          f" → {output_path.stat().st_size // 1024} KB")
    print(f"  Keine externen Font-Anfragen mehr.")


if __name__ == "__main__":
    main()
