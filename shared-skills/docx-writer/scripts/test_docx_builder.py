"""Unit tests for DOCXBuilder — construction + file-on-disk smoke tests.

Run from the skill directory:

    python3 -m pytest shared-skills/docx-writer/scripts/test_docx_builder.py -v
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from docx_builder import DOCXBuilder  # noqa: E402
from palette import aesthetic_to_override_tokens, get_palette  # noqa: E402


def _read_body_text(path: Path) -> str:
    """Return all <w:t> text from word/document.xml as a single string."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    # very loose extraction, good enough for assertions
    import re
    return " ".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))


def test_builder_constructor_defaults():
    b = DOCXBuilder()
    assert b.document is not None
    section = b.document.sections[0]
    assert section.page_width is not None
    assert section.page_height is not None


def test_builder_letter_landscape():
    b = DOCXBuilder(page_size="Letter", orientation="landscape")
    section = b.document.sections[0]
    # landscape: width > height
    assert section.page_width.cm > section.page_height.cm


def test_add_cover_creates_title_and_metadata(tmp_path):
    b = DOCXBuilder()
    b.add_cover(title="Hello World", subtitle="Smoke", author="Tester",
                metadata={"Ref": "TST-001"})
    out = b.save(tmp_path / "cover.docx")
    text = _read_body_text(out)
    assert "Hello World" in text
    assert "Smoke" in text
    assert "Tester" in text
    assert "TST-001" in text


def test_add_paragraph_inline_formatting(tmp_path):
    b = DOCXBuilder()
    b.add_paragraph("This is **bold** and *italic* and `code`.")
    out = b.save(tmp_path / "para.docx")
    text = _read_body_text(out)
    assert "bold" in text and "italic" in text and "code" in text


def test_add_table_shaded_header(tmp_path):
    b = DOCXBuilder()
    b.add_table(
        headers=["Name", "Value"],
        rows=[["alpha", "1"], ["beta", "2"]],
        caption="A table",
    )
    out = b.save(tmp_path / "table.docx")
    text = _read_body_text(out)
    assert "Name" in text and "alpha" in text and "beta" in text
    assert "A table" in text


def test_add_callout_variants(tmp_path):
    b = DOCXBuilder()
    for kind in ("info", "success", "warning", "danger"):
        b.add_callout(f"Callout kind={kind}", kind=kind)
    out = b.save(tmp_path / "callouts.docx")
    text = _read_body_text(out)
    assert "Callout kind=info" in text
    assert "Callout kind=warning" in text


def test_add_list_bullet_and_ordered(tmp_path):
    b = DOCXBuilder()
    b.add_list(["first bullet", "second bullet"], ordered=False)
    b.add_list(["first ordered", "second ordered"], ordered=True)
    out = b.save(tmp_path / "lists.docx")
    text = _read_body_text(out)
    assert "first bullet" in text and "second ordered" in text


def test_add_code_block_preserves_text(tmp_path):
    b = DOCXBuilder()
    b.add_code_block("def f(x):\n    return x + 1")
    out = b.save(tmp_path / "code.docx")
    text = _read_body_text(out)
    assert "def f(x):" in text
    assert "return x + 1" in text


def test_add_markdown_block_headings_and_tables(tmp_path):
    b = DOCXBuilder()
    md = (
        "# Title\n\nParagraph with **strong** words.\n\n"
        "- item one\n- item two\n\n"
        "| Col | Val |\n|-----|-----|\n| A   | 1   |\n| B   | 2   |\n"
    )
    b.add_markdown_block(md)
    out = b.save(tmp_path / "md.docx")
    text = _read_body_text(out)
    assert "Title" in text and "item one" in text
    assert "Col" in text and "A" in text


def test_palette_aesthetic_override_changes_primary(tmp_path):
    direction = {"tone": "corporate",
                 "palette_override": {"primary": "#aa0000"},
                 "font_pair": ["Instrument Serif", "Crimson Pro"]}
    override = aesthetic_to_override_tokens(direction)
    assert override["primary"] == (0xAA, 0x00, 0x00)
    assert override["font_main"] == "Crimson Pro"

    b = DOCXBuilder(aesthetic_direction=direction)
    b.add_cover(title="Override")
    out = b.save(tmp_path / "override.docx")
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    # primary colour used on title — expect AA0000 somewhere in the xml
    assert "AA0000" in xml.upper()


def test_set_footer_page_numbers(tmp_path):
    b = DOCXBuilder()
    b.add_paragraph("Body paragraph.")
    b.set_footer_page_numbers(lang="en")
    out = b.save(tmp_path / "footer.docx")
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    # python-docx writes footer parts under word/footerN.xml
    assert any(n.startswith("word/footer") and n.endswith(".xml") for n in names)


@pytest.mark.parametrize("tone", ["corporate", "academic", "modern"])
def test_palette_returns_rgb_tuples(tone):
    p = get_palette(tone)
    for key in ("primary", "text", "bg_alt"):
        value = p[key]
        assert isinstance(value, tuple) and len(value) == 3
        assert all(0 <= v <= 255 for v in value)


def test_palette_override_accepts_rgb_tuple():
    """aesthetic_to_override_tokens must accept palette_override values as tuples."""
    direction = {"palette_override": {"primary": (170, 0, 0)}}
    override = aesthetic_to_override_tokens(direction)
    assert override["primary"] == (170, 0, 0)

    p = get_palette("corporate", override_tokens=override)
    assert p["primary"] == (170, 0, 0)


def test_add_figure_missing_image_inserts_placeholder(tmp_path):
    """add_figure with a non-existent path should render a visible placeholder."""
    b = DOCXBuilder()
    b.add_figure("/nonexistent/image.png", caption="Missing illustration")
    out = b.save(tmp_path / "missing_fig.docx")
    text = _read_body_text(out)
    assert "Image not found" in text
    assert "Missing illustration" in text


def test_inline_formatting_bold_with_nested_italic(tmp_path):
    """Bold block containing an italic span should be captured as a single bold run."""
    b = DOCXBuilder()
    b.add_paragraph("Text with **bold and *italic* inside** end.")
    out = b.save(tmp_path / "nested.docx")
    text = _read_body_text(out)
    # All three substrings must be present, in order, without orphan asterisks
    assert "bold and" in text
    assert "italic" in text
    assert "end." in text
    assert "*" not in text, "Raw asterisks leaked into the body text"


# ---------------------------------------------------------------------------
# E1 — add_html_block (rich HTML, inline images, tables, callouts)
# ---------------------------------------------------------------------------

def test_add_html_block_preserves_headings_paragraphs_lists(tmp_path):
    b = DOCXBuilder()
    html = (
        "<h1>Chapter</h1>"
        "<p>Intro with <strong>bold</strong> and <em>italic</em>.</p>"
        "<ul><li>first</li><li>second</li></ul>"
        "<pre><code>def f(): return 1</code></pre>"
        "<hr />"
    )
    b.add_html_block(html)
    out = b.save(tmp_path / "html.docx")
    text = _read_body_text(out)
    assert "Chapter" in text
    assert "Intro with" in text and "bold" in text and "italic" in text
    assert "first" in text and "second" in text
    assert "def f():" in text


def test_add_html_block_embeds_base64_image(tmp_path):
    """An <img> with a data:image/...;base64,... URI must be decoded and embedded."""
    # Minimal 1x1 transparent PNG, base64-encoded
    png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAA"
        "AAAYAAjCB0C8AAAAASUVORK5CYII="
    )
    html = (
        f'<figure><img src="data:image/png;base64,{png_b64}" alt="dot" />'
        "<figcaption>Tiny dot</figcaption></figure>"
    )
    b = DOCXBuilder()
    b.add_html_block(html)
    out = b.save(tmp_path / "img.docx")
    # Caption makes it into the body; the image itself is verified by opening the docx
    text = _read_body_text(out)
    assert "Tiny dot" in text
    # The docx must contain at least one image part under word/media/
    with zipfile.ZipFile(out) as z:
        media = [n for n in z.namelist() if n.startswith("word/media/")]
    assert media, "Expected at least one embedded image under word/media/"


def test_add_html_block_renders_tables(tmp_path):
    b = DOCXBuilder()
    html = (
        "<table>"
        "<thead><tr><th>Col</th><th>Val</th></tr></thead>"
        "<tbody><tr><td>A</td><td>1</td></tr><tr><td>B</td><td>2</td></tr></tbody>"
        "</table>"
    )
    b.add_html_block(html)
    out = b.save(tmp_path / "htmltable.docx")
    text = _read_body_text(out)
    assert "Col" in text and "A" in text and "B" in text


def test_add_html_block_callout_div(tmp_path):
    b = DOCXBuilder()
    b.add_html_block(
        '<div class="callout warning">Watch out for edge cases.</div>'
    )
    out = b.save(tmp_path / "callout.docx")
    text = _read_body_text(out)
    assert "Watch out for edge cases." in text


# ---------------------------------------------------------------------------
# E2 — cell_colors on add_table
# ---------------------------------------------------------------------------

def test_add_table_cell_colors_apply_to_run_color(tmp_path):
    """cell_colors must stamp the text colour of the targeted cells."""
    b = DOCXBuilder()
    b.add_table(
        headers=["Status", "Value"],
        rows=[["OK", "42"], ["KO", "0"]],
        cell_colors={(1, 0): (40, 167, 69), (2, 0): (220, 53, 69)},
    )
    out = b.save(tmp_path / "colored.docx")
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    # The two colours (hex without '#') must appear somewhere in document.xml
    assert "28A745" in xml.upper()
    assert "DC3545" in xml.upper()


# ---------------------------------------------------------------------------
# E3 — Editorial tones exposed from palette.py
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "tone",
    ["default", "technical-minimal", "executive-editorial", "forensic"],
)
def test_editorial_tones_return_well_formed_palette(tone):
    p = get_palette(tone)
    for key in ("primary", "text", "bg_alt", "danger", "success"):
        v = p[key]
        assert isinstance(v, tuple) and len(v) == 3
        assert all(0 <= x <= 255 for x in v)
    assert isinstance(p["font_main"], str) and p["font_main"]


def test_editorial_tone_applies_to_document(tmp_path):
    b = DOCXBuilder(aesthetic_direction={"tone": "executive-editorial"})
    b.add_cover(title="Editorial")
    out = b.save(tmp_path / "editorial.docx")
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    # Executive-editorial primary is oxblood 8A3324 — must appear in the title styling
    assert "8A3324" in xml.upper()
