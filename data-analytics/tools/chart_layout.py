"""Chart Layout Helper — Prevents title/legend overlap in matplotlib and Plotly charts.

Provides consistent layout functions that separate title zone from legend zone,
ensuring no visual overlap between insight titles, context subtitles, and legends.

Usage:
    # Matplotlib
    from chart_layout import apply_chart_layout, get_chart_colors
    fig, ax = plt.subplots()
    ax.plot(x, y, label="Series A")
    apply_chart_layout(fig, ax, insight="North accounts for 45%",
                       context="Sales by region, Q4 2025")

    # Plotly
    from chart_layout import apply_plotly_layout
    fig = px.bar(df, x="region", y="sales")
    apply_plotly_layout(fig, insight="North accounts for 45%",
                        context="Sales by region, Q4 2025")

    # Colors
    colors = get_chart_colors("corporate", n=5)

    # Transparency (Plotly-safe — never use hex+alpha like "#1a365d80")
    from chart_layout import to_rgba
    fill_color = to_rgba("#1a365d", 0.3)   # "rgba(26,54,93,0.3)"
    fill_color = to_rgba((26, 54, 93), 0.3)  # same result from RGB tuple
"""

from __future__ import annotations

from css_builder import get_palette, aesthetic_to_override_tokens

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default font sizes
SUPTITLE_FONTSIZE = 14
SUBTITLE_FONTSIZE = 10
SUBTITLE_COLOR = "#666666"
SUBTITLE_PAD = 12

# Margins for matplotlib (fraction of figure height)
MPL_TOP_MARGIN = 0.88
MPL_BOTTOM_MARGIN = 0.18

# Legend defaults
LEGEND_MAX_COLS = 4
LEGEND_BOTTOM_Y = -0.12
LEGEND_RIGHT_X = 1.05
LEGEND_INSIDE_ALPHA = 0.8

# Plotly margins (pixels)
PLOTLY_MARGIN = dict(t=100, b=80, l=60, r=40)


# ---------------------------------------------------------------------------
# Matplotlib
# ---------------------------------------------------------------------------

def apply_chart_layout(
    fig,
    ax,
    insight: str,
    context: str = "",
    legend_position: str = "bottom",
    style: str = "corporate",
) -> None:
    """Apply anti-overlap layout to a matplotlib figure.

    Places the insight as suptitle at the top, context as axis subtitle,
    and moves the legend outside the title zone.

    Args:
        fig: matplotlib Figure.
        ax: matplotlib Axes (primary axes).
        insight: Main insight text (displayed as bold suptitle).
        context: Contextual subtitle (period, filters, etc.).
        legend_position: "bottom" (default), "right", or "inside".
        style: Visual style name for palette lookup (unused here but
            kept for API consistency with get_chart_colors).
    """
    # --- Title zone ---
    fig.suptitle(insight, fontsize=SUPTITLE_FONTSIZE, fontweight="bold", y=0.98)

    if context:
        ax.set_title(context, fontsize=SUBTITLE_FONTSIZE, color=SUBTITLE_COLOR, pad=SUBTITLE_PAD)

    # --- Legend zone ---
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        # Remove any existing legend first
        existing = ax.get_legend()
        if existing:
            existing.remove()

        n_items = len(handles)

        if legend_position == "bottom":
            ax.legend(
                handles, labels,
                bbox_to_anchor=(0.5, LEGEND_BOTTOM_Y),
                loc="upper center",
                ncol=min(n_items, LEGEND_MAX_COLS),
                frameon=False,
            )
        elif legend_position == "right":
            ax.legend(
                handles, labels,
                bbox_to_anchor=(LEGEND_RIGHT_X, 0.5),
                loc="center left",
            )
        elif legend_position == "inside":
            ax.legend(
                handles, labels,
                loc="best",
                framealpha=LEGEND_INSIDE_ALPHA,
            )

    # --- Reserve space for title and legend ---
    fig.subplots_adjust(top=MPL_TOP_MARGIN, bottom=MPL_BOTTOM_MARGIN)


# ---------------------------------------------------------------------------
# Plotly
# ---------------------------------------------------------------------------

def apply_plotly_layout(
    fig,
    insight: str,
    context: str = "",
    legend_position: str = "bottom",
) -> None:
    """Apply anti-overlap layout to a Plotly figure.

    Combines insight + context into an HTML title and moves the legend
    below the chart area.

    Args:
        fig: plotly Figure.
        insight: Main insight text (displayed bold).
        context: Contextual subtitle (smaller, gray).
        legend_position: "bottom" (default), "right", or "inside".
    """
    # --- Title zone (combined HTML) ---
    title_html = f"<b>{insight}</b>"
    if context:
        title_html += f"<br><span style='font-size:11px;color:gray'>{context}</span>"

    title_config = dict(text=title_html, y=0.95, x=0.5, xanchor="center", yanchor="top")

    # --- Legend zone ---
    if legend_position == "bottom":
        legend_config = dict(
            orientation="h",
            yanchor="top",
            y=LEGEND_BOTTOM_Y,
            xanchor="center",
            x=0.5,
        )
    elif legend_position == "right":
        legend_config = dict(
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
        )
    elif legend_position == "inside":
        legend_config = dict(
            yanchor="top",
            y=0.95,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.8)",
        )
    else:
        legend_config = dict(
            orientation="h",
            yanchor="top",
            y=LEGEND_BOTTOM_Y,
            xanchor="center",
            x=0.5,
        )

    fig.update_layout(
        title=title_config,
        legend=legend_config,
        margin=PLOTLY_MARGIN,
    )


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

def to_rgba(color, alpha: float = 0.5) -> str:
    """Convert a hex string or (R,G,B) tuple to an rgba() string.

    Works with both Plotly and matplotlib.  Use this instead of appending
    alpha digits to hex strings (Plotly rejects ``#RRGGBBAA``).

    Args:
        color: ``"#RRGGBB"`` hex string or ``(R, G, B)`` tuple (0-255).
        alpha: Opacity from 0.0 (transparent) to 1.0 (opaque).

    Returns:
        CSS rgba string, e.g. ``"rgba(26,54,93,0.5)"``.
    """
    if isinstance(color, str):
        h = color.strip().lstrip("#")
        if len(h) == 3:
            h = h[0] * 2 + h[1] * 2 + h[2] * 2
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    else:
        r, g, b = int(color[0]), int(color[1]), int(color[2])
    return f"rgba({r},{g},{b},{alpha})"


def get_chart_colors(style: str = "corporate", n: int = 6,
                     aesthetic_direction: dict | None = None) -> list[str]:
    """Return a list of n hex color strings from the given style palette.

    Wraps css_builder.get_palette() and extracts the chart-relevant colors
    in a consistent order.

    Args:
        style: Visual style name ("corporate", "modern", "academic").
        n: Number of colors needed.
        aesthetic_direction: Optional dict with ``palette_override`` /
            ``font_pair`` keys to apply a deliberate visual direction on
            top of the base style. Propagates to ``get_palette`` so Plotly
            charts stay coherent with the rest of the artifact.

    Returns:
        List of hex color strings (e.g., ["#1a365d", "#2b6cb0", ...]).
    """
    override_tokens = aesthetic_to_override_tokens(aesthetic_direction)
    palette = get_palette(style, override_tokens=override_tokens or None)

    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    # Build ordered color list from palette keys
    color_keys = ["primary", "secondary", "accent", "success", "warning", "danger",
                  "primary_light", "text_muted"]
    colors = []
    seen = set()
    for key in color_keys:
        val = palette.get(key)
        if val and isinstance(val, tuple) and len(val) == 3:
            hex_color = _rgb_to_hex(val)
            if hex_color not in seen:
                colors.append(hex_color)
                seen.add(hex_color)

    # If we need more colors than available, cycle
    if not colors:
        colors = ["#1a365d", "#2b6cb0", "#38a169", "#d69e2e", "#e53e3e", "#805ad5"]

    result = []
    for i in range(n):
        result.append(colors[i % len(colors)])
    return result
