# pptx-writer — REFERENCE

Copy-paste snippets for the slide compositions and operations that
`SKILL.md` references but doesn't spell out inline. Load this when
you're about to build something beyond the basic title+bullets slide.

All snippets assume the design tokens and safe-area helpers from the
scaffold in `SKILL.md` §3 (`DESIGN`, `hex_to_rgb`, `MARGIN`,
`TITLE_TOP`, `TITLE_H`, `CONTENT_TOP`, `CONTENT_H`, `CONTENT_W`,
`BLANK_LAYOUT`, `add_title`).

---

## Dynamic safe-area helpers

Derived from `prs.slide_width / slide_height` so every helper works
whether the deck is 16:9, 4:3, widescreen or the user's corporate
custom ratio.

```python
from pptx.util import Inches, Emu

def safe_area(prs, *, has_footer: bool = False):
    """Return a dict of safe-area coordinates in EMU."""
    w = prs.slide_width
    h = prs.slide_height
    margin = Inches(0.5)
    title_top = Inches(0.4)
    title_h = Inches(0.9)
    footer_h = Inches(0.3) if has_footer else 0
    return {
        "slide_w":     w,
        "slide_h":     h,
        "margin":      margin,
        "title_top":   title_top,
        "title_h":     title_h,
        "content_top": title_top + title_h + Inches(0.2),
        "content_bottom": h - Inches(0.5) - footer_h,
        "content_left": margin,
        "content_w":   w - 2 * margin,
        "footer_top":  h - Inches(0.5),
        "footer_h":    footer_h,
    }

def content_area(prs, has_footer: bool = False):
    sa = safe_area(prs, has_footer=has_footer)
    return {
        "left":   sa["content_left"],
        "top":    sa["content_top"],
        "width":  sa["content_w"],
        "height": sa["content_bottom"] - sa["content_top"],
    }

def check_bounds(left, top, width, height, area) -> bool:
    """Return True if a shape at (left, top, width, height) fits in the area dict."""
    return (
        left >= area["left"]
        and top >= area["top"]
        and left + width <= area["left"] + area["width"]
        and top + height <= area["top"] + area["height"]
    )

def fit_content(target_w, target_h, max_w, max_h):
    """Scale (target_w, target_h) down to fit inside (max_w, max_h) preserving ratio."""
    if target_w <= max_w and target_h <= max_h:
        return target_w, target_h
    ratio = min(max_w / target_w, max_h / target_h)
    return int(target_w * ratio), int(target_h * ratio)
```

---

## Cover slide

```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

def add_cover(prs, title: str, subtitle: str | None = None,
              author: str | None = None, date: str | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)

    # Vertically center the title/subtitle block
    title_top = Inches(1.5)
    title_box = slide.shapes.add_textbox(MARGIN, title_top, CONTENT_W, Inches(1.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.name = DESIGN["display"]
    r.font.size = Pt(DESIGN["size_title"] + 8)
    r.font.bold = True
    r.font.color.rgb = hex_to_rgb(DESIGN["primary"])

    if subtitle:
        sub_box = slide.shapes.add_textbox(
            MARGIN, title_top + Inches(1.6), CONTENT_W, Inches(0.8),
        )
        tf = sub_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = subtitle
        r.font.name = DESIGN["body"]
        r.font.size = Pt(DESIGN["size_subtitle"])
        r.font.color.rgb = hex_to_rgb(DESIGN["muted"])

    # Accent bar at top
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN, title_top - Inches(0.3),
        Inches(2.0), Inches(0.08),
    )
    bar.line.fill.background()
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(DESIGN["accent"])

    # Author / date footer
    footer_bits = [s for s in (author, date) if s]
    if footer_bits:
        foot = slide.shapes.add_textbox(
            MARGIN, prs.slide_height - Inches(0.7), CONTENT_W, Inches(0.3),
        )
        p = foot.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = "  ·  ".join(footer_bits)
        r.font.name = DESIGN["body"]
        r.font.size = Pt(DESIGN["size_small"])
        r.font.color.rgb = hex_to_rgb(DESIGN["muted"])

    return slide
```

---

## Agenda slide

```python
def add_agenda(prs, items: list[str]):
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, "Agenda")  # from SKILL.md scaffold

    box = slide.shapes.add_textbox(MARGIN, CONTENT_TOP, CONTENT_W, CONTENT_H)
    tf = box.text_frame
    tf.word_wrap = True

    for i, label in enumerate(items, start=1):
        p = tf.paragraphs[0] if i == 1 else tf.add_paragraph()
        p.space_after = Pt(12)
        num = p.add_run()
        num.text = f"{i:02d}.  "
        num.font.name = DESIGN["display"]
        num.font.size = Pt(DESIGN["size_heading"])
        num.font.color.rgb = hex_to_rgb(DESIGN["accent"])
        num.font.bold = True
        body = p.add_run()
        body.text = label
        body.font.name = DESIGN["body"]
        body.font.size = Pt(DESIGN["size_heading"])
        body.font.color.rgb = hex_to_rgb(DESIGN["ink"])

    return slide
```

---

## Section divider

```python
def add_section_divider(prs, label: str, number: str | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)

    # Large centered section name
    vert = (prs.slide_height - Inches(1.2)) // 2
    box = slide.shapes.add_textbox(MARGIN, vert, CONTENT_W, Inches(1.2))
    tf = box.text_frame
    tf.word_wrap = True
    from pptx.enum.text import PP_ALIGN
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER

    if number:
        nr = p.add_run()
        nr.text = f"{number}   "
        nr.font.name = DESIGN["display"]
        nr.font.size = Pt(24)
        nr.font.color.rgb = hex_to_rgb(DESIGN["accent"])
        nr.font.bold = True

    r = p.add_run()
    r.text = label
    r.font.name = DESIGN["display"]
    r.font.size = Pt(54)
    r.font.bold = True
    r.font.color.rgb = hex_to_rgb(DESIGN["primary"])

    return slide
```

---

## Bullet list slide

```python
def add_bullets(prs, title: str, items: list[str] | list[tuple[int, str]]):
    """
    items: list of strings (level-0 bullets) or list of (level, text) tuples
    for nested bullets. level goes 0-4.
    """
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, title)

    box = slide.shapes.add_textbox(MARGIN, CONTENT_TOP, CONTENT_W, CONTENT_H)
    tf = box.text_frame
    tf.word_wrap = True

    for i, it in enumerate(items):
        level, text = (it if isinstance(it, tuple) else (0, it))
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = level
        p.space_after = Pt(10)
        r = p.add_run()
        r.text = ("  " * level) + text
        r.font.name = DESIGN["body"]
        r.font.size = Pt(DESIGN["size_body"] - min(level, 3))
        r.font.color.rgb = hex_to_rgb(DESIGN["ink"])

    return slide
```

---

## Two-column slide

```python
def add_two_column(prs, title: str, left: list[str], right: list[str],
                   left_title: str | None = None, right_title: str | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, title)

    col_gap = Inches(0.3)
    col_w = (CONTENT_W - col_gap) // 2

    def _fill_column(box_left, items, sub_title):
        box = slide.shapes.add_textbox(box_left, CONTENT_TOP, col_w, CONTENT_H)
        tf = box.text_frame
        tf.word_wrap = True
        first = True
        if sub_title:
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = sub_title
            r.font.name = DESIGN["display"]
            r.font.size = Pt(DESIGN["size_heading"] - 6)
            r.font.bold = True
            r.font.color.rgb = hex_to_rgb(DESIGN["primary"])
            first = False
        for text in items:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_after = Pt(8)
            r = p.add_run()
            r.text = f"•  {text}"
            r.font.name = DESIGN["body"]
            r.font.size = Pt(DESIGN["size_body"])
            r.font.color.rgb = hex_to_rgb(DESIGN["ink"])

    _fill_column(MARGIN, left, left_title)
    _fill_column(MARGIN + col_w + col_gap, right, right_title)
    return slide
```

---

## KPI box

```python
def add_kpi_box(slide, left, top, width, height, label: str, value: str,
                unit: str | None = None, bg: str | None = None):
    """Render a single KPI tile with large value + small label beneath."""
    from pptx.enum.text import PP_ALIGN
    bg_hex = bg or DESIGN["bg_alt"]

    # Background rectangle
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    rect.line.fill.background()
    rect.fill.solid()
    rect.fill.fore_color.rgb = hex_to_rgb(bg_hex)

    # Value (big)
    val_box = slide.shapes.add_textbox(
        left, top + Inches(0.15), width, Inches(0.9),
    )
    tf = val_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    vr = p.add_run()
    vr.text = value
    vr.font.name = DESIGN["display"]
    vr.font.size = Pt(44)
    vr.font.bold = True
    vr.font.color.rgb = hex_to_rgb(DESIGN["primary"])
    if unit:
        ur = p.add_run()
        ur.text = f" {unit}"
        ur.font.name = DESIGN["display"]
        ur.font.size = Pt(20)
        ur.font.color.rgb = hex_to_rgb(DESIGN["muted"])

    # Label (small, below)
    lbl_box = slide.shapes.add_textbox(
        left, top + height - Inches(0.45), width, Inches(0.3),
    )
    p = lbl_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.name = DESIGN["body"]
    r.font.size = Pt(DESIGN["size_small"])
    r.font.color.rgb = hex_to_rgb(DESIGN["muted"])


def add_kpi_row(prs, title: str, kpis: list[dict]):
    """3 or 4 KPIs across the content area."""
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, title)
    n = len(kpis)
    if n == 0:
        return slide
    gap = Inches(0.3)
    tile_w = (CONTENT_W - gap * (n - 1)) // n
    tile_h = Inches(1.8)
    y = CONTENT_TOP + Inches(0.6)
    for i, kpi in enumerate(kpis):
        x = MARGIN + i * (tile_w + gap)
        add_kpi_box(slide, x, y, tile_w, tile_h,
                    kpi["label"], kpi["value"], kpi.get("unit"))
    return slide
```

---

## Table with style override

Aggressive override of python-pptx's pastel default. Primary-colour
header, alternating body rows, no vertical lines, right-aligned numerics.

```python
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.dml.color import RGBColor

def add_table_slide(prs, title: str, headers: list[str], rows: list[list[str]],
                    numeric_cols: list[int] | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, title)

    numeric_cols = numeric_cols or []
    n_cols = len(headers)
    n_rows = len(rows) + 1  # +1 header
    table_h = min(Inches(0.5) * n_rows, CONTENT_H)

    shape = slide.shapes.add_table(n_rows, n_cols, MARGIN, CONTENT_TOP,
                                   CONTENT_W, table_h)
    table = shape.table

    # Make columns equal unless caller tweaks them afterward
    col_w = CONTENT_W // n_cols
    for col in table.columns:
        col.width = col_w

    # Header row
    for c, head in enumerate(headers):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = hex_to_rgb(DESIGN["primary"])
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_top = Inches(0.08)
        cell.margin_bottom = Inches(0.08)
        tf = cell.text_frame
        tf.word_wrap = True
        tf.paragraphs[0].text = ""  # clear default
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT if c in numeric_cols else PP_ALIGN.LEFT
        r = p.add_run()
        r.text = head
        r.font.name = DESIGN["display"]
        r.font.size = Pt(DESIGN["size_body"] - 2)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Body rows
    for r_idx, row_data in enumerate(rows, start=1):
        band = DESIGN["bg_alt"] if r_idx % 2 == 0 else DESIGN["bg"]
        for c, cell_text in enumerate(row_data):
            cell = table.cell(r_idx, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = hex_to_rgb(band)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_top = Inches(0.06)
            cell.margin_bottom = Inches(0.06)
            tf = cell.text_frame
            tf.word_wrap = True
            tf.paragraphs[0].text = ""
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT if c in numeric_cols else PP_ALIGN.LEFT
            run = p.add_run()
            run.text = str(cell_text)
            run.font.name = DESIGN["body"]
            run.font.size = Pt(DESIGN["size_small"])
            run.font.color.rgb = hex_to_rgb(DESIGN["ink"])

    return slide
```

Caveats:
- `table.columns[c].width = ...` must use EMU, not Pt/Inches directly unless wrapped.
- Row heights self-adjust based on content; if a row is too tall, break the text or bump the table below the safe area check.
- For tables with > 12 rows, consider splitting across slides with the header repeated.

---

## Image with preserved aspect ratio

```python
from PIL import Image

def add_image_safe(slide, image_path: str, area: dict,
                   caption: str | None = None):
    """
    area: dict with 'left', 'top', 'width', 'height' in EMU (from content_area()).
    Scales the image to fit, preserves aspect, centers in the area.
    """
    with Image.open(image_path) as img:
        native_w, native_h = img.size
    # Target at image's native DPI, scaled into EMU
    aspect = native_w / native_h
    avail_w = area["width"]
    avail_h = area["height"]
    if caption:
        avail_h -= Inches(0.4)
    target_w = avail_w
    target_h = int(avail_w / aspect)
    if target_h > avail_h:
        target_h = avail_h
        target_w = int(avail_h * aspect)
    # Center
    left = area["left"] + (avail_w - target_w) // 2
    top = area["top"] + (avail_h - target_h) // 2
    slide.shapes.add_picture(image_path, left, top, target_w, target_h)

    if caption:
        box = slide.shapes.add_textbox(
            area["left"], top + target_h + Inches(0.05),
            area["width"], Inches(0.3),
        )
        p = box.text_frame.paragraphs[0]
        from pptx.enum.text import PP_ALIGN
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = caption
        r.font.name = DESIGN["body"]
        r.font.size = Pt(DESIGN["size_small"])
        r.font.italic = True
        r.font.color.rgb = hex_to_rgb(DESIGN["muted"])


def add_image_slide(prs, title: str, image_path: str,
                    caption: str | None = None, layout: str = "full"):
    """layout: 'full' | 'left' | 'right' — 'full' uses the whole content area."""
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, title)
    ca = content_area(prs)
    if layout == "full":
        add_image_safe(slide, image_path, ca, caption)
    elif layout == "left":
        left_area = {**ca, "width": ca["width"] // 2 - Inches(0.15)}
        add_image_safe(slide, image_path, left_area, caption)
    elif layout == "right":
        left_area = {
            **ca,
            "left": ca["left"] + ca["width"] // 2 + Inches(0.15),
            "width": ca["width"] // 2 - Inches(0.15),
        }
        add_image_safe(slide, image_path, left_area, caption)
    return slide
```

---

## Image with text (hero layout)

```python
def add_image_with_text(prs, title: str, image_path: str, body: str,
                        layout: str = "image-left"):
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, title)
    ca = content_area(prs)
    half_w = (ca["width"] - Inches(0.3)) // 2

    if layout == "image-left":
        image_area = {**ca, "width": half_w}
        text_left = ca["left"] + half_w + Inches(0.3)
    else:
        image_area = {
            **ca, "left": ca["left"] + half_w + Inches(0.3), "width": half_w,
        }
        text_left = ca["left"]

    add_image_safe(slide, image_path, image_area)

    box = slide.shapes.add_textbox(text_left, ca["top"], half_w, ca["height"])
    tf = box.text_frame
    tf.word_wrap = True
    for i, paragraph in enumerate(body.split("\n\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(10)
        r = p.add_run()
        r.text = paragraph.strip()
        r.font.name = DESIGN["body"]
        r.font.size = Pt(DESIGN["size_body"])
        r.font.color.rgb = hex_to_rgb(DESIGN["ink"])
    return slide
```

---

## Native OOXML chart — bar / column / line / pie / area

```python
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

def add_chart_slide(prs, title: str, chart_type: str,
                    categories: list[str],
                    series: list[dict]):
    """
    chart_type: 'column' | 'bar' | 'line' | 'pie' | 'area'
    series: [{'name': 'Revenue', 'values': [100, 120, 150]}, ...]
    """
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, title)

    data = CategoryChartData()
    data.categories = categories
    for s in series:
        data.add_series(s["name"], s["values"])

    chart_enum = {
        "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
        "bar":    XL_CHART_TYPE.BAR_CLUSTERED,
        "line":   XL_CHART_TYPE.LINE,
        "pie":    XL_CHART_TYPE.PIE,
        "area":   XL_CHART_TYPE.AREA,
    }[chart_type]

    ca = content_area(prs)
    chart_shape = slide.shapes.add_chart(
        chart_enum, ca["left"], ca["top"], ca["width"], ca["height"], data,
    )
    chart = chart_shape.chart
    if chart_type != "pie" and len(series) > 1:
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
    else:
        chart.has_legend = (chart_type == "pie")

    # Apply brand colours to series in order
    palette = [DESIGN["primary"], DESIGN["accent"], DESIGN["muted"]]
    for i, ser in enumerate(chart.plots[0].series):
        fill = ser.format.fill
        fill.solid()
        fill.fore_color.rgb = hex_to_rgb(palette[i % len(palette)])

    return slide
```

For **scatter**, **bubble** and **radar** charts the data shape differs:

```python
# Scatter: XyChartData with (x, y) tuples per point
xy_data = XyChartData()
ser = xy_data.add_series("Correlation")
for x, y in [(1, 2), (2, 3.5), (3, 5), (4, 4.8)]:
    ser.add_data_point(x, y)

# For bubble, use BubbleChartData with (x, y, size) triples.
# Radar uses CategoryChartData like column/line but with XL_CHART_TYPE.RADAR.
```

When the chart type is **waterfall / sunburst / sankey / combo** or
anything else python-pptx doesn't cover, render in matplotlib/plotly
with `dpi=200, facecolor="none"` and use `add_image_slide` instead.

---

## Quote slide

```python
def add_quote_slide(prs, quote: str, author: str, role: str | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    ca = content_area(prs)

    # Big opening quote mark
    mark = slide.shapes.add_textbox(
        MARGIN, ca["top"], Inches(1), Inches(1),
    )
    pr = mark.text_frame.paragraphs[0]
    rr = pr.add_run()
    rr.text = "\u201c"
    rr.font.name = DESIGN["display"]
    rr.font.size = Pt(120)
    rr.font.color.rgb = hex_to_rgb(DESIGN["accent"])

    # Quote body
    box = slide.shapes.add_textbox(
        MARGIN + Inches(0.5), ca["top"] + Inches(0.6),
        ca["width"] - Inches(0.5), Inches(2.5),
    )
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = quote
    r.font.name = DESIGN["display"]
    r.font.size = Pt(32)
    r.font.italic = True
    r.font.color.rgb = hex_to_rgb(DESIGN["ink"])

    # Attribution
    attr = slide.shapes.add_textbox(
        MARGIN + Inches(0.5), ca["top"] + Inches(3.3),
        ca["width"] - Inches(0.5), Inches(0.6),
    )
    p = attr.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"— {author}"
    r.font.name = DESIGN["body"]
    r.font.size = Pt(DESIGN["size_body"])
    r.font.color.rgb = hex_to_rgb(DESIGN["muted"])
    if role:
        rr = p.add_run()
        rr.text = f", {role}"
        rr.font.name = DESIGN["body"]
        rr.font.size = Pt(DESIGN["size_body"])
        rr.font.color.rgb = hex_to_rgb(DESIGN["muted"])

    return slide
```

---

## Conclusion slide

```python
def add_conclusion(prs, title: str, bullets: list[str]):
    return add_bullets(prs, title, bullets)
```

(Intentional: conclusion is structurally a bullet slide with a
stronger title. Override `title` to "Conclusions" / "Next steps" /
"Call to action" as appropriate.)

---

## Using a client template (`.potx` / `.pptx`)

```python
from pptx import Presentation

def build_from_template(template_path: str, out_path: str):
    prs = Presentation(template_path)

    # Inspect once to discover which layouts the template ships
    # (name them in the comments so future-you doesn't have to re-discover).
    # for i, layout in enumerate(prs.slide_layouts):
    #     print(i, layout.name)

    # Example: template ships Cover / Section / Content layouts at 0 / 1 / 2.
    COVER = prs.slide_layouts[0]
    SECTION = prs.slide_layouts[1]
    CONTENT = prs.slide_layouts[2]

    # Cover
    cover = prs.slides.add_slide(COVER)
    cover.placeholders[0].text = "Deck title"
    if len(cover.placeholders) > 1:
        cover.placeholders[1].text = "Subtitle / date / author"

    # Section divider
    sec = prs.slides.add_slide(SECTION)
    sec.placeholders[0].text = "01  Introduction"

    # Content with bullets
    content = prs.slides.add_slide(CONTENT)
    content.placeholders[0].text = "Slide heading"
    body = content.placeholders[1]
    tf = body.text_frame
    tf.text = "First bullet"
    for text in ("Second bullet", "Third bullet"):
        p = tf.add_paragraph()
        p.text = text

    prs.save(out_path)
```

Rules when using a client template:
- Do not change the master; it carries the brand.
- Do not use `slide_layouts[6]` (Blank); use the named layouts.
- Do use `placeholders` rather than `add_textbox`; the template
  positioned them.
- Still enforce `tf.word_wrap = True` if you replace a text frame's
  content wholesale.
- Still validate visually (see below).

---

## Structural validation

Reopen the saved PPTX and emit a manifest of what it actually contains.
Catches corruption, clipped text frames (missing `word_wrap`), missing
slides, mis-classified shapes. Runs in ~100 ms; call it immediately
after `prs.save(...)` on every build.

```python
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def validate_structure(pptx_path) -> dict:
    """Reopen the PPTX and emit a structural manifest."""
    path = Path(pptx_path)
    manifest: dict = {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "reopens": False,
    }
    try:
        prs = Presentation(str(path))
        manifest["reopens"] = True
    except Exception as exc:
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        return manifest

    w_in = (prs.slide_width or 0) / 914400
    h_in = (prs.slide_height or 0) / 914400
    manifest["slides"] = len(prs.slides)
    manifest["aspect_ratio"] = f"{w_in:.2f}x{h_in:.2f} in"

    shapes = {"text": 0, "picture": 0, "table": 0, "chart": 0, "other": 0}
    wrap_ok = True
    notes_count = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                shapes["text"] += 1
                if shape.text_frame.word_wrap is False:
                    wrap_ok = False
            elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                shapes["picture"] += 1
            elif shape.has_table:
                shapes["table"] += 1
            elif shape.has_chart:
                shapes["chart"] += 1
            else:
                shapes["other"] += 1
        if slide.has_notes_slide:
            notes_text = slide.notes_slide.notes_text_frame.text.strip()
            if notes_text:
                notes_count += 1

    manifest["shapes_by_type"] = shapes
    manifest["slides_with_notes"] = notes_count
    manifest["word_wrap_ok"] = wrap_ok
    return manifest


# Usage
manifest = validate_structure("output/deck.pptx")
print(manifest)
# {"path": "output/deck.pptx", "size_bytes": 38512, "reopens": True,
#  "slides": 8, "aspect_ratio": "10.00x5.63 in",
#  "shapes_by_type": {"text": 22, "picture": 3, "table": 1, "chart": 2, "other": 4},
#  "slides_with_notes": 8, "word_wrap_ok": True}
```

What to do with the manifest:

- `reopens: False` or `error` present — the file is corrupted. Fix the
  generator, don't deliver.
- `word_wrap_ok: False` — at least one text frame has `word_wrap=False`
  (the python-pptx default). Text will clip on overflow. Fix the
  emission site to set `tf.word_wrap = True`.
- `slides` does not match the brief ("pitch deck with 12 slides, got 7")
  — regenerate, don't deliver.
- `slides_with_notes` close to zero on pitch / briefing / training decks
  — speaker notes missing; flag to the user or regenerate.
- `aspect_ratio` other than the committed ratio (e.g. unexpected
  `10.00x7.50` in a 16:9 brief) — wrong scaffold loaded.

---

## Visual validation pipeline

After building, render each slide to a PNG and eyeball it. Detects
overflow, awkward contrast, spacing glitches that the XML view
doesn't surface.

```python
import shutil, subprocess, tempfile
from pathlib import Path

def validate_visual(pptx_path: str, out_dir: str, dpi: int = 150) -> list[Path]:
    if shutil.which("soffice") is None:
        raise RuntimeError("Install libreoffice for visual preview.")
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("Install poppler-utils for visual preview.")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pptx_pdf_") as tmp:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf",
             "--outdir", tmp, pptx_path],
            check=True, capture_output=True,
        )
        pdf = Path(tmp) / (Path(pptx_path).stem + ".pdf")
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi),
             str(pdf), str(out / pdf.stem)],
            check=True, capture_output=True,
        )
    return sorted(out.glob(f"{Path(pptx_path).stem}-*.png"))
```

Iterate: if a PNG shows an overflow or a broken image, regenerate
the offending slide. 2–3 iterations before a final delivery is
normal, not excessive.

---

## Export PDF

```python
import shutil, subprocess
from pathlib import Path

def export_pdf(pptx_path: str, out_dir: str) -> Path:
    if shutil.which("soffice") is None:
        raise RuntimeError("Install libreoffice for PDF export.")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(out), pptx_path],
        check=True, capture_output=True,
    )
    pdf = out / (Path(pptx_path).stem + ".pdf")
    if not pdf.exists():
        raise RuntimeError(f"soffice produced no PDF for {pptx_path}")
    return pdf
```

Default deliverable is the PPTX alone. Only call `export_pdf`
when the user explicitly asks for a PDF copy or when the brief
clearly implies distribution outside PowerPoint (external share,
email attachment, audience without Office, "I'll send it around",
publication). If you're unsure, skip the export — the user can
ask for the PDF afterwards with a one-line request.

---

## i18n labels

For headers / footers / repeated micro-text. Extend the dict as
your decks accumulate idioms.

```python
I18N = {
    "en": {
        "agenda":      "Agenda",
        "section":     "Section",
        "conclusions": "Conclusions",
        "thanks":      "Thank you",
        "notes":       "Notes",
        "slide_of":    "Slide {current} of {total}",
    },
    "es": {
        "agenda":      "Agenda",
        "section":     "Sección",
        "conclusions": "Conclusiones",
        "thanks":      "Gracias",
        "notes":       "Notas",
        "slide_of":    "Diapositiva {current} de {total}",
    },
}

def L(lang: str, key: str, **fmt) -> str:
    text = I18N.get(lang, I18N["en"]).get(key, key)
    return text.format(**fmt) if fmt else text
```
