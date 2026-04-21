"""Tests for the optional ``override_tokens`` extension in css_builder.

The feature adds a final ``:root`` block to the assembled CSS and merges
the same keys into ``get_palette``, so the HTML, PDF, DOCX, PPTX and chart
colour pickers all share a single source of visual truth for a design-first
artifact.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from css_builder import (  # noqa: E402
    build_css,
    get_palette,
    aesthetic_to_override_tokens,
    hex_to_rgb,
)


def test_build_css_baseline_has_no_override_marker():
    css, name = build_css("corporate", "web")
    assert name == "corporate"
    assert "/* === override === */" not in css


def test_build_css_unknown_style_falls_back_to_corporate():
    _, name = build_css("does-not-exist", "web")
    assert name == "corporate"


def test_build_css_unknown_target_falls_back_to_pdf():
    # Target is normalised internally; unknown target should still produce CSS.
    css, _ = build_css("corporate", "bogus-target")
    assert css  # not empty
    assert "--primary" in css


def test_build_css_override_wins_over_theme_via_cascade():
    """The final :root block must appear AFTER tokens/theme/target layers."""
    css, _ = build_css(
        "corporate", "web",
        override_tokens={"--primary": "#0a2540"},
    )
    tokens_marker = css.find("/* === tokens")
    override_marker = css.find("/* === override === */")
    assert tokens_marker != -1
    assert override_marker > tokens_marker, (
        "override must sit after the base layers to win the cascade"
    )


def test_build_css_appends_final_root_block():
    css, _ = build_css(
        "corporate", "web",
        override_tokens={"--primary": "#0a2540", "--font-main": "'Fraunces'"},
    )
    assert "/* === override === */" in css
    assert "#0a2540" in css
    assert "'Fraunces'" in css
    assert css.rstrip().endswith("}")


def test_get_palette_baseline_unchanged():
    baseline = get_palette("corporate")
    second_call = get_palette("corporate", override_tokens=None)
    assert baseline == second_call


def test_get_palette_override_wins_over_tokens():
    overridden = get_palette(
        "corporate",
        override_tokens={"--primary": "#0a2540", "--font-main": "Fraunces"},
    )
    assert overridden["primary"] == hex_to_rgb("#0a2540")
    assert overridden["font_main"] == "Fraunces"


def test_aesthetic_to_override_tokens_empty_input():
    assert aesthetic_to_override_tokens(None) == {}
    assert aesthetic_to_override_tokens({}) == {}


def test_aesthetic_to_override_tokens_maps_font_pair_body_only():
    out = aesthetic_to_override_tokens({
        "font_pair": ["Fraunces", "Inter"],
        "palette_override": {"--primary": "#111"},
    })
    assert out["--primary"] == "#111"
    # Body font becomes --font-main; display font is NOT a token (no theme
    # declares --font-display today).
    assert out["--font-main"] == "'Inter'"
    assert "--font-display" not in out
