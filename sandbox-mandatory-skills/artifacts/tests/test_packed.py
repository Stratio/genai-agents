# The skill as the sandbox receives it: the shared guide and the brand-kit theme catalog
# copied in, every reference resolving inside the skill, nothing that is not runtime.

import re

import pytest


def test_ships_the_guide_and_the_theme_catalog(packed_skill):
    for relative in (
        "SKILL.md",
        "scripts/artifact.py",
        "scripts/embed_fonts.py",
        "visual-craftsmanship.md",
        "brand-kit.md",
    ):
        assert (packed_skill / relative).is_file(), relative
    assert sorted(p.name for p in (packed_skill / "themes").glob("*.md"))


def test_every_theme_the_catalog_lists_is_there(packed_skill):
    catalog = (packed_skill / "brand-kit.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"\(themes/([\w-]+\.md)\)", catalog))
    assert listed
    assert listed <= {p.name for p in (packed_skill / "themes").glob("*.md")}


def test_references_are_local(packed_skill):
    """guides/<file> becomes <file> once the guide is copied next to SKILL.md."""
    skill = (packed_skill / "SKILL.md").read_text(encoding="utf-8")
    assert "guides/" not in skill
    assert "`visual-craftsmanship.md`" in skill
    for theme in re.findall(r"themes/([\w-]+\.md)", skill):
        assert (packed_skill / "themes" / theme).is_file(), theme


def test_only_its_own_skill_md(packed_skill):
    """Any other SKILL.md inside it would load as a skill of its own."""
    assert [p.relative_to(packed_skill).as_posix() for p in packed_skill.rglob("SKILL.md")] == ["SKILL.md"]


def test_development_files_stay_behind(packed_skill):
    assert not (packed_skill / "tests").exists()
    assert not (packed_skill / "guides").exists()
    assert not (packed_skill / "bundle-assets").exists()
    assert not list(packed_skill.rglob("__pycache__"))


def _embed_fonts(packed_skill):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "embed_fonts", packed_skill / "scripts" / "embed_fonts.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ships_fonts_with_their_licences(packed_skill):
    fonts = packed_skill / "fonts"
    assert list(fonts.glob("*.ttf"))
    assert list(fonts.glob("*OFL.txt"))


def test_reads_each_family_from_the_font_itself(packed_skill):
    """Names come from the files' name tables, not their file names: "JetBrainsMono"
    is "JetBrains Mono", "IBMPlexMono" is "IBM Plex Mono"."""
    catalog = _embed_fonts(packed_skill).catalog()
    assert {"Crimson Pro", "JetBrains Mono", "IBM Plex Mono", "Lora"} <= set(catalog)
    weights = {(f["weight"], f["style"]) for f in catalog["Lora"]}
    assert ("400", "normal") in weights and ("700", "normal") in weights
    assert any(style == "italic" for _, style in weights)


def test_embeds_into_the_placeholder_and_reports_what_is_missing(packed_skill, tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<style>/* fonts */ body { font-family: 'Lora', serif }</style>")

    result = _embed_fonts(packed_skill).embed(page, ["Lora", "Inter"])

    text = page.read_text()
    assert "/* fonts */" not in text
    assert text.count("@font-face") == len(_embed_fonts(packed_skill).catalog()["Lora"])
    assert "url(data:font/ttf;base64," in text
    assert result["embedded"] == ["Lora"] and result["missing"] == ["Inter"]


def test_a_page_without_the_placeholder_is_left_alone(packed_skill, tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<style>body{}</style>")

    with pytest.raises(SystemExit):
        _embed_fonts(packed_skill).embed(page, ["Lora"])
    assert page.read_text() == "<style>body{}</style>"
