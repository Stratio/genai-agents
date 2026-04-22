"""Tests for structural_ops — merge, split, find-replace.

Run from the skill directory:

    python3 -m pytest shared-skills/docx-writer/scripts/test_structural_ops.py -v
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from docx_builder import DOCXBuilder  # noqa: E402
from structural_ops import find_replace_docx, merge_docx, split_docx  # noqa: E402


def _mkdoc(path: Path, title: str, body_paragraphs: list[str]) -> Path:
    b = DOCXBuilder()
    b.add_heading(title, level=1)
    for p in body_paragraphs:
        b.add_paragraph(p)
    return b.save(path)


def _all_text(path: Path) -> str:
    import re
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    return " ".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))


def test_merge_docx_concatenates_bodies(tmp_path):
    a = _mkdoc(tmp_path / "a.docx", "First", ["Alpha body."])
    b = _mkdoc(tmp_path / "b.docx", "Second", ["Beta body."])
    c = _mkdoc(tmp_path / "c.docx", "Third", ["Gamma body."])
    out = merge_docx([a, b, c], tmp_path / "merged.docx")
    assert out.exists()
    text = _all_text(out)
    assert "First" in text and "Second" in text and "Third" in text
    assert "Alpha body." in text and "Gamma body." in text


def test_merge_docx_is_valid_zip(tmp_path):
    a = _mkdoc(tmp_path / "a.docx", "A", ["one"])
    b = _mkdoc(tmp_path / "b.docx", "B", ["two"])
    out = merge_docx([a, b], tmp_path / "merged.docx")
    with zipfile.ZipFile(out) as z:
        assert "word/document.xml" in z.namelist()
        assert "[Content_Types].xml" in z.namelist()


def test_split_by_heading_level(tmp_path):
    b = DOCXBuilder()
    b.add_heading("Section One", level=1)
    b.add_paragraph("Content for one.")
    b.add_heading("Section Two", level=1)
    b.add_paragraph("Content for two.")
    b.add_heading("Section Three", level=1)
    b.add_paragraph("Content for three.")
    src = b.save(tmp_path / "src.docx")

    parts = split_docx(src, tmp_path / "parts", by="heading-level", level=1)
    assert len(parts) == 3
    texts = [_all_text(p) for p in parts]
    assert any("Section One" in t and "Content for one." in t for t in texts)
    assert any("Section Three" in t and "Content for three." in t for t in texts)


def test_find_replace_literal(tmp_path):
    src = _mkdoc(tmp_path / "src.docx", "Policy",
                 ["The term is 30 days.", "Apply 30 days consistently."])
    out = find_replace_docx(
        src, tmp_path / "out.docx",
        mapping={"30 days": "60 days"},
    )
    text = _all_text(out)
    assert "60 days" in text
    assert "30 days" not in text


def test_find_replace_regex(tmp_path):
    src = _mkdoc(tmp_path / "src.docx", "Codes",
                 ["Reference AB-001 valid.", "Reference CD-002 valid."])
    out = find_replace_docx(
        src, tmp_path / "out.docx",
        mapping={r"[A-Z]{2}-\d{3}": "REDACTED"},
        use_regex=True,
    )
    text = _all_text(out)
    assert "REDACTED" in text
    assert "AB-001" not in text and "CD-002" not in text


def test_find_replace_preserves_non_matching_text(tmp_path):
    src = _mkdoc(tmp_path / "src.docx", "Keep",
                 ["This sentence stays intact."])
    out = find_replace_docx(
        src, tmp_path / "out.docx",
        mapping={"nonexistent": "whatever"},
    )
    text = _all_text(out)
    assert "This sentence stays intact." in text


def test_split_by_page_break(tmp_path):
    """split_docx(by='page-break') should cut at each explicit w:br w:type='page'."""
    b = DOCXBuilder()
    b.add_heading("Chapter One", level=1)
    b.add_paragraph("Content of chapter one.")
    b.add_page_break()
    b.add_heading("Chapter Two", level=1)
    b.add_paragraph("Content of chapter two.")
    b.add_page_break()
    b.add_heading("Chapter Three", level=1)
    b.add_paragraph("Content of chapter three.")
    src = b.save(tmp_path / "src.docx")

    parts = split_docx(src, tmp_path / "parts", by="page-break", stem="part")
    assert len(parts) == 3
    texts = [_all_text(p) for p in parts]
    assert any("Chapter One" in t and "chapter one" in t for t in texts)
    assert any("Chapter Three" in t and "chapter three" in t for t in texts)
