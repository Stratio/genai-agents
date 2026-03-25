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

from css_builder import build_css
from image_utils import embed_images_in_html

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates" / "pdf"


class PDFGenerator:
    """Generate professional PDFs with templates or free-form HTML."""

    def __init__(self, style: str = "corporate", author: str | None = None):
        """Initialize the generator.

        Args:
            style: CSS preset name (corporate, academic, modern) or path to CSS file.
            author: Default author for metadata and cover pages.
        """
        self._css, self._style_name = build_css(style, "pdf")
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

        Returns:
            self, for method chaining.
        """
        template = self._env.get_template("reports/scaffold.html")
        self._html = template.render(
            title=title,
            css=self._css,
            style_name=self._style_name,
            author=author or self._author,
            date=date.today().strftime("%d/%m/%Y"),
            domain=domain,
            subtitle=subtitle,
            show_cover=show_cover,
            executive_summary=executive_summary,
            methodology=methodology,
            data_section=data_section,
            analysis=analysis,
            conclusions=conclusions,
            kpis=kpis or [],
            figures=figures or [],
            data_tables=data_tables or [],
            callouts=callouts or [],
        )
        return self

    def render_from_html(
        self,
        html_body: str,
        title: str = "Report",
        domain: str | None = None,
        subtitle: str | None = None,
        author: str | None = None,
        show_cover: bool = True,
    ) -> "PDFGenerator":
        """Render free-form HTML with base infrastructure (CSS, cover, footer).

        The LLM generates the HTML body freely. The generator wraps it with
        the chosen CSS, optional cover page, running headers, and metadata.

        Args:
            html_body: Free-form HTML content for the report body.
            title: Report title.
            domain: Data domain name for the cover page.
            subtitle: Optional subtitle for the cover page.
            author: Author override (uses instance default if not set).
            show_cover: Whether to show the cover page.

        Returns:
            self, for method chaining.
        """
        # Inject html_body into a simple content block extending base.html
        content_template = self._env.from_string(
            '{% extends "base.html" %}\n{% block content %}\n'
            + html_body
            + "\n{% endblock %}"
        )
        self._html = content_template.render(
            title=title,
            css=self._css,
            style_name=self._style_name,
            author=author or self._author,
            date=date.today().strftime("%d/%m/%Y"),
            domain=domain,
            subtitle=subtitle,
            show_cover=show_cover,
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
