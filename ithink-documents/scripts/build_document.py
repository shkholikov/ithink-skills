#!/usr/bin/env python3
"""
Inlines ITHINK brand assets into a document so the result is fully
self-contained.

This exists because published artifacts run under a strict CSP that blocks
every external host — no Google Fonts, no remote images. A document that
looks right locally will silently fall back to a system font once published
unless the font is embedded as a data URI. The same self-contained file is
also what makes print-to-PDF reliable, since nothing has to be fetched while
the print dialog is open.

Usage:
    build_document.py <input.html> [-o output.html] [--pdf]

Placeholders substituted in the input:
    @@INTER@@                   the full @font-face block, fonts base64-inlined
    @@LOGO:<name>@@             a data: URI for assets/logos/<name>.png

Example:
    <style>@@INTER@@ body { font-family: Inter, sans-serif; }</style>
    <img src="@@LOGO:ithink-horizontal-color@@" alt="ITHINK">

Unknown logo names fail loudly rather than emitting a broken image.
"""

import argparse
import base64
import pathlib
import re
import shutil
import subprocess
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
FONTS = SKILL / 'assets/fonts'
LOGOS = SKILL / 'assets/logos'

# Subset ranges as published by Google Fonts. Cyrillic covers Russian; the
# Latin subset covers Uzbek, including the oʻ / gʻ modifier letters
# (U+02BB, U+02BC) that Uzbek orthography depends on.
UNICODE_RANGES = {
    'latin': (
        'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, '
        'U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, '
        'U+2193, U+2212, U+2215, U+FEFF, U+FFFD'
    ),
    'latin-ext': (
        'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, '
        'U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, '
        'U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF'
    ),
    'cyrillic': 'U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116',
}


def font_faces() -> str:
    """One @font-face per subset. Inter is variable, so 100-900 comes from one file."""
    blocks = []

    for subset, unicode_range in UNICODE_RANGES.items():
        path = FONTS / f'inter-{subset}.woff2'
        if not path.exists():
            sys.exit(f'missing font: {path}')

        encoded = base64.b64encode(path.read_bytes()).decode('ascii')
        blocks.append(
            '@font-face{'
            "font-family:'Inter';"
            'font-style:normal;'
            'font-weight:100 900;'
            'font-display:swap;'
            f"src:url(data:font/woff2;base64,{encoded}) format('woff2');"
            f'unicode-range:{unicode_range};'
            '}'
        )

    return ''.join(blocks)


def logo_uri(name: str) -> str:
    path = LOGOS / f'{name}.png'
    if not path.exists():
        available = sorted(p.stem for p in LOGOS.glob('*.png'))
        sys.exit(f'unknown logo {name!r}. Available: {", ".join(available) or "none"}')

    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:image/png;base64,{encoded}'


CHROME_CANDIDATES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    'google-chrome',
    'chromium',
]


def to_pdf(html: pathlib.Path) -> pathlib.Path:
    """Print to PDF headlessly so the final export is not a manual print dialog."""
    chrome = next(
        (c for c in CHROME_CANDIDATES if pathlib.Path(c).exists() or shutil.which(c)),
        None,
    )
    if not chrome:
        sys.exit('Chrome not found — open the HTML and print to PDF manually (A4, backgrounds on)')

    pdf = html.with_suffix('.pdf')
    subprocess.run(
        [
            chrome,
            '--headless',
            '--disable-gpu',
            '--no-pdf-header-footer',
            f'--print-to-pdf={pdf}',
            html.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
    )
    return pdf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=pathlib.Path)
    parser.add_argument('-o', '--output', type=pathlib.Path)
    parser.add_argument('--pdf', action='store_true', help='also render a PDF')
    args = parser.parse_args()

    html = args.input.read_text(encoding='utf-8')

    if '@@INTER@@' in html:
        html = html.replace('@@INTER@@', font_faces())

    html = re.sub(r'@@LOGO:([a-z0-9\-]+)@@', lambda m: logo_uri(m.group(1)), html)

    leftover = re.findall(r'@@[A-Z]+[^@]*@@', html)
    if leftover:
        sys.exit(f'unsubstituted placeholders remain: {sorted(set(leftover))}')

    output = args.output or args.input.with_name(f'{args.input.stem}.built.html')
    output.write_text(html, encoding='utf-8')

    print(f'{output}  {output.stat().st_size / 1024:.0f} KB')

    if args.pdf:
        pdf = to_pdf(output)
        print(f'{pdf}  {pdf.stat().st_size / 1024:.0f} KB')


if __name__ == '__main__':
    main()
