#!/usr/bin/env python3
"""Rasterize a PowerPoint presentation into per-slide PNGs.

Runs ``soffice --headless --convert-to pdf`` followed by ``pdftoppm`` to
produce one PNG per slide. Useful when you want to feed slide images to
a vision model without running full text extraction.

Usage:
    python3 rasterize_slides.py deck.pptx --out-dir /tmp/slides
    python3 rasterize_slides.py deck.pptx --out-dir /tmp/slides --dpi 300
    python3 rasterize_slides.py deck.pptx --out-dir /tmp/slides --pages 3-7
    python3 rasterize_slides.py deck.pptx --out-dir /tmp/slides --format jpeg
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _require_binary(name: str, hint: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"'{name}' not installed. {hint}")


def _parse_pages(spec: str | None) -> tuple[int | None, int | None]:
    """Parse '--pages 3-7' / '--pages 5' into (first, last). None means all."""
    if not spec:
        return (None, None)
    spec = spec.strip()
    if "-" in spec:
        first, last = spec.split("-", 1)
        return (int(first), int(last))
    page = int(spec)
    return (page, page)


def pptx_to_pdf(pptx_path: Path, out_dir: Path) -> Path:
    _require_binary(
        "soffice",
        "Install libreoffice or libreoffice-impress.",
    )
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(out_dir), str(pptx_path)],
        check=True, capture_output=True,
    )
    pdf_path = out_dir / (pptx_path.stem + ".pdf")
    if not pdf_path.exists():
        raise RuntimeError(
            f"LibreOffice produced no PDF for {pptx_path}. "
            "Try opening the file manually to rule out corruption."
        )
    return pdf_path


def pdf_to_pngs(
    pdf_path: Path,
    out_dir: Path,
    dpi: int,
    first: int | None,
    last: int | None,
    image_format: str,
) -> list[Path]:
    _require_binary("pdftoppm", "Install poppler-utils.")
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / pdf_path.stem

    cmd = ["pdftoppm", f"-{image_format}", "-r", str(dpi)]
    if first is not None:
        cmd += ["-f", str(first)]
    if last is not None:
        cmd += ["-l", str(last)]
    cmd += [str(pdf_path), str(prefix)]

    subprocess.run(cmd, check=True, capture_output=True)

    suffix = ".jpg" if image_format == "jpeg" else f".{image_format}"
    return sorted(out_dir.glob(f"{pdf_path.stem}-*{suffix}"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n\n")[0]
    )
    parser.add_argument("path", help="Path to the .pptx file")
    parser.add_argument("--out-dir", required=True,
                        help="Directory to write PNGs into "
                             "(created if absent)")
    parser.add_argument("--dpi", type=int, default=150,
                        help="DPI for rasterization (default: 150; "
                             "300 for dense content; 100 for speed)")
    parser.add_argument("--pages",
                        help="Page range like '3-7' or a single page '5' "
                             "(default: all slides)")
    parser.add_argument("--format", choices=("png", "jpeg", "tiff"),
                        default="png",
                        help="Output image format (default: png)")
    args = parser.parse_args()

    pptx_path = Path(args.path)
    if not pptx_path.exists():
        _log(f"error: file not found: {pptx_path}")
        return 1

    out_dir = Path(args.out_dir)

    try:
        first, last = _parse_pages(args.pages)
    except ValueError:
        _log(f"error: invalid --pages spec: {args.pages!r}")
        return 1

    try:
        with tempfile.TemporaryDirectory(prefix="pptx_pdf_") as tmp:
            pdf_path = pptx_to_pdf(pptx_path, Path(tmp))
            _log(f"converted to PDF: {pdf_path}")
            pngs = pdf_to_pngs(
                pdf_path, out_dir, args.dpi, first, last, args.format,
            )
    except Exception as exc:  # noqa: BLE001
        _log(f"error: {exc}")
        return 1

    _log(f"wrote {len(pngs)} file(s) to {out_dir}")
    for p in pngs:
        sys.stdout.write(str(p))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
