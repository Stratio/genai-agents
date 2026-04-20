"""PDF Generator for BI/BA Analytics Agent.

Provides two rendering modes:
- **scaffold**: Uses Jinja2 templates with predefined structure
  (executive summary -> methodology -> data -> analysis -> conclusions).
- **render_from_html**: Wraps free-form HTML with CSS, optional cover page,
  and base64-embedded images. Gives full creative freedom to the LLM.

Usage:
    from tools.pdf_generator import PDFGenerator

    gen = PDFGenerator(style="corporate")

    # Scaffold mode
    gen.render_scaffold(
        title="Sales Analysis Q4",
        kpis=[{"value": "1.2M", "label": "Revenue", "change": 15}],
        executive_summary="<p>Key findings...</p>",
        analysis="<p>Detailed analysis...</p>",
        conclusions="<p>Recommendations...</p>",
    )
    gen.save("output/report.pdf")

    # Free-form mode
    gen.render_from_html(
        html_body="<h2>Custom section</h2><p>...</p>",
        title="Creative Report",
    )
    gen.save("output/report.pdf")
"""

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from css_builder import build_css, aesthetic_to_override_tokens
from i18n import get_labels
from image_utils import embed_images_in_html

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates" / "pdf"


_MARKDOWN_SIGNATURES = (
    "\n## ", "\n### ", "\n#### ", "\n- ", "\n* ", "\n1. ", "\n> ",
    "\n```", "\n---\n", "\n|",
)


def _looks_like_markdown(text: str) -> bool:
    """Heuristic: does this string look like markdown rather than HTML?

    The scaffold sections expect HTML. LLMs frequently pass markdown,
    which Jinja renders literally and shows ``###`` or ``**`` to the
    reader. This detection is conservative — it only fires when the
    string has no obvious HTML tag and carries a markdown block-level
    signature. Inline-only markdown (bare ``**bold**`` in a paragraph)
    is not forced through the converter because it might be intentional.
    """
    if not text:
        return False
    stripped = text.strip()
    # Anything that already opens an HTML block element is left alone.
    if stripped.startswith("<") and "</" in stripped:
        return False
    if stripped.startswith(("# ", "## ", "### ", "- ", "* ", "1. ", "> ", "```")):
        return True
    return any(sig in "\n" + stripped for sig in _MARKDOWN_SIGNATURES)


def _coerce_to_html(text: str) -> str:
    """Return HTML; convert markdown when the input looks like markdown.

    If the input is already HTML (or empty / plain text), it is returned
    unchanged. Otherwise ``python-markdown`` transforms it, using the
    same extensions as ``md_to_report.py`` so authored markdown renders
    identically across the two entry points.
    """
    if not text or not _looks_like_markdown(text):
        return text
    try:
        import markdown as _md
    except ImportError:
        return text
    return _md.markdown(text, extensions=["extra", "sane_lists"])


def _footer_override_css(labels: dict) -> str:
    """CSS override for the paged-media footer using localised labels.

    The default ``@bottom-center`` in ``styles/pdf/base.css`` is in English
    so the PDF footer remains readable even if this override is missed.
    This block wins via cascade (later declaration) and pulls the page
    labels from the resolved i18n catalogue.
    """
    page_lbl = labels.get("pdf.page_label", "Page")
    of_lbl = labels.get("pdf.of_label", "of")
    return (
        "/* === footer override (i18n) === */\n"
        "@page {\n"
        "  @bottom-center {\n"
        f'    content: "{page_lbl} " counter(page) " {of_lbl} " counter(pages);\n'
        "    font-size: 8pt;\n"
        "    color: #64748b;\n"
        "  }\n"
        "}\n"
    )


class PDFGenerator:
    """Generate professional PDFs with templates or free-form HTML."""

    def __init__(self, style: str = "corporate", author: str | None = None,
                 aesthetic_direction: dict | None = None):
        """Initialize the generator.

        Args:
            style: CSS preset name (corporate, academic, modern) or path to CSS file.
            author: Default author for metadata and cover pages.
            aesthetic_direction: Optional dict with ``palette_override`` and
                ``font_pair`` keys to apply a deliberate visual direction on
                top of the base style. Translated to ``override_tokens`` on
                ``build_css``. See ``DashboardBuilder.__init__`` for the
                full schema.
        """
        override_tokens = aesthetic_to_override_tokens(aesthetic_direction)
        self._css, self._style_name = build_css(
            style, "pdf", override_tokens=override_tokens or None,
        )
        self._aesthetic = aesthetic_direction or {}
        self._author = author
        self._html: str | None = None

        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=False,
        )

    def render_scaffold(
        self,
        title: str,
        executive_summary: str = "",
        methodology: str = "",
        data_section: str = "",
        analysis: str = "",
        conclusions: str = "",
        kpis: list[dict] | None = None,
        figures: list[dict] | None = None,
        data_tables: list[dict] | None = None,
        callouts: list[dict] | None = None,
        domain: str | None = None,
        subtitle: str | None = None,
        author: str | None = None,
        show_cover: bool = True,
        lang: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> "PDFGenerator":
        """Render using the scaffold template (predefined structure).

        Args:
            title: Report title.
            executive_summary: HTML for the executive summary section.
            methodology: HTML for the methodology section.
            data_section: HTML for the data & sources section.
            analysis: HTML for the analysis section.
            conclusions: HTML for the conclusions section.
            kpis: List of KPI dicts: {"value", "label", "change"}.
            figures: List of figure dicts: {"path", "caption"}.
            data_tables: List of table dicts: {"headers", "rows", "caption"}.
            callouts: List of callout dicts: {"type", "content"}.
            domain: Data domain name for the cover page.
            subtitle: Optional subtitle for the cover page.
            author: Author override (uses instance default if not set).
            show_cover: Whether to show the cover page.
            lang: Language code. Resolves via i18n catalogue, falling back
                to `.agent_lang` file and finally English.
            labels: Override dict for specific label keys. Takes precedence
                over the catalogue.

        Returns:
            self, for method chaining.
        """
        resolved_labels = get_labels(lang=lang, overrides=labels)
        css_with_footer = self._css + "\n\n" + _footer_override_css(resolved_labels)
        template = self._env.get_template("reports/scaffold.html")
        self._html = template.render(
            title=title,
            css=css_with_footer,
            style_name=self._style_name,
            author=author or self._author,
            date=date.today().strftime("%d/%m/%Y"),
            domain=domain,
            subtitle=subtitle,
            show_cover=show_cover,
            executive_summary=_coerce_to_html(executive_summary),
            methodology=_coerce_to_html(methodology),
            data_section=_coerce_to_html(data_section),
            analysis=_coerce_to_html(analysis),
            conclusions=_coerce_to_html(conclusions),
            kpis=kpis or [],
            figures=figures or [],
            data_tables=data_tables or [],
            callouts=callouts or [],
            labels=resolved_labels,
        )
        return self

    def render_from_html(
        self,
        html_body: str,
        title: str | None = None,
        domain: str | None = None,
        subtitle: str | None = None,
        author: str | None = None,
        show_cover: bool = True,
        lang: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> "PDFGenerator":
        """Render free-form HTML with base infrastructure (CSS, cover, footer).

        The LLM generates the HTML body freely. The generator wraps it with
        the chosen CSS, optional cover page, running headers, and metadata.

        Args:
            html_body: Free-form HTML content for the report body.
            title: Report title. If omitted, uses the localised default
                ("Report" / "Informe" / ...).
            domain: Data domain name for the cover page.
            subtitle: Optional subtitle for the cover page.
            author: Author override (uses instance default if not set).
            show_cover: Whether to show the cover page.
            lang: Language code. See `render_scaffold` for resolution rules.
            labels: Override dict for specific label keys.

        Returns:
            self, for method chaining.
        """
        resolved_labels = get_labels(lang=lang, overrides=labels)
        effective_title = title or resolved_labels["report.default_title"]
        css_with_footer = self._css + "\n\n" + _footer_override_css(resolved_labels)

        # Inject html_body into a simple content block extending base.html
        content_template = self._env.from_string(
            '{% extends "base.html" %}\n{% block content %}\n'
            + html_body
            + "\n{% endblock %}"
        )
        self._html = content_template.render(
            title=effective_title,
            css=css_with_footer,
            style_name=self._style_name,
            author=author or self._author,
            date=date.today().strftime("%d/%m/%Y"),
            domain=domain,
            subtitle=subtitle,
            show_cover=show_cover,
            labels=resolved_labels,
        )
        return self

    def get_html(self) -> str:
        """Return the rendered HTML string.

        Raises:
            RuntimeError: If no render method has been called yet.
        """
        if self._html is None:
            raise RuntimeError("Call render_scaffold() or render_from_html() first.")
        return self._html

    def save(
        self,
        output_path: str | Path,
        embed_images: bool = True,
        also_save_html: bool = False,
    ) -> Path:
        """Save the rendered report as PDF (and optionally HTML).

        Args:
            output_path: Destination path for the PDF file.
            embed_images: Embed local images as base64 data URIs.
            also_save_html: Also save the intermediate HTML file.

        Returns:
            Path to the generated PDF file.

        Raises:
            RuntimeError: If no render method has been called yet.
        """
        if self._html is None:
            raise RuntimeError("Call render_scaffold() or render_from_html() first.")

        html = self._html
        if embed_images:
            html = embed_images_in_html(html, base_dir=PROJECT_ROOT)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if also_save_html:
            html_path = output_path.with_suffix(".html")
            html_path.write_text(html, encoding="utf-8")

        from weasyprint import HTML
        html_doc = HTML(string=html, base_url=str(PROJECT_ROOT))
        html_doc.write_pdf(str(output_path), presentational_hints=True)

        return output_path
