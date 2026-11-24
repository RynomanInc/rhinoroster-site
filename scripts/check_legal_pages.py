#!/usr/bin/env python3
"""Check that /terms and /privacy keep the approved wording and filled blanks."""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILURES: list[str] = []


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = False
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self._skip = False
        if tag in {"p", "li", "h1", "h2"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts)
        raw = raw.replace("\xa0", " ")
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r" *\n *", "\n", raw)
        return raw.strip()


def fail(msg: str) -> None:
    FAILURES.append(msg)


def page_text(path: Path) -> str:
    parser = TextExtractor()
    parser.feed(path.read_text())
    return parser.text()


def must_contain(label: str, text: str, needle: str) -> None:
    if needle not in text:
        fail(f"{label} is missing exact wording: {needle!r}")


def main() -> int:
    terms = page_text(ROOT / "terms/index.html")
    privacy = page_text(ROOT / "privacy/index.html")
    index = (ROOT / "index.html").read_text()
    sitemap = (ROOT / "sitemap.xml").read_text()

    for label, text in (("terms", terms), ("privacy", privacy)):
        if re.search(r"\[date\]|\[zip\]|\[contact email\]|\[phone\]", text):
            fail(f"{label} still has an unfilled bracket")
        if re.search(r"ryan@", text, re.I):
            fail(f"{label} contains a personal mailbox")
        must_contain(label, text, "Effective November 24, 2026")
        must_contain(label, text, "Searight Holdings, Inc.")
        must_contain(label, text, "201 SW Port St Lucie Blvd #104, Port St. Lucie, FL 34984")
        must_contain(label, text, "info@rhinoroster.com")
        must_contain(label, text, "(772) 240-1417")
        must_contain(label, text, "Florida law governs these terms." if label == "terms" else "Care details are not sent to QuickBooks.")

    must_contain("terms", terms, 'It is provided "as is", without warranties of any kind, to the extent the law allows.')
    must_contain("privacy", privacy, "QuickBooks access tokens are stored encrypted.")
    must_contain("privacy", privacy, "When an administrator disconnects QuickBooks, we delete the stored access tokens and stop reading QuickBooks data.")

    if 'href="/terms/"' not in index or 'href="/privacy/"' not in index:
        fail("homepage footer is missing Terms or Privacy links")
    if "https://rhinoroster.com/terms/" not in sitemap or "https://rhinoroster.com/privacy/" not in sitemap:
        fail("sitemap is missing the legal page URLs")

    if FAILURES:
        print("FAIL")
        for item in FAILURES:
            print("-", item)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
