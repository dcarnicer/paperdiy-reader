#!/usr/bin/env python3
"""Convert a CBZ/ZIP or PDF comic into a page-per-image EPUB.

The PaperDIY firmware does not open CBZ/CBR directly. This builds an EPUB where
every image is its own spine document, which the reader can paginate with the
normal A/B page turns.

Examples:
    python3 scripts/comic_to_epub.py comic.cbz comic.epub
    python3 scripts/comic_to_epub.py tome.pdf tome.epub --title "Seitokai 01-14"
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def natural_key(path: str) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path)]


def pdf_pages(pdf: Path, work: Path, scale: int) -> list[Path]:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise SystemExit("pdftoppm not found; install poppler (brew install poppler)")
    prefix = work / "page"
    subprocess.run(
        [pdftoppm, "-jpeg", "-jpegopt", "quality=85", "-scale-to", str(scale), str(pdf), str(prefix)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pages = sorted(
        (p for p in work.glob("page-*") if p.suffix.lower() in IMAGE_EXTENSIONS),
        key=lambda p: natural_key(p.name),
    )
    if not pages:
        raise SystemExit(f"pdftoppm produced no pages for {pdf}")
    return pages


def cbz_pages(cbz: Path, work: Path) -> list[tuple[str, bytes]]:
    pages: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(cbz) as archive:
        names = [
            info.filename
            for info in archive.infolist()
            if not info.is_dir() and Path(info.filename).suffix.lower() in IMAGE_EXTENSIONS
        ]
        for name in sorted(names, key=natural_key):
            pages.append((Path(name).suffix.lower(), archive.read(name)))
    if not pages:
        raise SystemExit(f"no images found in {cbz}")
    return pages


def page_document(number: int, image_name: str, title: str) -> str:
    return f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{html.escape(title)} - page {number}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body><div><img src="images/{html.escape(image_name)}" alt="page {number}"/></div></body>
</html>
"""


def build_epub(
    output: Path,
    pages: list[tuple[str, bytes]],
    title: str,
    author: str,
) -> None:
    manifest: list[str] = []
    spine: list[str] = []
    navpoints: list[str] = []
    page_names: list[str] = []

    for index, (extension, _) in enumerate(pages, start=1):
        page_name = f"page_{index:04d}.xhtml"
        image_name = f"page_{index:04d}{extension}"
        page_names.append(page_name)
        manifest.append(
            f'<item id="page{index}" href="{page_name}" media-type="application/xhtml+xml"/>'
        )
        manifest.append(
            f'<item id="image{index}" href="images/{image_name}" media-type="image/{extension.lstrip(".")}"/>'
        )
        spine.append(f'<itemref idref="page{index}"/>')
        navpoints.append(
            f'<navPoint id="nav{index}" playOrder="{index}">'
            f'<navLabel><text>Page {index}</text></navLabel>'
            f'<content src="{page_name}"/></navPoint>'
        )

    content_opf = f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{html.escape(title)}</dc:title>
    <dc:creator>{html.escape(author)}</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="bookid">comic-{abs(hash((title, len(pages))))}</dc:identifier>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
    {chr(10).join("    " + item for item in manifest)}
  </manifest>
  <spine toc="ncx">
    {chr(10).join("    " + item for item in spine)}
  </spine>
</package>
"""

    toc_ncx = f"""<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="comic"/></head>
  <docTitle><text>{html.escape(title)}</text></docTitle>
  <navMap>
    {chr(10).join("    " + item for item in navpoints)}
  </navMap>
</ncx>
"""

    container = """<?xml version='1.0' encoding='utf-8'?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    css = "body{margin:0;padding:0;text-align:center}img{max-width:100%;max-height:100%}\n"

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as epub:
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        epub.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        epub.writestr("OEBPS/content.opf", content_opf, compress_type=zipfile.ZIP_DEFLATED)
        epub.writestr("OEBPS/toc.ncx", toc_ncx, compress_type=zipfile.ZIP_DEFLATED)
        epub.writestr("OEBPS/style.css", css, compress_type=zipfile.ZIP_DEFLATED)
        for index, (extension, data) in enumerate(pages, start=1):
            epub.writestr(f"OEBPS/page_{index:04d}.xhtml", page_document(index, f"page_{index:04d}{extension}", title),
                          compress_type=zipfile.ZIP_DEFLATED)
            epub.writestr(f"OEBPS/images/page_{index:04d}{extension}", data,
                          compress_type=zipfile.ZIP_DEFLATED)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert CBZ/ZIP/PDF comics to page-per-image EPUB")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", default=None)
    parser.add_argument("--author", default="Unknown")
    parser.add_argument("--scale", type=int, default=960, help="max PDF page dimension (default: 960)")
    args = parser.parse_args()

    source = args.input
    if not source.exists():
        raise SystemExit(f"input not found: {source}")
    title = args.title or source.stem
    suffix = source.suffix.lower()

    with tempfile.TemporaryDirectory(prefix="comic2epub-") as temp:
        if suffix == ".pdf":
            rendered = pdf_pages(source, Path(temp), args.scale)
            pages = [(path.suffix.lower(), path.read_bytes()) for path in rendered]
        elif suffix in (".cbz", ".zip"):
            pages = cbz_pages(source, Path(temp))
        else:
            raise SystemExit("input must be .pdf, .cbz or .zip")

    build_epub(args.output, pages, title, args.author)
    print(f"wrote {args.output} ({len(pages)} pages, {args.output.stat().st_size / (1024 * 1024):.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
