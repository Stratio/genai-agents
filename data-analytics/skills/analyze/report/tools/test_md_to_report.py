"""Tests for ``load_aesthetic`` — the schema validator behind --aesthetic.

The validator is the last line of defence against typos; silently ignoring
misspelled keys would leave users without the visual direction they asked
for and no diagnostic.
"""

import json
import os
import sys
from pathlib import Path

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from md_to_report import load_aesthetic  # noqa: E402


def _write(tmp_path: Path, data) -> Path:
    p = tmp_path / "aesthetic.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_valid_minimal(tmp_path):
    p = _write(tmp_path, {"tone": "editorial-serious"})
    assert load_aesthetic(p) == {"tone": "editorial-serious"}


def test_valid_full(tmp_path):
    data = {
        "tone": "editorial-serious",
        "palette_override": {"--primary": "#0a2540"},
        "font_pair": ["Fraunces", "Inter"],
        "motion_budget": "expressive",
        "background_style": "gradient-mesh",
    }
    p = _write(tmp_path, data)
    assert load_aesthetic(p) == data


def test_rejects_top_level_non_object(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")
    with pytest.raises(ValueError, match="must be a JSON object"):
        load_aesthetic(p)


def test_rejects_unknown_key(tmp_path):
    p = _write(tmp_path, {"tone": "x", "bogus": True})
    with pytest.raises(ValueError, match="unknown keys"):
        load_aesthetic(p)


def test_rejects_non_string_tone(tmp_path):
    p = _write(tmp_path, {"tone": 42})
    with pytest.raises(ValueError, match="'tone' must be a string"):
        load_aesthetic(p)


def test_rejects_non_dict_palette_override(tmp_path):
    p = _write(tmp_path, {"palette_override": ["--primary", "#000"]})
    with pytest.raises(ValueError, match="palette_override.*must be an object"):
        load_aesthetic(p)


@pytest.mark.parametrize("fp", [
    "single-string",
    ["only-one"],
    ["a", "b", "c"],
    [None, "Inter"],
    ["Fraunces", ""],
])
def test_rejects_malformed_font_pair(tmp_path, fp):
    p = _write(tmp_path, {"font_pair": fp})
    with pytest.raises(ValueError, match="font_pair"):
        load_aesthetic(p)


@pytest.mark.parametrize("mb", ["expresive", "Minimal", "", "aggressive"])
def test_rejects_unknown_motion_budget(tmp_path, mb):
    p = _write(tmp_path, {"motion_budget": mb})
    with pytest.raises(ValueError, match="motion_budget"):
        load_aesthetic(p)


@pytest.mark.parametrize("bs", ["Solid", "rainbow", "gradient_mesh", ""])
def test_rejects_unknown_background_style(tmp_path, bs):
    p = _write(tmp_path, {"background_style": bs})
    with pytest.raises(ValueError, match="background_style"):
        load_aesthetic(p)


def test_accepts_all_motion_budgets(tmp_path):
    for mb in ["none", "minimal", "expressive"]:
        assert load_aesthetic(_write(tmp_path, {"motion_budget": mb}))["motion_budget"] == mb


def test_accepts_all_background_styles(tmp_path):
    for bs in ["solid", "gradient-mesh", "noise", "grain"]:
        assert load_aesthetic(_write(tmp_path, {"background_style": bs}))["background_style"] == bs
