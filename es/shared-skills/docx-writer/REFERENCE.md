# docx-writer — REFERENCE

Snippets copy-paste para los bloques de documento y operaciones que
`SKILL.md` referencia pero no deletrea inline. Carga este archivo
cuando vayas a construir algo más allá de un documento
encabezado+párrafo básico.

Todos los snippets asumen el dict `DESIGN` y el helper `hex_to_rgb`
del scaffold en `SKILL.md` §4.

---

## Guía de paleta

Esta skill no incluye un catálogo de paletas. El contrato canónico de
tokens — `primary`, `ink`, `muted`, `rule`, `bg`, `bg_alt`, `accent`,
`state_ok` / `state_warn` / `state_danger`, más `display` / `body` /
`mono` — se comparte entre las skills de output.

- Para temas predefinidos (un catálogo curado de tokens listos para
  volcar a `DESIGN`), consulta la skill de brand-kit / theming
  centralizada del agente si está incluida.
- Para improvisación ad-hoc contra los roles de paleta tonal
  (editorial-serious, technical-minimal, warm-magazine, etc.),
  consulta `skills-guides/visual-craftsmanship.md`.

Cualquiera que sea la fuente, resuelve el set de tokens aguas arriba
y hazlo merge en `DESIGN` al principio del scaffold:

```python
# `theme_tokens` viene de la skill de theming o de improvisación
DESIGN.update(theme_tokens)
```

---

## Portada

```python
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


def add_cover(doc, title, subtitle=None, metadata=None):
    # Regla de acento fina sobre la portada.
    rule = doc.add_paragraph()
    pPr = rule._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "24")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), DESIGN["primary"].lstrip("#"))
    pBdr.append(bottom)
    pPr.append(pBdr)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(60)
    run = p.add_run(title)
    run.font.name = DESIGN["display"]
    run.font.size = Pt(DESIGN["size_h1"] + 12)
    run.font.bold = True
    run.font.color.rgb = hex_to_rgb(DESIGN["primary"])

    if subtitle:
        p = doc.add_paragraph()
        run = p.add_run(subtitle)
        run.font.name = DESIGN["body"]
        run.font.size = Pt(DESIGN["size_h2"])
        run.font.color.rgb = hex_to_rgb(DESIGN["muted"])

    if metadata:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(36)
        for key, value in metadata.items():
            k_run = p.add_run(f"{key}: ")
            k_run.bold = True
            k_run.font.size = Pt(DESIGN["size_small"])
            v_run = p.add_run(f"{value}    ")
            v_run.font.size = Pt(DESIGN["size_small"])

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
```

---

## Tabla con override de estilo

Sobrescribe el estilo pastel por defecto de Microsoft: cabecera
primary, sin reglas verticales, bandas alternas en cuerpo, filas
`cantSplit`, cabecera repetida en salto de página, rellenos
`w:shd w:val="clear"` seguros.

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


def _set_cell_shading(cell, hex_color: str) -> None:
    """Aplica fondo a una celda usando val='clear'."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")         # NUNCA "solid"
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    tc_pr.append(shd)


def _set_cell_borders(cell, *, bottom: str | None = None,
                      sides: str = "none") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = OxmlElement("w:tcBorders")
    for edge in ("top", "start", "end"):
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), sides)
        tc_borders.append(border)
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single" if bottom else "none")
    bot.set(qn("w:sz"), "4")
    bot.set(qn("w:color"), (bottom or "FFFFFF").lstrip("#"))
    tc_borders.append(bot)
    tc_pr.append(tc_borders)


def _mark_repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    tr_pr.append(header)
    cant = OxmlElement("w:cantSplit")
    tr_pr.append(cant)


def add_styled_table(doc, headers, rows, *, caption: str | None = None,
                    numeric_cols: set[int] | None = None):
    numeric_cols = numeric_cols or set()
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))

    # Fila cabecera.
    header_row = table.rows[0]
    _mark_repeat_header(header_row)
    for i, text in enumerate(headers):
        cell = header_row.cells[i]
        _set_cell_shading(cell, DESIGN["primary"])
        _set_cell_borders(cell)
        para = cell.paragraphs[0]
        para.alignment = (
            WD_ALIGN_PARAGRAPH.RIGHT if i in numeric_cols else WD_ALIGN_PARAGRAPH.LEFT
        )
        run = para.add_run(text)
        run.bold = True
        run.font.color.rgb = hex_to_rgb("#ffffff")
        run.font.size = Pt(DESIGN["size_body"])
        run.font.name = DESIGN["body"]

    # Filas cuerpo — bandas alternas, regla inferior sutil.
    for r_idx, row_data in enumerate(rows):
        body_row = table.rows[r_idx + 1]
        cant = OxmlElement("w:cantSplit")
        body_row._tr.get_or_add_trPr().append(cant)
        for c_idx, text in enumerate(row_data):
            cell = body_row.cells[c_idx]
            if r_idx % 2 == 0:
                _set_cell_shading(cell, DESIGN["bg_alt"])
            _set_cell_borders(cell, bottom=DESIGN["rule"])
            para = cell.paragraphs[0]
            para.alignment = (
                WD_ALIGN_PARAGRAPH.RIGHT if c_idx in numeric_cols else WD_ALIGN_PARAGRAPH.LEFT
            )
            run = para.add_run(str(text))
            run.font.size = Pt(DESIGN["size_body"])
            run.font.name = DESIGN["body"]
            run.font.color.rgb = hex_to_rgb(DESIGN["ink"])

    if caption:
        cap = doc.add_paragraph(caption, style="Caption")
        for run in cap.runs:
            run.font.size = Pt(DESIGN["size_small"])
            run.font.color.rgb = hex_to_rgb(DESIGN["muted"])

    return table
```

---

## Figura con pie

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm


def add_figure(doc, image_path, caption: str | None = None,
               width_cm: float = 14.0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Empareja figura + pie con keep_with_next.
    pPr = p._p.get_or_add_pPr()
    keep = OxmlElement("w:keepNext")
    pPr.append(keep)

    run = p.add_run()
    run.add_picture(str(image_path), width=Cm(width_cm))

    if caption:
        cap = doc.add_paragraph(caption, style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cap.runs:
            run.font.size = Pt(DESIGN["size_small"])
            run.font.color.rgb = hex_to_rgb(DESIGN["muted"])
            run.italic = True
```

---

## Callout

Párrafo sombreado con regla lateral izquierda de acento. Tipos:
`info` (primary), `warning`, `danger`, `success`.

```python
CALLOUT_COLORS = {
    "info":    "primary",
    "warning": "state_warn",
    "danger":  "state_danger",
    "success": "state_ok",
}


def add_callout(doc, text: str, kind: str = "info"):
    colour_key = CALLOUT_COLORS.get(kind, "primary")
    hex_colour = DESIGN[colour_key]
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()

    # Borde izquierdo (regla gruesa de acento).
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "6")
    left.set(qn("w:color"), hex_colour.lstrip("#"))
    pBdr.append(left)
    pPr.append(pBdr)

    # Fondo sombreado.
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), DESIGN["bg_alt"].lstrip("#"))
    pPr.append(shd)

    # Sangría para que el texto no toque la regla.
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "300")
    ind.set(qn("w:right"), "100")
    pPr.append(ind)

    run = p.add_run(text)
    run.font.size = Pt(DESIGN["size_body"])
    run.font.color.rgb = hex_to_rgb(DESIGN["ink"])
    run.font.name = DESIGN["body"]
```

---

## Bloque de código

Monoespaciado, fondo suave, preserva whitespace (importante: DOCX
colapsa whitespace inicial salvo que se ponga `xml:space="preserve"`
en cada `<w:t>` — `add_run` lo hace automáticamente para strings que
empiezan con whitespace, pero solo si el string entero sobrevive como
un único run).

```python
def add_code_block(doc, text: str, language: str | None = None):
    lines = text.split("\n")
    for line in lines:
        p = doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        # Fondo sombreado.
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), DESIGN["bg_alt"].lstrip("#"))
        pPr.append(shd)
        # Espaciado apretado entre líneas de código.
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:before"), "20")
        spacing.set(qn("w:after"), "20")
        pPr.append(spacing)
        run = p.add_run(line or " ")
        run.font.name = DESIGN["mono"]
        run.font.size = Pt(DESIGN["size_small"] + 1)
        run.font.color.rgb = hex_to_rgb(DESIGN["ink"])
```

---

## Listas

Usa los estilos nativos de Word para numeración / viñetas. **Nunca**
pegues viñetas Unicode (`•`) — no sobreviven round-trips a Google
Docs / Office Web.

```python
for item in ["Primer punto", "Segundo punto", "Tercer punto"]:
    doc.add_paragraph(item, style="List Bullet")

for item in ["Paso uno", "Paso dos", "Paso tres"]:
    doc.add_paragraph(item, style="List Number")
```

Para una viñeta anidada, ajusta el nivel del formato del párrafo
manualmente:

```python
p = doc.add_paragraph("Viñeta anidada", style="List Bullet")
p.paragraph_format.left_indent = Cm(1.5)
```

---

## Regla horizontal

Borde inferior a nivel de párrafo. **No** uses una tabla de una fila
como regla — las celdas tienen alto mínimo y renderizan visibles.

```python
def add_horizontal_rule(doc, colour_hex: str | None = None):
    colour_hex = (colour_hex or DESIGN["rule"]).lstrip("#")
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single")
    bot.set(qn("w:sz"), "6")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), colour_hex)
    pBdr.append(bot)
    pPr.append(pBdr)
```

---

## Cabeceras, pies, números de página

### Número de página centrado en pie

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH


def add_footer_page_number(doc, labels: dict | None = None):
    labels = labels or {"page": "Página", "of": "de"}
    section = doc.sections[0]
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _field(instr: str):
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        instr_el = OxmlElement("w:instrText")
        instr_el.text = instr
        fld_sep = OxmlElement("w:fldChar")
        fld_sep.set(qn("w:fldCharType"), "separate")
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        return fld_begin, instr_el, fld_sep, fld_end

    run = p.add_run(f"{labels['page']} ")
    run.font.size = Pt(DESIGN["size_small"])
    run = p.add_run()
    for el in _field("PAGE"):
        run._r.append(el)
    run.font.size = Pt(DESIGN["size_small"])

    run = p.add_run(f" {labels['of']} ")
    run.font.size = Pt(DESIGN["size_small"])
    run = p.add_run()
    for el in _field("NUMPAGES"):
        run._r.append(el)
    run.font.size = Pt(DESIGN["size_small"])
```

### Logo + título en cabecera

```python
from docx.shared import Inches


section = doc.sections[0]
header = section.header
p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
run = p.add_run()
run.add_picture("assets/logo.png", width=Inches(1.2))
run = p.add_run("    Política de Retención — Confidencial")
run.bold = True
run.font.size = Pt(DESIGN["size_small"])
run.font.color.rgb = hex_to_rgb(DESIGN["muted"])
```

### Saltar chrome en la portada

```python
section = doc.sections[0]
section.different_first_page_header_footer = True
# Ahora section.first_page_header / section.first_page_footer existen
# y están vacíos por defecto — que es lo que quieres en la portada.
```

---

## Tabla de contenidos

Inserta un campo TOC; Word lo rellena al abrir.

```python
def add_toc(doc):
    toc_para = doc.add_paragraph()
    run = toc_para.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
```

Los encabezados construidos con `doc.add_heading(text, level=N)`
sobre un estilo incorporado redefinido llevan el `outlineLevel`
correcto, así que el TOC los recoge automáticamente. Word pide al
usuario que actualice los campos al abrir (o autoactualiza según
configuración).

---

## Documentos multi-sección (vertical / apaisado mezclado)

```python
from docx.enum.section import WD_SECTION, WD_ORIENT

portrait = doc.sections[0]
# ... contenido vertical ...

landscape = doc.add_section(WD_SECTION.NEW_PAGE)
landscape.orientation = WD_ORIENT.LANDSCAPE
landscape.page_width = Cm(29.7)
landscape.page_height = Cm(21.0)
landscape.left_margin = landscape.right_margin = Cm(2.0)
doc.add_heading("Tabla ancha", level=1)
# ... contenido de tabla ...

# Volver a vertical.
third = doc.add_section(WD_SECTION.NEW_PAGE)
third.orientation = WD_ORIENT.PORTRAIT
third.page_width = Cm(21.0)
third.page_height = Cm(29.7)
```

Cada nueva sección tiene sus propias cabeceras / pies por defecto. Si
quieres heredarlos de la sección anterior, pon
`is_linked_to_previous = True` en la cabecera / pie de la sección.

---

## Encabezados numerados (`1.`, `1.1`, `1.1.1`)

Por defecto los estilos H1–H3 de Word no tienen numeración. La
numeración multinivel automática requiere editar `numbering.xml`,
que `python-docx` expone solo vía oxml de bajo nivel. La vía pragmática:

1. Crea una vez una plantilla DOCX con la numeración deseada (más
   fácil en el propio Word o editando `numbering.xml` directamente).
2. Carga esa plantilla como documento de arranque.
3. Cada `Heading 1` / `Heading 2` / `Heading 3` que añadas hereda la
   numeración.

```python
from docx import Document

doc = Document("templates/headings_numerados.docx")
# doc.add_heading(...) producirá entradas numeradas.
```

Si necesitas crear la definición de numeración desde cero en Python,
el patrón es inyectar un `<w:abstractNum>` en
`doc.part.numbering_part.element` y vincular los estilos H1–H3 vía
`<w:numPr><w:numId w:val="..."/></w:numPr>`. Queda reservado para
casos raros — prefiere la vía de plantilla.

---

## Embedding de fuentes

Word 2016+ en Windows / macOS honra fuentes embebidas dentro de
`word/fontTable.xml`. El procedimiento:

1. Construye el DOCX normalmente con tus fuentes display y body
   referenciadas por nombre.
2. Descomprime el DOCX producido.
3. Añade los archivos TTF dentro de un nuevo directorio
   `word/fonts/` dentro del ZIP.
4. Edita `word/fontTable.xml` para que cada fuente embebida tenga
   `<w:embedRegular r:id="..."/>` (más variantes bold / italic según
   aplique) apuntando a los archivos incluidos.
5. Registra las relaciones dentro de
   `word/_rels/fontTable.xml.rels`.
6. Vuelve a comprimir el ZIP.

LibreOffice y Word Online ignoran los embeds silenciosamente —
sustituyen por la mejor coincidencia del sistema. Usa el embedding
solo cuando la entrega esté garantizada en Word 2016+ Windows/macOS.

---

## Trabajar con un DOCX existente como punto de partida

Para casos en que "genera un DOCX" realmente significa "rellena una
plantilla de empresa":

```python
from docx import Document

template = Document("templates/letterhead_empresa.docx")
template.add_heading("Asunto: Actualización de política", level=1)
template.add_paragraph("Estimado/a destinatario/a, …")
template.save("output/carta.docx")
```

Para fill-in-the-blank (`{{destinatario_nombre}}` → nombre real),
construye la plantilla una vez con strings placeholder y luego
ejecuta `find_replace` desde `STRUCTURAL_OPS.md`:

```python
# Ver STRUCTURAL_OPS.md §Find-replace — el snippet lee el DOCX
# fuente, recorre los nodos <w:t>, y escribe un nuevo archivo con
# las sustituciones.
```

---

## Validación estructural

Reabre el DOCX guardado y emite un manifest de lo que realmente
contiene. Detecta corrupción, runs perdidos, secciones faltantes o
invariantes OOXML rotos *antes* de que el archivo se entregue. Corre
en ~100 ms; llámalo inmediatamente después de `doc.save(...)` en cada
build.

```python
import zipfile
from pathlib import Path

from docx import Document
from lxml import etree


def validate_structure(docx_path) -> dict:
    """Reabre el DOCX y emite un manifest estructural."""
    W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"
    SPACE_ATTR = "{http://www.w3.org/XML/1998/namespace}space"
    Q_T = f"{{{W_NS}}}t"
    Q_PIC = f"{{{PIC_NS}}}pic"

    path = Path(docx_path)
    manifest: dict = {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "reopens": False,
    }
    try:
        doc = Document(str(path))
        manifest["reopens"] = True
    except Exception as exc:
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        return manifest

    manifest["paragraphs"] = len(doc.paragraphs)
    manifest["tables"] = len(doc.tables)
    manifest["sections"] = len(doc.sections)

    headings = {"H1": 0, "H2": 0, "H3": 0}
    for p in doc.paragraphs:
        style_name = p.style.name if p.style else ""
        for level in (1, 2, 3):
            if style_name == f"Heading {level}":
                headings[f"H{level}"] += 1
    manifest["headings"] = headings

    # Inspección XML — figuras + invariantes OOXML en una pasada.
    figures = 0
    space_ok = True
    with zipfile.ZipFile(path) as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    for _ in root.iter(Q_PIC):
        figures += 1
    for t in root.iter(Q_T):
        txt = t.text or ""
        if txt != txt.strip() and t.get(SPACE_ATTR) != "preserve":
            space_ok = False
            break
    manifest["figures"] = figures
    manifest["xml_space_preserved"] = space_ok

    return manifest


# Uso
manifest = validate_structure("output/politica_retencion.docx")
print(manifest)
# {"path": "output/politica_retencion.docx", "size_bytes": 42381, "reopens": True,
#  "paragraphs": 12, "tables": 1, "sections": 1,
#  "headings": {"H1": 2, "H2": 1, "H3": 0}, "figures": 0,
#  "xml_space_preserved": True}
```

Qué hacer con el manifest:

- `reopens: False` o `error` presente — el archivo está corrupto.
  Arregla el generador, no lo entregues.
- `xml_space_preserved: False` — un run con whitespace inicial/final
  perdió el atributo `xml:space="preserve"`; el texto colapsará al
  abrir. Arregla la emisión del run (suele estar en rutas tipo
  `find_replace`).
- Conteos de encabezado o sección que no casan con el brief ("pedí 5
  H1, emití 2") — regenera, no entregues.

---

## Pipeline de validación visual

```bash
# 1. Convierte DOCX a PDF con LibreOffice headless.
soffice --headless --convert-to pdf --outdir /tmp/preview output/doc.docx

# 2. Rasteriza un PNG por página con poppler-utils.
pdftoppm -r 150 -png /tmp/preview/doc.pdf /tmp/preview/page
# → /tmp/preview/page-1.png, /tmp/preview/page-2.png, ...
```

Envuélvelo en un helper pequeño cuando iteres:

```python
import subprocess
from pathlib import Path


def visual_validate(docx_path, out_dir, dpi=150):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(out), str(docx_path)],
        check=True,
    )
    pdf = out / (Path(docx_path).stem + ".pdf")
    subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-png",
         str(pdf), str(out / Path(docx_path).stem)],
        check=True,
    )
    return sorted(out.glob(f"{Path(docx_path).stem}-*.png"))
```

Itera: genera → rasteriza a dpi=100 → inspecciona → ajusta tokens →
regenera. Sube a dpi=150–200 solo para el paso final de QA.

---

## Export PDF

One-liner cuando necesites un PDF junto al DOCX. Por defecto,
**solo DOCX**; añade el PDF cuando el usuario lo pida o el brief
implique claramente distribución externa.

```python
import subprocess
from pathlib import Path


def export_pdf(docx_path, out_dir=None):
    out_dir = Path(out_dir or Path(docx_path).parent)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(out_dir), str(docx_path)],
        check=True,
    )
    return out_dir / (Path(docx_path).stem + ".pdf")
```

---

## Labels i18n

Catálogo mínimo de labels para chrome generado (metadatos de portada,
contadores de pie). Extiende según necesites.

```python
LABELS = {
    "en": {
        "cover": {
            "author":       "Author",
            "domain":       "Domain",
            "date":         "Date",
            "version":      "Version",
            "ref":          "Ref",
            "default_title": "Untitled",
        },
        "page": {
            "page_label":    "Page",
            "of_label":      "of",
        },
    },
    "es": {
        "cover": {
            "author":       "Autor",
            "domain":       "Dominio",
            "date":         "Fecha",
            "version":      "Versión",
            "ref":          "Ref",
            "default_title": "Sin título",
        },
        "page": {
            "page_label":    "Página",
            "of_label":      "de",
        },
    },
}


def get_labels(lang: str | None, overrides: dict | None = None) -> dict:
    lang = (lang or "en").lower().split("-")[0]
    base = LABELS.get(lang, LABELS["en"])
    if overrides:
        merged = {k: {**v} for k, v in base.items()}
        for section, values in overrides.items():
            merged.setdefault(section, {}).update(values)
        return merged
    return base
```

Resuelve el idioma desde la locale del invocador; la guía del agente
sobre el idioma del usuario tiene preferencia sobre cualquier
heurística.

---

## Campos SEQ para numeración de figuras / tablas

El campo `SEQ` de Word autonumera figuras, tablas y ecuaciones.

```python
def add_seq_caption(doc, category: str, text: str):
    """Añade un pie tipo 'Figura 3 — <text>'."""
    p = doc.add_paragraph(style="Caption")
    p.add_run(f"{category} ").bold = True

    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.text = f'SEQ {category} \\* ARABIC'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)

    tail = p.add_run(f" — {text}")
    tail.italic = True
    for r in p.runs:
        r.font.size = Pt(DESIGN["size_small"])
        r.font.color.rgb = hex_to_rgb(DESIGN["muted"])
```

Word rellena el contador cuando el usuario abre el archivo (o cuando
se invoca `Actualizar campos`). Llama esto una vez por figura /
tabla.

---

## Content controls (`<w:sdt>`) — inspección read-only

`python-docx` no expone escritura ni relleno de content controls
`<w:sdt>`. Para inspección read-only:

```python
from docx.oxml.ns import qn

for sdt in doc.element.body.iter(qn("w:sdt")):
    tag = sdt.find(qn("w:sdtPr") + "/" + qn("w:tag"))
    content = sdt.find(qn("w:sdtContent"))
    if tag is not None:
        print("Tag:", tag.get(qn("w:val")))
    if content is not None:
        for t in content.iter(qn("w:t")):
            print("  Valor:", t.text)
```

Escribir los cuerpos `<w:sdtContent>` requiere recorrer
`document.xml` a mano y editar los runs in-place preservando el
binding `<w:sdtPr>`. Fuera de alcance de esta skill.

---

## Generación batch

Cada construcción `Document` es barata (~20 ms para una carta simple
en hardware commodity). Para N documentos desde un dataset, itera:

```python
from pathlib import Path

out_dir = Path("output/cartas")
out_dir.mkdir(parents=True, exist_ok=True)

for row in rows:  # iterable de dicts
    doc = Document()
    # ... aplicar estilos DESIGN, add_cover, contenido ...
    doc.save(out_dir / f"{row['id']}.docx")
```

Mantén una función helper por composición (portada, tabla, figura,
callout) a nivel de módulo. Instancia un `Document` fresco por fila
— no hay estado compartido del que preocuparse.

---

## Acceso a los primitivos python-docx subyacentes

Todo lo anterior es azúcar sobre `python-docx`. Cuando necesites una
vía de escape (inyección XML custom, un primitivo de layout no
cubierto aquí), baja:

```python
section = doc.sections[0]
body = doc.element.body
# cualquier operación de python-docx funciona aquí
```

Recorre el árbol XML del part relevante con selectores `lxml` sobre
`qn("w:...")` cuando la API pythonica no cubra lo que necesitas. La
spec OOXML (ECMA-376) es la referencia autoritativa para la semántica
de tags.
