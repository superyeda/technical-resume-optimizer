#!/usr/bin/env python3
"""Check the page count of an HTML resume when printed to A4 PDF.

Uses a local Chrome/Edge (headless) to print the HTML to PDF, then counts
pages. Falls back gracefully with clear messages if no browser is found.

Usage:
    python check_resume_pages.py <resume.html> [--browser PATH]
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Common browser locations per OS
BROWSER_CANDIDATES = [
    # Windows (most likely)
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    # Linux
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/microsoft-edge",
]


def find_browser(explicit: str | None) -> str | None:
    if explicit:
        if os.path.isfile(explicit):
            return explicit
        return None
    for candidate in BROWSER_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    for name in ("chrome", "google-chrome", "chromium", "msedge", "microsoft-edge"):
        path = shutil.which(name)
        if path:
            return path
    return None


def count_pages(pdf_path: str) -> int:
    """Count pages by scanning /Type /Page objects (skips /Pages parent)."""
    with open(pdf_path, "rb") as f:
        data = f.read()
    # Chromium PDFs store objects uncompressed in predictable order;
    # a robust-enough heuristic: count '/Type /Page' that is NOT '/Type /Pages'.
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    return max(pages, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Count A4 print pages of an HTML resume.")
    parser.add_argument("html_file", type=Path, help="Path to the resume HTML file")
    parser.add_argument("--browser", default=None, help="Explicit path to Chrome/Edge executable")
    args = parser.parse_args()

    html = args.html_file
    if not html.is_file():
        raise SystemExit(f"HTML file not found: {html}")

    browser = find_browser(args.browser)
    if not browser:
        print("WARN: No Chrome/Edge found. Open the HTML in a browser and press Ctrl+P to check page count manually.")
        print("PAGES: unknown")
        raise SystemExit(2)

    uri = html.resolve().as_uri()
    with tempfile.TemporaryDirectory() as tmp:
        pdf = os.path.join(tmp, "resume.pdf")
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf}",
            "--print-to-pdf-no-header",
            uri,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0 or not os.path.isfile(pdf):
            print(f"WARN: Browser print failed: {result.stderr.strip() or result.stdout.strip()}")
            print("PAGES: unknown")
            raise SystemExit(2)

        pages = count_pages(pdf)
        print(f"PAGES: {pages}")
        print(f"PDF: {pdf}")
        if pages > 2:
            print("HINT: Over 2 pages. Options: (A) compress spacing/font, "
                  "(B) ask user: increase pages (max 3) or trim content.")


if __name__ == "__main__":
    main()
