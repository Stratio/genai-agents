#!/usr/bin/env python3
"""Convert a Markdown file to PDF, and optionally HTML and DOCX.

Usage:
    python tools/md_to_report.py <input.md> [--output-dir DIR] [--style STYLE]
           [--author AUTHOR] [--no-embed-images] [--cover] [--domain DOMAIN]
           [--title TITLE] [--html] [--docx]

Arguments:
    input.md            Path to the source markdown file.
    --output-dir        Directory for generated files (default: same as input).
    --style             CSS preset from styles/ folder: corporate, academic, modern
                        (default: corporate). Can also be a path to a custom CSS file.
    --author            Author name for PDF metadata and cover page.
    --no-embed-images   Skip embedding local images as base64 in the PDF.
    --cover             Generate a cover page with title, author, date, and domain.
    --domain            Domain name shown on the cover page.
    --title             Override title (default: extracted from first H1 in markdown).
    --html              Also save the intermediate HTML file alongside PDF.
    --docx              Also generate a DOCX file alongside PDF.

Outputs:
    <name>.pdf      PDF generated from the HTML via weasyprint.
    <name>.html     Standalone HTML file (only when --html is passed).
    <name>.docx     DOCX file (only when --docx is passed).
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import markdown

from css_builder import build_css
from image_utils import embed_images_in_html

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_STYLE = "corporate"

EXTRA_MD_EXTENSIONS = [
    "extra",       # tables, fenced_code, footnotes, etc.
    "codehilite",  # syntax highlighting
    "toc",         # table of contents via [TOC]
    "sane_lists",  # better list handling
]


def _extract_h1(md_content: str) -> str | None:
    """Extract the first H1 heading from markdown content."""
    match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def resolve_css(style: str) -> str:
    """Resolve a style name or path to CSS content."""
    css_content, _ = build_css(style, "pdf")
    return css_content


def _build_cover_html(title: str, author: str | None = None,
                      domain: str | None = None) -> str:
    """Build HTML for a cover page."""
    meta_lines = []
    if author:
        meta_lines.append(f"<strong>Autor:</strong> {author}")
    if domain:
        meta_lines.append(f"<strong>Dominio:</strong> {domain}")
    meta_lines.append(f"<strong>Fecha:</strong> {date.today().strftime('%d/%m/%Y')}")

    meta_html = "<br>".join(meta_lines)

    return f"""<div class="cover-page">
    <div class="cover-title">{title}</div>
    <div class="cover-meta">{meta_html}</div>
</div>
"""


def md_to_html(md_content: str, css: str, title: str = "Report",
               author: str | None = None, cover: bool = False,
               domain: str | None = None) -> str:
    """Convert markdown content to a standalone HTML document."""
    body = markdown.markdown(md_content, extensions=EXTRA_MD_EXTENSIONS)

    meta_tags = f'    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
    if author:
        meta_tags += f'\n    <meta name="author" content="{author}">'

    cover_html = ""
    if cover:
        cover_html = _build_cover_html(title, author, domain)

    running_header = f'<div class="running-header">{title}</div>\n' if not cover else f'<div class="running-header">{title}</div>\n<div class="running-title">{title}</div>\n'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
{meta_tags}
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
{running_header}{cover_html}{body}
</body>
</html>"""


def convert(input_path: Path, output_dir: Path, style: str,
            author: str | None = None, embed_images: bool = True,
            cover: bool = False, domain: str | None = None,
            title: str | None = None,
            generate_docx: bool = False,
            also_save_html: bool = False) -> tuple[Path | None, Path, Path | None]:
    """Convert a markdown file to PDF, and optionally HTML and DOCX.

    Returns (html_path_or_None, pdf_path, docx_path_or_None).
    """
    md_content = input_path.read_text(encoding="utf-8")
    css = resolve_css(style)
    if title is None:
        title = _extract_h1(md_content) or input_path.stem.replace("_", " ").replace("-", " ").title()

    html_content = md_to_html(md_content, css, title, author=author,
                              cover=cover, domain=domain)

    if embed_images:
        html_content = embed_images_in_html(html_content, base_dir=PROJECT_ROOT)

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem

    html_path = None
    if also_save_html:
        html_path = output_dir / f"{stem}.html"
        html_path.write_text(html_content, encoding="utf-8")

    pdf_path = output_dir / f"{stem}.pdf"
    from weasyprint import HTML
    html_doc = HTML(string=html_content, base_url=str(PROJECT_ROOT))
    html_doc.write_pdf(str(pdf_path), presentational_hints=True)

    docx_path = None
    if generate_docx:
        from docx_generator import DOCXGenerator
        docx_gen = DOCXGenerator(style=style, author=author)
        docx_gen.render_from_markdown(
            md_content, title=title, domain=domain,
            author=author, show_cover=cover,
        )
        docx_path = output_dir / f"{stem}.docx"
        docx_gen.save(docx_path)

    return html_path, pdf_path, docx_path


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML and PDF")
    parser.add_argument("input", type=Path, help="Source markdown file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: same as input file)",
    )
    parser.add_argument(
        "--style",
        default=DEFAULT_STYLE,
        help=f"CSS style preset or file path (default: {DEFAULT_STYLE})",
    )
    parser.add_argument(
        "--author",
        default=None,
        help="Author name for PDF metadata and cover page",
    )
    parser.add_argument(
        "--no-embed-images",
        action="store_true",
        help="Skip embedding local images as base64",
    )
    parser.add_argument(
        "--cover",
        action="store_true",
        help="Generate a cover page",
    )
    parser.add_argument(
        "--domain",
        default=None,
        help="Domain name shown on the cover page",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Override title (default: extracted from first H1 in markdown)",
    )
    parser.add_argument(
        "--docx",
        action="store_true",
        help="Also generate a DOCX file alongside PDF",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Also save the intermediate HTML file alongside PDF",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output_dir or args.input.parent

    html_path, pdf_path, docx_path = convert(
        args.input, output_dir, args.style,
        author=args.author,
        embed_images=not args.no_embed_images,
        cover=args.cover,
        domain=args.domain,
        title=args.title,
        generate_docx=args.docx,
        also_save_html=args.html,
    )
    if html_path:
        print(f"HTML: {html_path}")
    print(f"PDF:  {pdf_path}")
    if docx_path:
        print(f"DOCX: {docx_path}")


if __name__ == "__main__":
    main()
