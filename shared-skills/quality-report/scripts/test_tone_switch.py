"""Tests for the visual tone switch in quality-report.

Each tone must apply its own palette and type pairing to the HTML template
and to the DOCX output. The default behaviour (tone=None) must match the
legacy palette so existing callers are not affected.
"""

import os
import sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from quality_report_generator import (  # noqa: E402
    HTML_TEMPLATE,
    TONES,
    _apply_tone,
    _tone_palette,
    _hex_to_rgbcolor,
)


def test_default_palette_matches_legacy_accent():
    palette = _tone_palette(None)
    assert palette["accent"] == "#0f3460"


def test_unknown_tone_falls_back_to_default():
    palette = _tone_palette("does-not-exist")
    assert palette == TONES["default"]


@pytest.mark.parametrize("tone", ["default", "technical-minimal",
                                  "executive-editorial", "forensic"])
def test_apply_tone_substitutes_all_placeholders(tone):
    out = _apply_tone(HTML_TEMPLATE, tone)
    for key in TONES[tone]:
        assert "{{ " + key + " }}" not in out, (
            f"placeholder for {key} leaked through for tone {tone}"
        )


@pytest.mark.parametrize("tone", ["technical-minimal", "executive-editorial",
                                  "forensic"])
def test_apply_tone_produces_distinct_accent_from_default(tone):
    default_out = _apply_tone(HTML_TEMPLATE, "default")
    tone_out = _apply_tone(HTML_TEMPLATE, tone)
    assert TONES[tone]["accent"] in tone_out
    assert TONES[tone]["accent"] not in default_out


def test_apply_tone_changes_body_font_family():
    default_out = _apply_tone(HTML_TEMPLATE, "default")
    forensic_out = _apply_tone(HTML_TEMPLATE, "forensic")
    assert "IBM Plex Mono" in forensic_out
    assert "IBM Plex Mono" not in default_out


def test_hex_to_rgbcolor_parses_tone_palette():
    class FakeRgb:
        def __init__(self, r, g, b):
            self.value = (r, g, b)

    rgb = _hex_to_rgbcolor("#8a3324", FakeRgb)
    assert rgb.value == (0x8a, 0x33, 0x24)
