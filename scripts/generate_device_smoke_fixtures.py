#!/usr/bin/env python3
"""Generate deterministic fixtures for the PaperDIY device regression.

Outputs (under build/device-regression/fixtures by default):
  paperdiy-smoke.epub
  dictionaries/smoke/smoke.ifo
  dictionaries/smoke/smoke.idx
  dictionaries/smoke/smoke.dict

The EPUB is intentionally small but long enough to span two pages. It has a
link to chapter two, a footnote and known words for the test dictionary. The
dictionary is plain StarDict (uncompressed .idx and .dict).
"""

from __future__ import annotations

import argparse
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "build" / "device-regression" / "fixtures"

CHAPTER_ONE = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Chapter One</title></head>
<body>
<h1>Chapter One</h1>
<p>alpha beta gamma. SMOKE PAGE ONE. This paragraph has a <a href="chapter2.xhtml">link to chapter two</a> and a footnote <a href="#fn1" epub:type="noteref">[1]</a>.</p>
<p>The smoke reader opens this page and checks that the first marker is visible. The next paragraphs add enough text to force a second page at the default font size.</p>
<p>Filler paragraph one. The reader should render this text without missing glyphs, clipped lines or layout errors. A quick brown fox jumps over the lazy dog while the page is being prepared.</p>
<p>Filler paragraph two. E-ink refresh behaviour is not judged from the framebuffer, but the text layout and page boundaries are deterministic and can be checked.</p>
<p>Filler paragraph three. Alpha, beta and gamma are also dictionary headwords, so a lookup on this page can return a stable definition.</p>
<p>SMOKE PAGE TWO. This marker must appear after one page turn. It confirms that pagination advanced and that the reader did not stop at the end of Chapter One.</p>
<p>Filler paragraph four. The remaining text keeps the page height stable and gives the link and footnote selectors enough content to work with.</p>
<aside epub:type="footnote" id="fn1"><p>SMOKE FOOTNOTE. Footnote text is reachable from the link selector.</p></aside>
</body></html>
"""

CHAPTER_TWO = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Chapter Two</title></head>
<body>
<h1>Chapter Two</h1>
<p>SMOKE CHAPTER TWO. The link and table-of-contents target arrived correctly.</p>
<p>This page is deliberately short so it is easy to recognise after a TOC jump or a link follow.</p>
</body></html>
"""

NAV = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Contents</title></head>
<body>
<nav epub:type="toc" id="toc">
<ol>
<li><a href="chapter1.xhtml">Chapter One</a></li>
<li><a href="chapter2.xhtml">Chapter Two</a></li>
</ol>
</nav>
</body></html>
"""

CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""

CONTENT_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>PaperDIY Smoke Test</dc:title>
<dc:creator>PaperDIY</dc:creator>
<dc:identifier id="bookid">paperdiy-smoke-001</dc:identifier>
<dc:language>en</dc:language>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
<item id="c1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
<item id="c2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
</manifest>
<spine><itemref idref="c1"/><itemref idref="c2"/></spine>
</package>
"""


def write_epub(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", CONTAINER)
        archive.writestr("OEBPS/content.opf", CONTENT_OPF)
        archive.writestr("OEBPS/nav.xhtml", NAV)
        archive.writestr("OEBPS/chapter1.xhtml", CHAPTER_ONE)
        archive.writestr("OEBPS/chapter2.xhtml", CHAPTER_TWO)


# Headwords are sorted case-insensitively, as the reader's index does.
DICT_ENTRIES = {
    "alpha": "SMOKEDEF alpha: the first test letter.",
    "arrived": "SMOKEDEF arrived: reached the destination.",
    "beta": "SMOKEDEF beta: the second test letter.",
    "Chapter": "SMOKEDEF chapter: a book division.",
    "correctly": "SMOKEDEF correctly: in the right way.",
    "gamma": "SMOKEDEF gamma: the third test letter.",
    "One": "SMOKEDEF one: the first number.",
    "SMOKE": "SMOKEDEF smoke: the test marker.",
    "target": "SMOKEDEF target: the destination.",
    "Two": "SMOKEDEF two: the second number.",
}


def write_dictionary(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    words = sorted(DICT_ENTRIES, key=lambda word: (word.lower(), word))
    dict_bytes = bytearray()
    idx_bytes = bytearray()
    for word in words:
        definition = DICT_ENTRIES[word].encode("utf-8")
        offset = len(dict_bytes)
        dict_bytes.extend(definition)
        idx_bytes.extend(word.encode("utf-8"))
        idx_bytes.append(0)
        idx_bytes.extend(struct.pack(">II", offset, len(definition)))
    (path / "smoke.dict").write_bytes(dict_bytes)
    (path / "smoke.idx").write_bytes(idx_bytes)
    ifo = (
        "StarDict's dict ifo file\n"
        "version=2.4.2\n"
        f"wordcount={len(words)}\n"
        f"idxfilesize={len(idx_bytes)}\n"
        "bookname=PaperDIY Smoke Dictionary\n"
        "sametypesequence=m\n"
    )
    (path / "smoke.ifo").write_text(ifo, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PaperDIY device regression fixtures")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    write_epub(args.output / "paperdiy-smoke.epub")
    write_dictionary(args.output / "dictionaries" / "smoke")
    print(f"fixtures: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
