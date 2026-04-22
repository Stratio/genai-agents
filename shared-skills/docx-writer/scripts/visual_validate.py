#!/usr/bin/env python3
"""Render a .docx to per-page PNGs for visual inspection.

Pipeline: ``soffice --convert-to pdf`` → ``pdftoppm -png -r <dpi>``. Writes
one PNG per page into the output directory and prints their paths to stdout.

Agents can use the resulting PNGs multimodally to verify layout before
handing the document to the user and to decide whether to iterate on the
aesthetic direction.

Usage:
    python3 visual_validate.py document.docx --out /tmp/preview
    python3 visual_validate.py document.docx --out /tmp/preview --dpi 200
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def render_preview(
    docx_path: str | Path,
    out_dir: str | Path,
    dpi: int = 150,
) -> list[Path]:
    src = Path(docx_path)
    dst = Path(out_dir)
    if not src.exists():
        raise FileNotFoundError(src)
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "LibreOffice headless (soffice) not found on PATH. "
            "Install libreoffice or libreoffice-writer."
        )
    if shutil.which("pdftoppm") is None:
        raise RuntimeError(
            "pdftoppm not found on PATH. Install poppler-utils."
        )

    dst.mkdir(parents=True, exist_ok=True)

    # 1) DOCX -> PDF via LibreOffice
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(dst), str(src)],
        check=True, capture_output=True,
    )
    pdf = dst / (src.stem + ".pdf")
    if not pdf.exists():
        raise RuntimeError(f"LibreOffice produced no PDF for {src}")

    # 2) PDF -> PNG per page
    prefix = dst / src.stem
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(prefix)],
        check=True, capture_output=True,
    )

    pages = sorted(dst.glob(f"{src.stem}-*.png"))
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").strip())
    parser.add_argument("docx", help="Path to the .docx file.")
    parser.add_argument("--out", required=True, help="Output directory for PNGs.")
    parser.add_argument("--dpi", type=int, default=150,
                        help="Rasterisation DPI (default 150).")
    args = parser.parse_args()

    try:
        pages = render_preview(args.docx, args.out, dpi=args.dpi)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for p in pages:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
