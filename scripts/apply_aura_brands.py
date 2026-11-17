#!/usr/bin/env python3
"""Apply AURA display names + font links across vuln-arena apps. Skin only."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROME = (ROOT / "shared" / "ui" / "chrome.css").read_text(encoding="utf-8")

RENAMES = [
    ("Meridian Ledger", "Ledgerly"),
    ("Souk &amp; Co", "Morrow Market"),
    ("Souk & Co", "Morrow Market"),
    ("Relay Hub", "Relaywork"),
    ("Mirror Edge", "Northstar Edge"),
    ("North Desk", "Goodline"),
    ("Ink &amp; Folio", "Margin"),
    ("Ink & Folio", "Margin"),
    ("Pulse Ops", "Signalwatch"),
    ("VaultLite", "Lockbox"),
    ("Forge Pipeline", "Foundry CI"),
    ("Studio Canvas", "Kiteboard"),
    ("Canvas Board", "Kiteboard"),
    ("Spool Queue", "Backlog"),
    ("Atlas Collective", "Alder & Rowe"),
]

# Prefer replacing full Google Fonts hrefs per theme
FONTS = {
    "ledger": "https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Manrope:wght@400;500;600;700;800&display=swap",
    "bazaar": "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Karla:wght@400;500;600;700&display=swap",
    "relay": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap",
    "mirror": "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Source+Sans+3:wght@400;500;600;700&display=swap",
    "desk": "https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Work+Sans:wght@400;500;600;700&display=swap",
    "ink": "https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap",
    "pulse": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Sora:wght@400;500;600;700&display=swap",
    "vaultlite": "https://fonts.googleapis.com/css2?family=Newsreader:wght@400;500;600;700&family=Public+Sans:wght@400;500;600;700&display=swap",
    "forge": "https://fonts.googleapis.com/css2?family=Anton&family=Noto+Sans:wght@400;500;600;700&display=swap",
    "canvas": "https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:wght@400;500;600;700;800&display=swap",
    "spool": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap",
    "atlas": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Figtree:wght@400;500;600;700&display=swap",
}

APP_GLOBS = {
    "ledger": ["apps/ledger/**/*"],
    "bazaar": ["apps/bazaar/**/*"],
    "relay": ["apps/relay/**/*"],
    "mirror": ["apps/mirror/**/*"],
    "desk": ["apps/desk/**/*"],
    "ink": ["apps/ink/**/*"],
    "pulse": ["apps/pulse/**/*"],
    "vaultlite": ["apps/vaultlite/**/*"],
    "forge": ["apps/forge/**/*"],
    "canvas": ["apps/canvas/**/*"],
    "spool": ["apps/spool/**/*"],
    "atlas": ["apps/atlas/**/*"],
}

TEXT_EXT = {".html", ".php", ".js", ".py", ".rb", ".java", ".go", ".css", ".md"}


def files_for(app: str) -> list[Path]:
    out: list[Path] = []
    for pattern in APP_GLOBS[app]:
        out.extend(ROOT.glob(pattern))
    return [p for p in out if p.is_file() and p.suffix.lower() in TEXT_EXT]


def replace_fonts(text: str, url: str) -> str:
    return re.sub(
        r'https://fonts\.googleapis\.com/css2\?[^"\'\s>]+',
        url,
        text,
    )


def sync_embedded_css(path: Path, marker_start: str, marker_end: str | None = None) -> bool:
    """Replace a raw-string / heredoc body that previously held chrome.css."""
    raw = path.read_text(encoding="utf-8")
    # desk Java text block between CHROME_CSS = """ and closing """
    if path.suffix == ".java":
        m = re.search(r'(static final String CHROME_CSS = """)(.*?)(""")', raw, re.S)
        if not m:
            return False
        path.write_text(raw[: m.start(2)] + "\n" + CHROME + m.group(3) + raw[m.end(3) :], encoding="utf-8")
        return True
    if path.suffix == ".rb":
        m = re.search(r"(CHROME_CSS = <<~'CHROME_CSS_BODY'\n)(.*?)(\nCHROME_CSS_BODY)", raw, re.S)
        if not m:
            return False
        path.write_text(raw[: m.start(2)] + CHROME + m.group(3) + raw[m.end(3) :], encoding="utf-8")
        return True
    if path.name == "main.go" and "chromeCSS" in raw:
        # Go raw string `...` assigned to chromeCSS — find const/var block
        m = re.search(r'(chromeCSS\s*=\s*`)(.*?)(`)', raw, re.S)
        if not m:
            m = re.search(r'(var chromeCSS\s*=\s*`)(.*?)(`)', raw, re.S)
        if not m:
            return False
        path.write_text(raw[: m.start(2)] + CHROME + m.group(3) + raw[m.end(3) :], encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for app, url in FONTS.items():
        for path in files_for(app):
            if path.name == "chrome.css":
                continue
            text = path.read_text(encoding="utf-8")
            orig = text
            for a, b in RENAMES:
                text = text.replace(a, b)
            if path.suffix == ".html" or (path.suffix == ".php" and "<" in text):
                text = text.replace("Alder & Rowe", "Alder &amp; Rowe")
                text = text.replace("Souk & Co", "Morrow Market")  # already handled
            text = replace_fonts(text, url)
            if text != orig:
                path.write_text(text, encoding="utf-8")
                changed += 1
                print(f"updated {path.relative_to(ROOT)}")

    for emb in [
        ROOT / "apps" / "desk" / "Main.java",
        ROOT / "apps" / "ink" / "app.rb",
        ROOT / "apps" / "spool" / "main.go",
        ROOT / "apps" / "mirror" / "main.go",
    ]:
        if emb.exists() and sync_embedded_css(emb, ""):
            print(f"synced embedded css {emb.relative_to(ROOT)}")
            changed += 1

    print(f"done files_touched≈{changed}")


if __name__ == "__main__":
    main()
