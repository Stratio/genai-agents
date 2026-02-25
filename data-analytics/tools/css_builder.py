"""CSS Builder — Assembles CSS from the 3-layer architecture (tokens + theme + target).

Usage:
    from css_builder import build_css

    css_content, style_name = build_css("modern", "pdf")
    css_content, style_name = build_css("corporate", "web")
    css_content, style_name = build_css("/path/to/custom.css", "pdf")  # legacy fallback

    # For non-CSS consumers (PPTX, notebooks):
    from css_builder import get_palette
    palette = get_palette("corporate")
    # palette["primary"] == (0x1a, 0x36, 0x5d)
    # palette["font_main"] == "Inter"
"""

import re
from pathlib import Path

STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"

_KNOWN_STYLES = {"modern", "corporate", "academic"}
_KNOWN_TARGETS = {"pdf", "web"}
_FALLBACK_STYLE = "corporate"


def build_css(style: str, target: str = "pdf") -> tuple[str, str]:
    """Assemble CSS by concatenating tokens + theme + target layers.

    Args:
        style: Preset name ("modern", "corporate", "academic") or path to
            a custom CSS file (legacy fallback — returned as-is).
        target: "pdf" or "web".

    Returns:
        Tuple of (css_content, canonical_style_name).
    """
    # Legacy fallback: if style is a file path, return it as-is
    style_path = Path(style)
    if style_path.is_file():
        return style_path.read_text(encoding="utf-8"), style_path.stem

    # Normalize style name
    style_name = style.lower().strip()
    if style_name not in _KNOWN_STYLES:
        style_name = _FALLBACK_STYLE

    # Normalize target
    target_name = target.lower().strip()
    if target_name not in _KNOWN_TARGETS:
        target_name = "pdf"

    # Resolve layer paths
    tokens_file = STYLES_DIR / "tokens" / f"{style_name}.css"
    theme_file = STYLES_DIR / "themes" / f"{style_name}.css"
    target_file = STYLES_DIR / target_name / "base.css"

    # Read and concatenate: tokens first (so var() works), then theme, then target
    layers = []
    for label, path in [("tokens", tokens_file), ("theme", theme_file), ("target", target_file)]:
        if path.is_file():
            layers.append(f"/* === {label}: {path.name} === */\n{path.read_text(encoding='utf-8')}")

    # Fallback if somehow no files found (shouldn't happen with correct install)
    if not layers:
        fallback = STYLES_DIR / "tokens" / f"{_FALLBACK_STYLE}.css"
        if fallback.is_file():
            return fallback.read_text(encoding="utf-8"), _FALLBACK_STYLE
        return "", _FALLBACK_STYLE

    return "\n\n".join(layers), style_name


# ---------------------------------------------------------------------------
# Palette extraction — bridge between CSS tokens and non-CSS consumers (PPTX)
# ---------------------------------------------------------------------------

_PALETTE_MAP = {
    "modern": {
        "primary": "--primary",
        "primary_light": "--primary-dark",
        "secondary": "--secondary",
        "accent": "--accent",
        "success": "--success",
        "danger": "--danger",
        "text": "--text-primary",
        "text_muted": "--text-secondary",
        "border": "--border",
        "bg": "--bg-page",
        "bg_alt": "--bg-section",
    },
    "corporate": {
        "primary": "--primary",
        "primary_light": "--primary-light",
        "secondary": "--accent",
        "accent": "--accent",
        "success": "--success",
        "warning": "--warning",
        "danger": "--danger",
        "text": "--text-primary",
        "text_muted": "--text-secondary",
        "border": "--border",
        "bg": "#ffffff",
        "bg_alt": "--bg-light",
    },
    "academic": {
        "primary": "--heading-color",
        "primary_light": "--border-color",
        "secondary": "--caption-color",
        "accent": "--caption-color",
        "text": "--text-color",
        "text_muted": "--caption-color",
        "border": "--border-color",
        "bg": "#ffffff",
        "bg_alt": "--bg-light",
    },
}

_PALETTE_DEFAULTS = {
    "success": (0x38, 0xA1, 0x69),
    "warning": (0xD6, 0x9E, 0x2E),
    "danger": (0xE5, 0x3E, 0x3E),
}


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert a CSS hex color to an (R, G, B) tuple.

    Supports both short (#abc) and full (#aabbcc) notation.
    """
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def get_palette(style: str) -> dict:
    """Extract a normalised color/font palette from CSS tokens.

    Parses ``styles/tokens/{style}.css`` and returns a dict with keys:
        primary, primary_light, secondary, accent, success, warning, danger,
        text, text_muted, border, bg, bg_alt  — each an (R, G, B) tuple
        font_main, font_mono                  — font family name (str)

    Unknown style names fall back to *corporate*.
    """
    style_name = style.lower().strip()
    if style_name not in _KNOWN_STYLES:
        style_name = _FALLBACK_STYLE

    tokens_file = STYLES_DIR / "tokens" / f"{style_name}.css"
    if not tokens_file.is_file():
        tokens_file = STYLES_DIR / "tokens" / f"{_FALLBACK_STYLE}.css"

    css_text = tokens_file.read_text(encoding="utf-8")

    # Parse CSS custom properties from :root
    css_vars: dict[str, str] = {}
    for match in re.finditer(r"--([\w-]+)\s*:\s*([^;]+);", css_text):
        css_vars[f"--{match.group(1)}"] = match.group(2).strip()

    pmap = _PALETTE_MAP.get(style_name, _PALETTE_MAP[_FALLBACK_STYLE])

    palette: dict = {}
    for key, css_ref in pmap.items():
        if css_ref.startswith("#"):
            palette[key] = hex_to_rgb(css_ref)
        elif css_ref in css_vars:
            palette[key] = hex_to_rgb(css_vars[css_ref])
        elif key in _PALETTE_DEFAULTS:
            palette[key] = _PALETTE_DEFAULTS[key]

    # Fill in any missing semantic colours with safe defaults
    for key, default in _PALETTE_DEFAULTS.items():
        if key not in palette:
            palette[key] = default

    # --- Fonts --------------------------------------------------------
    def _first_font(raw: str) -> str:
        """Return the first font-family name, stripping quotes and fallbacks."""
        m = re.match(r"'([^']+)'|\"([^\"]+)\"|([^,]+)", raw)
        if m:
            return (m.group(1) or m.group(2) or m.group(3)).strip()
        return "Arial"

    palette["font_main"] = _first_font(css_vars.get("--font-main", "Arial"))
    palette["font_mono"] = _first_font(css_vars.get("--font-mono", "Consolas"))

    return palette
