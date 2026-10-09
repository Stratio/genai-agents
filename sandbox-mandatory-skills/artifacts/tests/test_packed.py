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
    skill = "\n".join(
        (packed_skill / name).read_text(encoding="utf-8")
        for name in ("SKILL.md", "html.md", "reference.md")
    )
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


def _contrast(a: str, b: str) -> float:
    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def test_every_theme_ships_a_dark_mode_that_reads(packed_skill):
    """A page follows the reader's dark preference with the theme's own values: text
    reaches 4.5:1 on both dark surfaces, chart colors 3:1, text on a fill 4.5:1."""
    for theme in sorted((packed_skill / "themes").glob("*.md")):
        text = theme.read_text(encoding="utf-8")
        section = text.split("## Dark mode\n", 1)[1].split("\n## ", 1)[0]
        dark = dict(re.findall(r"^\| (\w+) \| (#[0-9a-f]{6}) \|$", section, re.M))
        assert {"bg", "bg_alt", "ink", "primary", "accent", "on_primary", "on_accent"} <= set(dark), theme.name
        for token in ("ink", "muted", "primary", "accent", "state_ok", "state_warn", "state_danger"):
            for surface in ("bg", "bg_alt"):
                assert _contrast(dark[token], dark[surface]) >= 4.5, (theme.name, token, surface)
        for fill in ("primary", "accent"):
            assert _contrast(dark[f"on_{fill}"], dark[fill]) >= 4.5, (theme.name, fill)
        chart = re.findall(r"`(#[0-9a-f]{6})`", section.split("Chart categorical", 1)[1].split("\n", 1)[0])
        assert chart and all(_contrast(c, dark["bg"]) >= 3 for c in chart), theme.name
