# The skill as the sandbox receives it: the shared guide and the brand-kit theme catalog
# copied in, every reference resolving inside the skill, nothing that is not runtime.

import re


def test_ships_the_guide_and_the_theme_catalog(packed_skill):
    for relative in ("SKILL.md", "scripts/artifact.py", "visual-craftsmanship.md", "brand-kit.md"):
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
