#!/usr/bin/env python3
"""Convert a Markdown file to PDF, and optionally HTML and DOCX.

Usage (run from the agent root):
    python3 skills/analyze/report/tools/md_to_report.py <input.md> [--output-dir DIR] [--style STYLE]
           [--author AUTHOR] [--no-embed-images] [--cover] [--domain DOMAIN]
           [--title TITLE] [--html] [--docx]

Arguments:
    input.md            Path to the source markdown file.
    --output-dir        Directory for generated files (default: same as input).
    --style             CSS preset name: corporate, academic, modern
                        (default: corporate). Can also be a path to a custom CSS file.
                        Presets are resolved from the sibling `../styles/tokens/` folder.
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

from css_builder import build_css, aesthetic_to_override_tokens
from i18n import get_labels
from image_utils import embed_images_in_html

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_STYLE = "corporate"

EXTRA_MD_EXTENSIONS = [
    "extra",       # tables, fenced_code, footnotes, etc.
    "codehilite",  # syntax highlighting
    "toc",         # table of contents via [TOC]
    "sane_lists",  # better list handling
]

# Canonical schema of ``aesthetic.json`` — any other key is rejected.
_AESTHETIC_KEYS = {"tone", "palette_override", "font_pair",
                   "motion_budget", "background_style"}
_MOTION_BUDGETS = {"none", "minimal", "expressive"}
_BACKGROUND_STYLES = {"solid", "gradient-mesh", "noise", "grain"}


def load_aesthetic(path: Path) -> dict:
    """Load and validate an aesthetic.json file.

    Raises ValueError if the file violates the canonical schema. Rejecting
    typos early prevents generators from silently ignoring misspelled values.
    """
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("aesthetic.json must be a JSON object")
    unknown = set(data) - _AESTHETIC_KEYS
    if unknown:
        raise ValueError(
            f"aesthetic.json contains unknown keys: {sorted(unknown)}. "
            f"Allowed keys are: {sorted(_AESTHETIC_KEYS)}."
        )
    if "tone" in data and not isinstance(data["tone"], str):
        raise ValueError("aesthetic.json: 'tone' must be a string")
    if "palette_override" in data and not isinstance(data["palette_override"], dict):
        raise ValueError("aesthetic.json: 'palette_override' must be an object")
    fp = data.get("font_pair")
    if fp is not None:
        if (not isinstance(fp, list) or len(fp) != 2
                or not all(isinstance(x, str) and x for x in fp)):
            raise ValueError("aesthetic.json: 'font_pair' must be a list of "
                             "exactly two non-empty strings [display, body]")
    mb = data.get("motion_budget")
    if mb is not None and mb not in _MOTION_BUDGETS:
        raise ValueError(
            f"aesthetic.json: 'motion_budget' must be one of "
            f"{sorted(_MOTION_BUDGETS)} (got {mb!r})"
        )
    bs = data.get("background_style")
    if bs is not None and bs not in _BACKGROUND_STYLES:
        raise ValueError(
            f"aesthetic.json: 'background_style' must be one of "
            f"{sorted(_BACKGROUND_STYLES)} (got {bs!r})"
        )
    return data


def _extract_h1(md_content: str) -> str | None:
    """Extract the first H1 heading from markdown content."""
    match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def resolve_css(style: str, aesthetic_direction: dict | None = None) -> str:
    """Resolve a style name or path to CSS content, applying an aesthetic."""
    override_tokens = aesthetic_to_override_tokens(aesthetic_direction)
    css_content, _ = build_css(style, "pdf", override_tokens=override_tokens or None)
    return css_content


def _build_cover_html(title: str, author: str | None = None,
                      domain: str | None = None,
                      labels: dict[str, str] | None = None) -> str:
    """Build HTML for a cover page with localised labels."""
    if labels is None:
        labels = get_labels()
    meta_lines = []
    if author:
        meta_lines.append(f"<strong>{labels['cover.author']}:</strong> {author}")
    if domain:
        meta_lines.append(f"<strong>{labels['cover.domain']}:</strong> {domain}")
    meta_lines.append(f"<strong>{labels['cover.date']}:</strong> {date.today().strftime('%d/%m/%Y')}")

    meta_html = "<br>".join(meta_lines)

    return f"""<div class="cover-page">
    <div class="cover-title">{title}</div>
    <div class="cover-meta">{meta_html}</div>
</div>
"""


def md_to_html(md_content: str, css: str, title: str | None = None,
               author: str | None = None, cover: bool = False,
               domain: str | None = None,
               lang: str | None = None,
               labels: dict[str, str] | None = None) -> str:
    """Convert markdown content to a standalone HTML document.

    `lang` selects the language from the i18n catalogue (fallbacks to
    `.agent_lang`, then English). `labels` overrides specific keys.
    Both are used for the cover labels, the HTML `lang` attribute, and the
    default title.
    """
    resolved_labels = get_labels(lang=lang, overrides=labels)
    effective_title = title or resolved_labels["report.default_title"]
    html_lang_attr = resolved_labels["html.lang_attr"]

    body = markdown.markdown(md_content, extensions=EXTRA_MD_EXTENSIONS)

    meta_tags = f'    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
    if author:
        meta_tags += f'\n    <meta name="author" content="{author}">'

    cover_html = ""
    if cover:
        cover_html = _build_cover_html(effective_title, author, domain, labels=resolved_labels)

    running_header = f'<div class="running-header">{effective_title}</div>\n' if not cover else f'<div class="running-header">{effective_title}</div>\n<div class="running-title">{effective_title}</div>\n'

    return f"""<!DOCTYPE html>
<html lang="{html_lang_attr}">
<head>
{meta_tags}
    <title>{effective_title}</title>
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
            also_save_html: bool = False,
            lang: str | None = None,
            labels: dict[str, str] | None = None,
            aesthetic_direction: dict | None = None) -> tuple[Path | None, Path, Path | None]:
    """Convert a markdown file to PDF, and optionally HTML and DOCX.

    `lang` / `labels` flow through to `md_to_html` and to the DOCX generator
    so that cover labels and the HTML `lang` attribute match the user's
    language. See `i18n.get_labels` for resolution rules.

    `aesthetic_direction` applies a deliberate visual direction on top of
    the base style. Schema is documented in `dashboard-aesthetics.md`
    (sibling of this file's parent dir). When present, it flows to
    `resolve_css` and to the DOCX generator so the PDF, HTML and DOCX
    stay visually coherent.

    Returns (html_path_or_None, pdf_path, docx_path_or_None).
    """
    md_content = input_path.read_text(encoding="utf-8")
    css = resolve_css(style, aesthetic_direction=aesthetic_direction)
    if title is None:
        title = _extract_h1(md_content) or input_path.stem.replace("_", " ").replace("-", " ").title()

    html_content = md_to_html(md_content, css, title, author=author,
                              cover=cover, domain=domain,
                              lang=lang, labels=labels)

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
        docx_gen = DOCXGenerator(style=style, author=author,
                                 aesthetic_direction=aesthetic_direction)
        docx_gen.render_from_markdown(
            md_content, title=title, domain=domain,
            author=author, show_cover=cover,
            lang=lang, labels=labels,
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
    parser.add_argument(
        "--lang",
        default=None,
        help="Language code (e.g. en, es). Falls back to .agent_lang file, then 'en'",
    )
    parser.add_argument(
        "--labels-json",
        default=None,
        help='JSON dict of label overrides (e.g. \'{"cover.author":"Autor"}\'). Overrides the --lang catalogue',
    )
    parser.add_argument(
        "--aesthetic",
        type=Path,
        default=None,
        help="Path to an aesthetic.json file with the design-first decision "
             "(keys: tone, palette_override, font_pair, motion_budget, "
             "background_style). Applied to PDF, HTML and DOCX output.",
    )
    args = parser.parse_args()

    aesthetic_direction = None
    if args.aesthetic is not None:
        if not args.aesthetic.is_file():
            print(f"ERROR: aesthetic file not found: {args.aesthetic}", file=sys.stderr)
            sys.exit(1)
        try:
            aesthetic_direction = load_aesthetic(args.aesthetic)
        except (ValueError, OSError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    labels_override = None
    if args.labels_json:
        import json
        try:
            labels_override = json.loads(args.labels_json)
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid --labels-json: {e}", file=sys.stderr)
            sys.exit(1)

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
        lang=args.lang,
        labels=labels_override,
        aesthetic_direction=aesthetic_direction,
    )
    if html_path:
        print(f"HTML: {html_path}")
    print(f"PDF:  {pdf_path}")
    if docx_path:
        print(f"DOCX: {docx_path}")


if __name__ == "__main__":
    main()
