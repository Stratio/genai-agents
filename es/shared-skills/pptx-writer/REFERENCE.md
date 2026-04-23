# pptx-writer — REFERENCE

Snippets copy-paste para las composiciones de slide y operaciones que
`SKILL.md` referencia pero no detalla inline. Carga este fichero
cuando vayas a construir algo más allá del slide básico de
título+bullets.

Todos los snippets asumen los tokens de diseño y helpers de
safe-area del scaffold en `SKILL.md` §3 (`DESIGN`, `hex_to_rgb`,
`MARGIN`, `TITLE_TOP`, `TITLE_H`, `CONTENT_TOP`, `CONTENT_H`,
`CONTENT_W`, `BLANK_LAYOUT`, `add_title`).

---

## Helpers dinámicos de safe-area

Derivados desde `prs.slide_width / slide_height` para que cada
helper funcione tanto si el deck es 16:9, 4:3, widescreen o el
aspect ratio custom corporativo del usuario.

```python
from pptx.util import Inches, Emu

def safe_area(prs, *, has_footer: bool = False):
    """Devuelve un dict con las coordenadas de safe-area en EMU."""
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
    """Devuelve True si un shape en (left, top, width, height) cabe en el area dict."""
    return (
        left >= area["left"]
        and top >= area["top"]
        and left + width <= area["left"] + area["width"]
        and top + height <= area["top"] + area["height"]
    )

def fit_content(target_w, target_h, max_w, max_h):
    """Escala (target_w, target_h) hasta caber en (max_w, max_h) preservando ratio."""
    if target_w <= max_w and target_h <= max_h:
        return target_w, target_h
    ratio = min(max_w / target_w, max_h / target_h)
    return int(target_w * ratio), int(target_h * ratio)
```

---

## Slide de portada

```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

def add_cover(prs, title: str, subtitle: str | None = None,
              author: str | None = None, date: str | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)

    # Centra verticalmente el bloque título/subtítulo
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

    # Barra de acento arriba
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN, title_top - Inches(0.3),
        Inches(2.0), Inches(0.08),
    )
    bar.line.fill.background()
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(DESIGN["accent"])

    # Footer autor / fecha
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

## Slide de agenda

```python
def add_agenda(prs, items: list[str]):
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, "Agenda")  # del scaffold de SKILL.md

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

## Divisor de sección

```python
def add_section_divider(prs, label: str, number: str | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)

    # Nombre de sección grande y centrado
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

## Slide de lista de bullets

```python
def add_bullets(prs, title: str, items: list[str] | list[tuple[int, str]]):
    """
    items: lista de strings (bullets de nivel 0) o lista de tuplas (nivel, texto)
    para bullets anidados. El nivel va 0-4.
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

## Slide de dos columnas

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

## Caja de KPI

```python
def add_kpi_box(slide, left, top, width, height, label: str, value: str,
                unit: str | None = None, bg: str | None = None):
    """Renderiza un tile de KPI con valor grande + etiqueta pequeña debajo."""
    from pptx.enum.text import PP_ALIGN
    bg_hex = bg or DESIGN["bg_alt"]

    # Rectángulo de fondo
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    rect.line.fill.background()
    rect.fill.solid()
    rect.fill.fore_color.rgb = hex_to_rgb(bg_hex)

    # Valor (grande)
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

    # Etiqueta (pequeña, debajo)
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
    """3 o 4 KPIs a lo ancho del área de contenido."""
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

## Tabla con override de estilo

Override agresivo del default pastel de python-pptx. Cabecera con
color primario, filas alternadas, sin líneas verticales, numéricas
alineadas a la derecha.

```python
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.dml.color import RGBColor

def add_table_slide(prs, title: str, headers: list[str], rows: list[list[str]],
                    numeric_cols: list[int] | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    add_title(slide, title)

    numeric_cols = numeric_cols or []
    n_cols = len(headers)
    n_rows = len(rows) + 1  # +1 cabecera
    table_h = min(Inches(0.5) * n_rows, CONTENT_H)

    shape = slide.shapes.add_table(n_rows, n_cols, MARGIN, CONTENT_TOP,
                                   CONTENT_W, table_h)
    table = shape.table

    # Columnas iguales salvo que el llamador las ajuste después
    col_w = CONTENT_W // n_cols
    for col in table.columns:
        col.width = col_w

    # Fila de cabecera
    for c, head in enumerate(headers):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = hex_to_rgb(DESIGN["primary"])
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_top = Inches(0.08)
        cell.margin_bottom = Inches(0.08)
        tf = cell.text_frame
        tf.word_wrap = True
        tf.paragraphs[0].text = ""  # limpia default
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT if c in numeric_cols else PP_ALIGN.LEFT
        r = p.add_run()
        r.text = head
        r.font.name = DESIGN["display"]
        r.font.size = Pt(DESIGN["size_body"] - 2)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Filas de body
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
- `table.columns[c].width = ...` debe usar EMU, no Pt/Inches directamente salvo que lo envuelvas.
- Las alturas de fila se auto-ajustan según el contenido; si una fila es muy alta, parte el texto o empuja la tabla bajo el check de safe-area.
- Para tablas con > 12 filas, considera dividir en slides con la cabecera repetida.

---

## Imagen con aspect ratio preservado

```python
from PIL import Image

def add_image_safe(slide, image_path: str, area: dict,
                   caption: str | None = None):
    """
    area: dict con 'left', 'top', 'width', 'height' en EMU (desde content_area()).
    Escala la imagen para que encaje, preserva aspect, centra en el area.
    """
    with Image.open(image_path) as img:
        native_w, native_h = img.size
    # Target al DPI nativo de la imagen, escalado a EMU
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
    # Centra
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
    """layout: 'full' | 'left' | 'right' — 'full' usa toda el área de contenido."""
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

## Imagen con texto (layout hero)

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

## Chart OOXML nativo — bar / column / line / pie / area

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

    # Aplica colores de marca a las series en orden
    palette = [DESIGN["primary"], DESIGN["accent"], DESIGN["muted"]]
    for i, ser in enumerate(chart.plots[0].series):
        fill = ser.format.fill
        fill.solid()
        fill.fore_color.rgb = hex_to_rgb(palette[i % len(palette)])

    return slide
```

Para charts **scatter**, **bubble** y **radar** la forma de los datos
difiere:

```python
# Scatter: XyChartData con tuplas (x, y) por punto
xy_data = XyChartData()
ser = xy_data.add_series("Correlación")
for x, y in [(1, 2), (2, 3.5), (3, 5), (4, 4.8)]:
    ser.add_data_point(x, y)

# Para bubble, usa BubbleChartData con triples (x, y, size).
# Radar usa CategoryChartData igual que column/line pero con XL_CHART_TYPE.RADAR.
```

Cuando el tipo sea **waterfall / sunburst / sankey / combo** o
cualquier otro que python-pptx no cubra, renderiza en matplotlib/
plotly con `dpi=200, facecolor="none"` y usa `add_image_slide`.

---

## Slide de cita

```python
def add_quote_slide(prs, quote: str, author: str, role: str | None = None):
    slide = prs.slides.add_slide(BLANK_LAYOUT)
    ca = content_area(prs)

    # Comilla grande de apertura
    mark = slide.shapes.add_textbox(
        MARGIN, ca["top"], Inches(1), Inches(1),
    )
    pr = mark.text_frame.paragraphs[0]
    rr = pr.add_run()
    rr.text = "\u201c"
    rr.font.name = DESIGN["display"]
    rr.font.size = Pt(120)
    rr.font.color.rgb = hex_to_rgb(DESIGN["accent"])

    # Cuerpo de la cita
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

    # Atribución
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

## Slide de conclusión

```python
def add_conclusion(prs, title: str, bullets: list[str]):
    return add_bullets(prs, title, bullets)
```

(Intencional: la conclusión es estructuralmente un slide de bullets
con un título más fuerte. Anula `title` con "Conclusiones" /
"Siguientes pasos" / "Llamada a la acción" según aplique.)

---

## Usando una plantilla de cliente (`.potx` / `.pptx`)

```python
from pptx import Presentation

def build_from_template(template_path: str, out_path: str):
    prs = Presentation(template_path)

    # Inspecciona una vez para descubrir qué layouts trae la plantilla
    # (nómbralos en los comentarios para que tu yo futuro no tenga que re-descubrir).
    # for i, layout in enumerate(prs.slide_layouts):
    #     print(i, layout.name)

    # Ejemplo: la plantilla trae Cover / Section / Content en 0 / 1 / 2.
    COVER = prs.slide_layouts[0]
    SECTION = prs.slide_layouts[1]
    CONTENT = prs.slide_layouts[2]

    # Portada
    cover = prs.slides.add_slide(COVER)
    cover.placeholders[0].text = "Título del deck"
    if len(cover.placeholders) > 1:
        cover.placeholders[1].text = "Subtítulo / fecha / autor"

    # Divisor de sección
    sec = prs.slides.add_slide(SECTION)
    sec.placeholders[0].text = "01  Introducción"

    # Contenido con bullets
    content = prs.slides.add_slide(CONTENT)
    content.placeholders[0].text = "Heading de slide"
    body = content.placeholders[1]
    tf = body.text_frame
    tf.text = "Primer bullet"
    for text in ("Segundo bullet", "Tercer bullet"):
        p = tf.add_paragraph()
        p.text = text

    prs.save(out_path)
```

Reglas al usar plantilla de cliente:
- No cambies el master; lleva la marca.
- No uses `slide_layouts[6]` (Blank); usa los layouts con nombre.
- Sí usa `placeholders` antes que `add_textbox`; la plantilla los posicionó.
- Sigue forzando `tf.word_wrap = True` si reemplazas el contenido de un text frame completo.
- Sigue validando visualmente (ver abajo).

---

## Pipeline de validación visual

Tras construir, renderiza cada slide a PNG e inspecciónalo. Detecta
overflow, contraste awkward, glitches de espaciado que la vista XML
no aflora.

```python
import shutil, subprocess, tempfile
from pathlib import Path

def validate_visual(pptx_path: str, out_dir: str, dpi: int = 150) -> list[Path]:
    if shutil.which("soffice") is None:
        raise RuntimeError("Instala libreoffice para el preview visual.")
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("Instala poppler-utils para el preview visual.")
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

Itera: si un PNG muestra overflow o una imagen rota, regenera el
slide ofensor. 2–3 iteraciones antes de una entrega final es normal,
no excesivo.

---

## Export PDF

```python
import shutil, subprocess
from pathlib import Path

def export_pdf(pptx_path: str, out_dir: str) -> Path:
    if shutil.which("soffice") is None:
        raise RuntimeError("Instala libreoffice para exportar a PDF.")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(out), pptx_path],
        check=True, capture_output=True,
    )
    pdf = out / (Path(pptx_path).stem + ".pdf")
    if not pdf.exists():
        raise RuntimeError(f"soffice no produjo PDF para {pptx_path}")
    return pdf
```

El entregable por defecto es solo el PPTX. Llama a `export_pdf`
únicamente cuando el usuario pida explícitamente una copia en PDF
o cuando el brief implique distribución fuera de PowerPoint
(compartir en externo, adjunto de email, audiencia sin Office,
"lo mando por ahí", publicación). Si tienes dudas, no generes el
PDF — el usuario siempre puede pedirlo después con una frase.

---

## Etiquetas i18n

Para headers / footers / micro-texto repetido. Extiende el dict
según tus decks acumulen modismos.

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
