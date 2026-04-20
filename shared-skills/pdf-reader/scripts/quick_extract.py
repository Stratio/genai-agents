#!/usr/bin/env python3
"""
quick_extract.py — One-shot PDF text extraction with graceful fallback.

Use this when you want structured Markdown from a PDF without thinking
about which library to use or whether it's installed. The script tries
several extractors in order and returns the first successful result.

USAGE
    python quick_extract.py <path/to/file.pdf>
    python quick_extract.py <path/to/file.pdf> --pages 1-5
    python quick_extract.py <path/to/file.pdf> --no-tables
    cat file.pdf | python quick_extract.py -

OUTPUT
    stdout — Markdown-structured text (metadata + pages + tables)
    stderr — diagnostic messages (which tool ran, warnings, errors)
    exit 0 — success
    exit 1 — all extractors failed or input error

EXTRACTOR PRIORITY
    1. pdfplumber   — best layout + table extraction
    2. pdfminer.six — pure Python, handles odd encodings
    3. pypdf        — lightweight, last-resort text dump
    4. pdftotext    — system CLI (poppler-utils)

This is the "quick mode" of the pdf-reader skill. For complex documents
(scans, broken fonts, mixed content), use the manual workflow described
in SKILL.md instead.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


# ============================================================================
# CLI parsing
# ============================================================================

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="quick_extract.py",
        description="Extract PDF text as structured Markdown.",
    )
    p.add_argument("pdf", help="Path to PDF file, or '-' for stdin")
    p.add_argument(
        "--pages",
        help="Page range to extract, e.g. '1-5' or '3' (default: all pages)",
        default=None,
    )
    p.add_argument(
        "--no-tables",
        action="store_true",
        help="Skip table extraction (faster, less noisy for text-only docs)",
    )
    p.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip document metadata block in output",
    )
    p.add_argument(
        "--tool",
        choices=["pdfplumber", "pdfminer", "pypdf", "pdftotext"],
        help="Force a specific extractor (otherwise auto-detect)",
    )
    p.add_argument(
        "--auto-install",
        action="store_true",
        help="If no Python extractor is available, pip-install pdfminer.six",
    )
    return p.parse_args()


def parse_page_range(spec: str | None) -> tuple[int, int] | None:
    """Parse '1-5' or '3' into (start, end) 1-indexed inclusive. None = all."""
    if not spec:
        return None
    m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+)\s*)?", spec)
    if not m:
        raise ValueError(f"Invalid page range: {spec!r} (expected '1-5' or '3')")
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    if start < 1 or end < start:
        raise ValueError(f"Invalid page range: {spec!r}")
    return start, end


# ============================================================================
# Text utilities
# ============================================================================

def log(msg: str) -> None:
    """Write to stderr — never pollutes the Markdown output on stdout."""
    print(msg, file=sys.stderr, flush=True)


def normalize_text(text: str) -> str:
    """Normalize line endings and collapse excessive blank lines."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)          # trailing whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)           # max one blank line
    return text.strip()


def promote_headings(text: str) -> str:
    """
    Promote likely heading lines to Markdown '### ' headings.

    Heuristic: a line is a heading when it is standalone (surrounded by
    blank lines or doc boundaries), short (<= 80 chars), doesn't end in
    sentence punctuation, and looks like a title (Title Case or ALL CAPS
    with at least one letter).

    Known limitation: promotes false positives on short prose lines like
    'Yours Sincerely' or 'Table of Contents'. Heuristic, not semantic.
    """
    lines = text.split("\n")
    out: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            out.append(line)
            continue

        prev_blank = i == 0 or not lines[i - 1].strip()
        next_blank = i == len(lines) - 1 or not lines[i + 1].strip()
        last_char = stripped[-1]

        has_letter = any(c.isalpha() for c in stripped)
        looks_like_heading = (
            prev_blank
            and next_blank
            and len(stripped) <= 80
            and last_char not in ".,:;"
            and has_letter
            and (stripped.istitle() or stripped.isupper())
            and not stripped.startswith("#")
        )
        out.append(f"### {stripped}" if looks_like_heading else line)
    return "\n".join(out)


def table_to_markdown(table: list[list]) -> str:
    """Convert a 2D list (pdfplumber table) into a Markdown table."""
    if not table or not any(table):
        return ""

    # Normalize cells: None -> "", collapse internal whitespace
    def cell(v) -> str:
        if v is None:
            return ""
        s = str(v).replace("\n", " ")
        return re.sub(r"\s+", " ", s).strip()

    rows = [[cell(c) for c in row] for row in table if any(c is not None for c in row)]
    if not rows:
        return ""

    # Pad short rows to match widest row
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]

    header, *body = rows if len(rows) > 1 else (rows[0], [])
    col_widths = [max(3, max(len(r[i]) for r in rows)) for i in range(width)]

    def fmt(row):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(row, col_widths)) + " |"

    sep = "| " + " | ".join("-" * w for w in col_widths) + " |"
    lines = [fmt(header), sep] + [fmt(r) for r in body]
    return "\n".join(lines)


# ============================================================================
# Tool detection
# ============================================================================

def detect_available() -> dict[str, bool]:
    available = {"pdfplumber": False, "pdfminer": False, "pypdf": False, "pdftotext": False}

    try:
        import pdfplumber  # noqa: F401
        available["pdfplumber"] = True
    except ImportError:
        pass

    try:
        from pdfminer.high_level import extract_pages  # noqa: F401
        available["pdfminer"] = True
    except ImportError:
        pass

    try:
        import pypdf  # noqa: F401
        available["pypdf"] = True
    except ImportError:
        pass

    try:
        r = subprocess.run(["pdftotext", "-v"], capture_output=True, timeout=5)
        available["pdftotext"] = r.returncode == 0 or b"pdftotext" in (r.stderr or b"")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return available


def try_auto_install() -> bool:
    """Install pdfminer.six — pure Python, minimal footprint."""
    log("Attempting auto-install of pdfminer.six ...")
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "pdfminer.six"],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode == 0:
            log("Installed pdfminer.six.")
            return True
        log(f"Install failed (exit {r.returncode}): {r.stderr.strip()[:200]}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log(f"Install failed: {e}")
    return False


# ============================================================================
# Extractors — each returns (metadata_lines, list of (page_num, markdown))
# ============================================================================

PageMD = tuple[int, str]


def _in_page_range(i: int, pr: tuple[int, int] | None) -> bool:
    return pr is None or (pr[0] <= i <= pr[1])


def extract_with_pdfplumber(path: str, *, pages: tuple[int, int] | None,
                             include_tables: bool) -> tuple[list[str], list[PageMD]]:
    import pdfplumber

    meta_lines: list[str] = []
    pages_out: list[PageMD] = []

    with pdfplumber.open(path) as pdf:
        meta = pdf.metadata or {}
        for key, label in [("Title", "Title"), ("Author", "Author"),
                           ("Subject", "Subject"), ("CreationDate", "Created")]:
            if meta.get(key):
                meta_lines.append(f"- **{label}**: {meta[key]}")
        meta_lines.append(f"- **Pages**: {len(pdf.pages)}")

        for idx, page in enumerate(pdf.pages, start=1):
            if not _in_page_range(idx, pages):
                continue

            parts: list[str] = []

            # Strategy: if tables are requested, extract them and then
            # suppress the text inside their bounding boxes when pulling
            # body text. We do this at the character level (preserves
            # reading order) instead of the word level (can shuffle
            # superscripts/subscripts).
            tables = []
            table_bboxes: list[tuple[float, float, float, float]] = []
            if include_tables:
                tables = page.extract_tables() or []
                if tables:
                    table_bboxes = [t.bbox for t in page.find_tables()]

            if table_bboxes:
                def outside_tables(obj):
                    cx = (obj["x0"] + obj["x1"]) / 2
                    cy = (obj["top"] + obj["bottom"]) / 2
                    for x0, y0, x1, y1 in table_bboxes:
                        if x0 <= cx <= x1 and y0 <= cy <= y1:
                            return False
                    return True
                filtered = page.filter(outside_tables)
                text = filtered.extract_text() or ""
            else:
                text = page.extract_text() or ""

            if text.strip():
                parts.append(promote_headings(normalize_text(text)))

            for t in tables:
                md = table_to_markdown(t)
                if md:
                    parts.append(md)

            if parts:
                pages_out.append((idx, "\n\n".join(parts)))

    return meta_lines, pages_out


def extract_with_pdfminer(path: str, *, pages: tuple[int, int] | None,
                           include_tables: bool) -> tuple[list[str], list[PageMD]]:
    # include_tables ignored — pdfminer doesn't do table detection
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument

    meta_lines: list[str] = []
    try:
        with open(path, "rb") as f:
            parser = PDFParser(f)
            doc = PDFDocument(parser)
            info = doc.info[0] if doc.info else {}
            for key, label in [("Title", "Title"), ("Author", "Author"),
                               ("Subject", "Subject"), ("CreationDate", "Created")]:
                val = info.get(key)
                if val:
                    decoded = val.decode("utf-8", "replace") if isinstance(val, bytes) else str(val)
                    meta_lines.append(f"- **{label}**: {decoded}")
    except Exception as e:
        log(f"pdfminer: metadata read failed ({e}); continuing without metadata")

    # Page count
    try:
        with open(path, "rb") as f:
            total = sum(1 for _ in PDFPage.get_pages(f))
        meta_lines.append(f"- **Pages**: {total}")
    except Exception:
        pass

    pages_out: list[PageMD] = []
    for idx, layout in enumerate(extract_pages(path), start=1):
        if not _in_page_range(idx, pages):
            continue
        chunks = [el.get_text() for el in layout if isinstance(el, LTTextContainer)]
        body = "".join(chunks)
        if body.strip():
            pages_out.append((idx, promote_headings(normalize_text(body))))

    return meta_lines, pages_out


def extract_with_pypdf(path: str, *, pages: tuple[int, int] | None,
                        include_tables: bool) -> tuple[list[str], list[PageMD]]:
    # include_tables ignored — pypdf doesn't do table detection
    import pypdf

    meta_lines: list[str] = []
    pages_out: list[PageMD] = []

    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        if reader.is_encrypted:
            try:
                reader.decrypt("")  # try empty password
            except Exception:
                log("pypdf: PDF is encrypted and no password provided")

        meta = reader.metadata or {}
        for key, label in [("/Title", "Title"), ("/Author", "Author"),
                           ("/Subject", "Subject"), ("/CreationDate", "Created")]:
            if meta.get(key):
                meta_lines.append(f"- **{label}**: {meta[key]}")
        meta_lines.append(f"- **Pages**: {len(reader.pages)}")

        for idx, page in enumerate(reader.pages, start=1):
            if not _in_page_range(idx, pages):
                continue
            text = page.extract_text() or ""
            if text.strip():
                pages_out.append((idx, promote_headings(normalize_text(text))))

    return meta_lines, pages_out


def extract_with_pdftotext(path: str, *, pages: tuple[int, int] | None,
                            include_tables: bool) -> tuple[list[str], list[PageMD]]:
    cmd = ["pdftotext", "-layout", "-enc", "UTF-8"]
    if pages:
        cmd += ["-f", str(pages[0]), "-l", str(pages[1])]
    cmd += [path, "-"]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"pdftotext exited {r.returncode}: {r.stderr.strip()[:200]}")
    if not r.stdout.strip():
        raise RuntimeError("pdftotext produced no output")

    meta_lines: list[str] = []
    # Get metadata via pdfinfo (best-effort)
    try:
        info = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=10)
        if info.returncode == 0:
            for line in info.stdout.splitlines():
                if line.startswith(("Title:", "Author:", "Subject:", "CreationDate:", "Pages:")):
                    key, _, val = line.partition(":")
                    val = val.strip()
                    if val:
                        meta_lines.append(f"- **{key.strip()}**: {val}")
    except Exception:
        pass

    pages_out: list[PageMD] = []
    # pdftotext emits \f as page separator
    raw_pages = r.stdout.split("\f")
    start_idx = pages[0] if pages else 1
    for offset, raw in enumerate(raw_pages):
        idx = start_idx + offset
        cleaned = normalize_text(raw)
        if cleaned:
            pages_out.append((idx, promote_headings(cleaned)))

    return meta_lines, pages_out


EXTRACTORS: dict[str, Callable] = {
    "pdfplumber": extract_with_pdfplumber,
    "pdfminer":   extract_with_pdfminer,
    "pypdf":      extract_with_pypdf,
    "pdftotext":  extract_with_pdftotext,
}

TOOL_ORDER = ["pdfplumber", "pdfminer", "pypdf", "pdftotext"]

INSTALL_HINTS = {
    "pdfplumber": "pip install pdfplumber",
    "pdfminer":   "pip install pdfminer.six",
    "pypdf":      "pip install pypdf",
    "pdftotext":  "apt install poppler-utils  # or: brew install poppler",
}


# ============================================================================
# Main
# ============================================================================

def resolve_input_path(arg: str) -> tuple[str, str | None]:
    """Return (usable_path, tmp_path_to_cleanup_or_None)."""
    if arg == "-":
        data = sys.stdin.buffer.read()
        if not data:
            raise ValueError("empty input on stdin")
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.write(data)
        tmp.close()
        return tmp.name, tmp.name

    path = os.path.expanduser(arg)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"file not found: {path}")
    return path, None


def assemble_output(meta_lines: list[str], pages: list[PageMD],
                    include_metadata: bool) -> str:
    blocks: list[str] = []
    if include_metadata and meta_lines:
        blocks.append("## Document Metadata\n\n" + "\n".join(meta_lines))
    for page_num, body in pages:
        blocks.append(f"## Page {page_num}\n\n{body}")
    return "\n\n---\n\n".join(blocks)


def main() -> int:
    try:
        args = parse_args()
        page_range = parse_page_range(args.pages)
    except (SystemExit, ValueError) as e:
        if isinstance(e, ValueError):
            log(f"Error: {e}")
        return 1

    try:
        pdf_path, tmp_path = resolve_input_path(args.pdf)
    except (FileNotFoundError, ValueError) as e:
        log(f"Error: {e}")
        return 1

    try:
        available = detect_available()
        log("Available: " + ", ".join(
            f"{k}={'yes' if v else 'no'}" for k, v in available.items()
        ))

        # If nothing Python-side is available and auto-install opted in, try it
        if args.auto_install and not any(available[t] for t in ("pdfplumber", "pdfminer", "pypdf")):
            if try_auto_install():
                available = detect_available()

        order = [args.tool] if args.tool else TOOL_ORDER
        last_error: Exception | None = None

        for tool in order:
            if not available.get(tool):
                if args.tool:
                    log(f"Error: requested tool {tool!r} is not available. "
                        f"Install with: {INSTALL_HINTS[tool]}")
                    return 1
                continue

            log(f"Extracting with: {tool}")
            try:
                meta, pages = EXTRACTORS[tool](
                    pdf_path,
                    pages=page_range,
                    include_tables=not args.no_tables,
                )
                output = assemble_output(meta, pages, include_metadata=not args.no_metadata)
                if output.strip():
                    print(output)
                    return 0
                log(f"{tool}: produced empty output")
            except Exception as e:
                last_error = e
                log(f"{tool}: failed — {type(e).__name__}: {e}")

        log("")
        log("No extractor succeeded. Install one of the following and retry:")
        for t in TOOL_ORDER:
            if not available.get(t):
                log(f"  {t:12s}  {INSTALL_HINTS[t]}")
        if last_error:
            log(f"\nLast error: {type(last_error).__name__}: {last_error}")
        return 1

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


if __name__ == "__main__":
    sys.exit(main())
