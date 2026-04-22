#!/usr/bin/env python3
"""CLI wrapper to convert legacy binary ``.doc`` to ``.docx`` via LibreOffice.

Usage:
    python3 convert_doc_to_docx.py input.doc --out-dir /tmp/
"""
from __future__ import annotations

import argparse
import sys

from structural_ops import convert_doc_to_docx  # type: ignore[import-not-found]


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").strip())
    parser.add_argument("input", help="Path to the .doc file.")
    parser.add_argument("--out-dir", default=None,
                        help="Output directory (default: new temp dir).")
    args = parser.parse_args()

    try:
        out = convert_doc_to_docx(args.input, output_dir=args.out_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
