"""Palette extraction for the docx-writer skill.

Self-contained: does not rely on CSS token files. The three base palettes
(corporate, academic, modern) mirror the values the data-analytics analytical
pipeline uses, so a DOCX produced here feels visually continuous with those
reports without importing from that agent.

``get_palette`` returns a dict with (R, G, B) tuples for every colour key
plus ``font_main`` and ``font_mono`` strings, matching the shape expected
by ``docx_builder.DOCXBuilder``. ``aesthetic_to_override_tokens`` translates
an ``aesthetic_direction`` argument into the override dict consumed by
``get_palette``.
"""
from __future__ import annotations

RGB = tuple[int, int, int]

_FALLBACK_STYLE = "corporate"

# Base palettes: one per analytical style. `corporate` is the default fallback.
# Tonal palettes (``default``, ``technical-minimal``, ``executive-editorial``,
# ``forensic``) live alongside and target use cases like quality reports or
# governance briefs where the editorial tone matters more than corporate
# consistency. All palettes use the same key set so callers can swap freely.
_PALETTES: dict[str, dict[str, RGB | str]] = {
    "corporate": {
        "primary": (0x1A, 0x36, 0x5D),
        "primary_light": (0x2B, 0x6C, 0xB0),
        "secondary": (0x31, 0x82, 0xCE),
        "accent": (0x31, 0x82, 0xCE),
        "success": (0x38, 0xA1, 0x69),
        "warning": (0xD6, 0x9E, 0x2E),
        "danger": (0xE5, 0x3E, 0x3E),
        "text": (0x1A, 0x20, 0x2C),
        "text_muted": (0x4A, 0x55, 0x68),
        "border": (0xE2, 0xE8, 0xF0),
        "bg": (0xFF, 0xFF, 0xFF),
        "bg_alt": (0xF7, 0xFA, 0xFC),
        "font_main": "Calibri",
        "font_mono": "Consolas",
    },
    "academic": {
        "primary": (0x00, 0x00, 0x00),
        "primary_light": (0x33, 0x33, 0x33),
        "secondary": (0x55, 0x55, 0x55),
        "accent": (0x55, 0x55, 0x55),
        "success": (0x38, 0xA1, 0x69),
        "warning": (0xD6, 0x9E, 0x2E),
        "danger": (0xE5, 0x3E, 0x3E),
        "text": (0x11, 0x11, 0x11),
        "text_muted": (0x55, 0x55, 0x55),
        "border": (0x99, 0x99, 0x99),
        "bg": (0xFF, 0xFF, 0xFF),
        "bg_alt": (0xF5, 0xF5, 0xF5),
        "font_main": "Libertinus Serif",
        "font_mono": "Consolas",
    },
    "modern": {
        "primary": (0x63, 0x66, 0xF1),
        "primary_light": (0x4F, 0x46, 0xE5),
        "secondary": (0x06, 0xB6, 0xD4),
        "accent": (0xF5, 0x9E, 0x0B),
        "success": (0x10, 0xB9, 0x81),
        "warning": (0xF5, 0x9E, 0x0B),
        "danger": (0xEF, 0x44, 0x44),
        "text": (0x0F, 0x17, 0x2A),
        "text_muted": (0x64, 0x74, 0x8B),
        "border": (0xE2, 0xE8, 0xF0),
        "bg": (0xFF, 0xFF, 0xFF),
        "bg_alt": (0xF8, 0xFA, 0xFC),
        "font_main": "DM Sans",
        "font_mono": "JetBrains Mono",
    },
    # ----- Editorial tones -------------------------------------------------
    # Designed for quality / governance / policy reports where a distinctive
    # tone beats corporate neutrality.
    "default": {
        "primary": (0x0F, 0x34, 0x60),
        "primary_light": (0x16, 0x21, 0x3E),
        "secondary": (0x0F, 0x34, 0x60),
        "accent": (0x0F, 0x34, 0x60),
        "success": (0x28, 0xA7, 0x45),
        "warning": (0xFD, 0x7E, 0x14),
        "danger": (0xDC, 0x35, 0x45),
        "text": (0x1A, 0x1A, 0x2E),
        "text_muted": (0x6C, 0x75, 0x7D),
        "border": (0xDD, 0xDD, 0xDD),
        "bg": (0xFF, 0xFF, 0xFF),
        "bg_alt": (0xF8, 0xF9, 0xFA),
        "font_main": "Arial",
        "font_mono": "Consolas",
    },
    "technical-minimal": {
        "primary": (0x0A, 0x4B, 0x6E),
        "primary_light": (0x06, 0x2B, 0x41),
        "secondary": (0x0A, 0x4B, 0x6E),
        "accent": (0x0A, 0x4B, 0x6E),
        "success": (0x28, 0xA7, 0x45),
        "warning": (0xFD, 0x7E, 0x14),
        "danger": (0xDC, 0x35, 0x45),
        "text": (0x16, 0x19, 0x1F),
        "text_muted": (0x60, 0x68, 0x70),
        "border": (0xDA, 0xDF, 0xE4),
        "bg": (0xFF, 0xFF, 0xFF),
        "bg_alt": (0xF5, 0xF7, 0xF9),
        "font_main": "IBM Plex Serif",
        "font_mono": "IBM Plex Mono",
    },
    "executive-editorial": {
        "primary": (0x8A, 0x33, 0x24),
        "primary_light": (0x57, 0x1C, 0x14),
        "secondary": (0x8A, 0x33, 0x24),
        "accent": (0x8A, 0x33, 0x24),
        "success": (0x28, 0xA7, 0x45),
        "warning": (0xFD, 0x7E, 0x14),
        "danger": (0xDC, 0x35, 0x45),
        "text": (0x20, 0x1A, 0x16),
        "text_muted": (0x6C, 0x5D, 0x4D),
        "border": (0xDC, 0xCF, 0xBF),
        "bg": (0xFF, 0xFF, 0xFF),
        "bg_alt": (0xFA, 0xF4, 0xEA),
        "font_main": "Crimson Pro",
        "font_mono": "JetBrains Mono",
    },
    "forensic": {
        "primary": (0x5A, 0x1C, 0x1C),
        "primary_light": (0x2F, 0x0F, 0x0F),
        "secondary": (0x5A, 0x1C, 0x1C),
        "accent": (0x5A, 0x1C, 0x1C),
        "success": (0x28, 0xA7, 0x45),
        "warning": (0xFD, 0x7E, 0x14),
        "danger": (0xDC, 0x35, 0x45),
        "text": (0x12, 0x12, 0x12),
        "text_muted": (0x5A, 0x55, 0x50),
        "border": (0xCC, 0xCC, 0xCC),
        "bg": (0xFF, 0xFF, 0xFF),
        "bg_alt": (0xEC, 0xEB, 0xE8),
        "font_main": "IBM Plex Mono",
        "font_mono": "IBM Plex Mono",
    },
}


def _hex_to_rgb(value: str) -> RGB:
    s = value.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _coerce_rgb(value: RGB | str | list | tuple) -> RGB:
    if isinstance(value, str):
        return _hex_to_rgb(value)
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return (int(value[0]), int(value[1]), int(value[2]))
    raise ValueError(f"cannot coerce {value!r} to an (R, G, B) tuple")


def aesthetic_to_override_tokens(
    aesthetic_direction: dict | None,
) -> dict:
    """Translate ``aesthetic_direction`` into an override dict for ``get_palette``.

    Recognised keys:
    - ``palette_override``: dict mapping palette-key to hex or RGB. Example::

          {"primary": "#0a2540", "accent": (240, 180, 0)}

    - ``font_pair``: ``[display, body]``. The body font becomes ``font_main``.
      The display font is not injected into the palette here; callers may use
      it for heading styles via a separate key (``aesthetic_direction.font_pair[0]``).

    Returns an empty dict when ``aesthetic_direction`` is falsy.
    """
    if not aesthetic_direction:
        return {}
    override: dict = {}
    palette_override = aesthetic_direction.get("palette_override") or {}
    for key, raw in palette_override.items():
        override[key] = _coerce_rgb(raw)
    font_pair = aesthetic_direction.get("font_pair")
    if font_pair and len(font_pair) >= 2 and font_pair[1]:
        override["font_main"] = str(font_pair[1])
    return override


def get_palette(
    style: str,
    override_tokens: dict | None = None,
) -> dict:
    """Return a palette dict for a given style, with optional overrides applied.

    Args:
        style: one of ``corporate``, ``academic``, ``modern``. Unknown names
            fall back to ``corporate``.
        override_tokens: dict returned by ``aesthetic_to_override_tokens``.
            Keys use palette naming (``primary``, not ``--primary``).

    Returns a dict with RGB tuples for colours and strings for fonts.
    """
    name = (style or "").lower().strip()
    if name not in _PALETTES:
        name = _FALLBACK_STYLE
    palette = dict(_PALETTES[name])
    if override_tokens:
        palette.update(override_tokens)
    return palette
