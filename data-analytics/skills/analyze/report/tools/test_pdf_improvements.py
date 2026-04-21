"""Tests for PDF improvement utilities: image_utils, md_to_report, pdf_generator."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure tools/ is on sys.path for local imports
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

# Inject a fake weasyprint module so tests run without system libs (cairo, pango)
_weasyprint_mock = MagicMock()
sys.modules.setdefault("weasyprint", _weasyprint_mock)

from image_utils import embed_images_in_html, image_to_base64


# ---------------------------------------------------------------------------
# image_utils tests
# ---------------------------------------------------------------------------

class TestImageToBase64:
    def test_valid_png(self, tmp_path):
        img = tmp_path / "test.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
        result = image_to_base64(img)
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_relative_path_with_base_dir(self, tmp_path):
        img = tmp_path / "assets" / "chart.png"
        img.parent.mkdir()
        img.write_bytes(b"\x89PNG" + b"\x00" * 20)
        result = image_to_base64("assets/chart.png", base_dir=tmp_path)
        assert result is not None
        assert "base64," in result

    def test_nonexistent_file_returns_none(self):
        result = image_to_base64("/nonexistent/image.png")
        assert result is None

    def test_jpeg_mime_type(self, tmp_path):
        img = tmp_path / "photo.jpg"
        img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 30)
        result = image_to_base64(img)
        assert result is not None
        assert result.startswith("data:image/jpeg;base64,")


class TestEmbedImagesInHtml:
    def test_replaces_local_img_src(self, tmp_path):
        img = tmp_path / "chart.png"
        img.write_bytes(b"\x89PNG" + b"\x00" * 20)
        html = f'<img src="chart.png" alt="test">'
        result = embed_images_in_html(html, base_dir=tmp_path)
        assert "data:image/png;base64," in result
        assert 'src="chart.png"' not in result

    def test_skips_remote_urls(self):
        html = '<img src="https://example.com/img.png">'
        result = embed_images_in_html(html)
        assert result == html

    def test_skips_data_uris(self):
        html = '<img src="data:image/png;base64,abc123">'
        result = embed_images_in_html(html)
        assert result == html

    def test_preserves_missing_files(self):
        html = '<img src="nonexistent.png">'
        result = embed_images_in_html(html, base_dir=Path("/tmp"))
        assert result == html


# ---------------------------------------------------------------------------
# md_to_report tests
# ---------------------------------------------------------------------------

from md_to_report import _build_cover_html, md_to_html, resolve_css


class TestResolveCss:
    def test_preset_corporate(self):
        css = resolve_css("corporate")
        assert "tokens: corporate.css" in css

    def test_preset_academic(self):
        css = resolve_css("academic")
        assert "tokens: academic.css" in css

    def test_preset_modern(self):
        css = resolve_css("modern")
        assert "tokens: modern.css" in css

    def test_custom_file(self, tmp_path):
        custom = tmp_path / "custom.css"
        custom.write_text("body { color: red; }")
        css = resolve_css(str(custom))
        assert "color: red" in css

    def test_unknown_falls_back(self):
        css = resolve_css("nonexistent_style_xyz")
        assert "tokens: corporate.css" in css


class TestBuildCoverHtml:
    def test_basic_cover(self):
        html = _build_cover_html("Test Report")
        assert "cover-page" in html
        assert "Test Report" in html
        assert "Date:" in html

    def test_cover_with_author_and_domain(self):
        html = _build_cover_html("Report", author="Alice", domain="Sales")
        assert "Alice" in html
        assert "Sales" in html
        assert "Author:" in html
        assert "Domain:" in html


class TestMdToHtml:
    def test_basic_conversion(self):
        html = md_to_html("# Hello\n\nWorld", "body{}", title="Test")
        assert "<h1" in html and "Hello</h1>" in html
        assert "<p>World</p>" in html
        assert "<title>Test</title>" in html

    def test_author_meta_tag(self):
        html = md_to_html("text", "body{}", author="Bob")
        assert 'name="author"' in html
        assert "Bob" in html

    def test_cover_page_generation(self):
        html = md_to_html("text", "body{}", title="My Report", cover=True)
        assert "cover-page" in html
        assert "My Report" in html

    def test_no_cover_by_default(self):
        html = md_to_html("text", "body{}")
        assert "cover-page" not in html

    def test_running_header(self):
        html = md_to_html("text", "body{}", title="Header Test")
        assert "running-header" in html


class TestConvert:
    @patch("weasyprint.HTML")
    def test_convert_creates_files(self, mock_html_cls, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent here.")
        output_dir = tmp_path / "out"

        mock_instance = MagicMock()
        mock_html_cls.return_value = mock_instance

        from md_to_report import convert

        html_path, pdf_path, docx_path = convert(md_file, output_dir, "corporate", also_save_html=True)

        assert html_path is not None
        assert html_path.exists()
        assert html_path.suffix == ".html"
        content = html_path.read_text()
        assert "tokens: corporate.css" in content
        mock_instance.write_pdf.assert_called_once()

    @patch("weasyprint.HTML")
    def test_convert_with_cover(self, mock_html_cls, tmp_path):
        md_file = tmp_path / "report.md"
        md_file.write_text("# Title\n\nBody")
        output_dir = tmp_path / "out"

        mock_instance = MagicMock()
        mock_html_cls.return_value = mock_instance

        from md_to_report import convert

        html_path, _, _ = convert(
            md_file, output_dir, "corporate",
            author="Test Author", cover=True, domain="Finance",
            also_save_html=True,
        )
        assert html_path is not None
        content = html_path.read_text()
        assert "cover-page" in content
        assert "Test Author" in content
        assert "Finance" in content


# ---------------------------------------------------------------------------
# pdf_generator tests
# ---------------------------------------------------------------------------

from pdf_generator import PDFGenerator


class TestPDFGenerator:
    def test_scaffold_generates_html(self):
        gen = PDFGenerator(style="corporate")
        gen.render_scaffold(
            title="Test Report",
            executive_summary="<p>Summary</p>",
            analysis="<p>Analysis</p>",
            conclusions="<p>Conclusions</p>",
            kpis=[{"value": "100", "label": "Sales", "change": 5}],
        )
        html = gen.get_html()
        assert "Test Report" in html
        assert "Summary" in html
        assert "Analysis" in html
        assert "Conclusions" in html
        assert "100" in html
        assert "Sales" in html

    def test_scaffold_with_tables(self):
        gen = PDFGenerator(style="modern")
        gen.render_scaffold(
            title="Table Test",
            executive_summary="<p>OK</p>",
            analysis="<p>Detail</p>",
            conclusions="<p>Done</p>",
            data_tables=[{
                "headers": ["Name", "Value"],
                "rows": [["A", "1"], ["B", "2"]],
                "caption": "Test Table",
            }],
        )
        html = gen.get_html()
        assert "<th>Name</th>" in html
        assert "<td>A</td>" in html
        assert "Test Table" in html

    def test_render_from_html(self):
        gen = PDFGenerator(style="academic", author="Test Author")
        gen.render_from_html(
            html_body="<h2>Custom Section</h2><p>Free content</p>",
            title="Creative Report",
            show_cover=True,
            domain="Sales",
        )
        html = gen.get_html()
        assert "Creative Report" in html
        assert "Custom Section" in html
        assert "Free content" in html
        assert "cover-page" in html
        assert "Test Author" in html

    def test_render_from_html_no_cover(self):
        gen = PDFGenerator(style="corporate")
        gen.render_from_html(
            html_body="<p>Body only</p>",
            title="No Cover",
            show_cover=False,
        )
        html = gen.get_html()
        assert '<div class="cover-page">' not in html
        assert "Body only" in html

    def test_get_html_before_render_raises(self):
        gen = PDFGenerator()
        with pytest.raises(RuntimeError, match="render"):
            gen.get_html()

    def test_save_before_render_raises(self):
        gen = PDFGenerator()
        with pytest.raises(RuntimeError, match="render"):
            gen.save("/tmp/test.pdf")

    @patch("weasyprint.HTML")
    def test_save_also_html(self, mock_html_cls, tmp_path):
        mock_instance = MagicMock()
        mock_html_cls.return_value = mock_instance

        gen = PDFGenerator(style="corporate")
        gen.render_from_html(html_body="<p>Test</p>", title="HTML Test")

        output = tmp_path / "report.pdf"
        gen.save(str(output), also_save_html=True)

        html_path = tmp_path / "report.html"
        assert html_path.exists()

    def test_all_styles_render(self):
        for style in ("corporate", "academic", "modern"):
            gen = PDFGenerator(style=style)
            gen.render_scaffold(
                title=f"{style} test",
                executive_summary="<p>OK</p>",
                analysis="<p>OK</p>",
                conclusions="<p>OK</p>",
                show_cover=True,
            )
            html = gen.get_html()
            assert "cover-page" in html
            assert f"{style} test" in html

    def test_scaffold_with_figures(self):
        gen = PDFGenerator(style="corporate")
        gen.render_scaffold(
            title="Figure Test",
            executive_summary="<p>Summary</p>",
            analysis="<p>Analysis</p>",
            conclusions="<p>Done</p>",
            figures=[{"path": "assets/chart.png", "caption": "Sales Chart"}],
        )
        html = gen.get_html()
        assert "assets/chart.png" in html
        assert "Sales Chart" in html

    def test_scaffold_with_callouts(self):
        gen = PDFGenerator(style="modern")
        gen.render_scaffold(
            title="Callout Test",
            executive_summary="<p>Sum</p>",
            analysis="<p>Detail</p>",
            conclusions="<p>End</p>",
            callouts=[{"type": "warning", "content": "<p>Watch out!</p>"}],
        )
        html = gen.get_html()
        assert "callout-warning" in html
        assert "Watch out!" in html


# ---------------------------------------------------------------------------
# Markdown tolerance in render_scaffold
# ---------------------------------------------------------------------------

class TestMarkdownCoercion:
    """LLM-generated scaffolds frequently pass markdown where HTML is expected.
    The generator must convert it so readers never see raw ``###`` or ``**``."""

    def test_looks_like_markdown_detects_heading(self):
        from pdf_generator import _looks_like_markdown
        assert _looks_like_markdown("### Heading\n- item")

    def test_looks_like_markdown_detects_bullet_list(self):
        from pdf_generator import _looks_like_markdown
        assert _looks_like_markdown("- first\n- second")

    def test_looks_like_markdown_leaves_html_alone(self):
        from pdf_generator import _looks_like_markdown
        assert not _looks_like_markdown("<p>texto</p>")
        assert not _looks_like_markdown("<h2>Título</h2><p>cuerpo</p>")

    def test_looks_like_markdown_ignores_plain_text(self):
        from pdf_generator import _looks_like_markdown
        assert not _looks_like_markdown("Un párrafo normal sin formato.")

    def test_coerce_converts_markdown_to_html(self):
        from pdf_generator import _coerce_to_html
        html = _coerce_to_html("### Hallazgos\n- **Liderazgo:** texto\n- **Foco:** otro")
        assert "<h3>Hallazgos</h3>" in html
        assert "<ul>" in html and "<li>" in html
        assert "<strong>Liderazgo:</strong>" in html

    def test_coerce_preserves_already_html(self):
        from pdf_generator import _coerce_to_html
        original = "<h2>Title</h2><p>body</p>"
        assert _coerce_to_html(original) == original

    def test_coerce_preserves_empty(self):
        from pdf_generator import _coerce_to_html
        assert _coerce_to_html("") == ""

    def test_render_scaffold_converts_markdown_in_analysis(self):
        from pdf_generator import PDFGenerator
        gen = PDFGenerator(style="corporate", author="X")
        gen.render_scaffold(
            title="MD Test",
            analysis="### Findings\n- **Bold thing**\n- item two",
        )
        html = gen.get_html()
        assert "<h3>Findings</h3>" in html
        assert "<strong>Bold thing</strong>" in html
        # The raw markdown tokens should NOT leak into the output.
        assert "### Findings" not in html
        assert "**Bold thing**" not in html


class TestFooterI18n:
    """The paged-media footer must reflect the resolved language."""

    def test_english_footer(self):
        from pdf_generator import _footer_override_css
        from i18n import get_labels
        css = _footer_override_css(get_labels(lang="en"))
        assert '"Page "' in css
        assert '" of "' in css
        assert "Pagina" not in css

    def test_spanish_footer_has_tilde(self):
        from pdf_generator import _footer_override_css
        from i18n import get_labels
        css = _footer_override_css(get_labels(lang="es"))
        assert '"Página "' in css
        assert '" de "' in css
        # "Pagina" without the accent is the legacy bug we removed.
        assert '"Pagina "' not in css

    def test_scaffold_injects_localised_footer(self):
        from pdf_generator import PDFGenerator
        gen = PDFGenerator(style="corporate", author="X")
        gen.render_scaffold(title="t", lang="es")
        html = gen.get_html()
        assert "Página" in html
        assert "Pagina " not in html
