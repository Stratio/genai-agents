# docx-writer — Referencia

Patrones avanzados que extienden las primitivas de `DOCXBuilder`. Se cargan bajo demanda; no hace falta nada de esto para la creación estándar de documentos.

## Acceso al Document subyacente de `python-docx`

Todo lo que hace `DOCXBuilder` es azúcar fina sobre `python-docx`. Cuando necesites una salida de emergencia (inyección de XML personalizado, o una primitiva de layout que el builder no cubra), léelo directamente:

```python
b = DOCXBuilder()
doc = b.document              # Document de python-docx
section = doc.sections[0]
# cualquier operación de python-docx funciona aquí
```

## Índice (TOC)

DOCX usa un campo (field) para la generación automática de TOC. Los encabezados de un documento construido con `DOCXBuilder` ya llevan el `outlineLevel` correcto (0 para H1, 1 para H2, 2 para H3), así que un campo TOC los recoge al abrir:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def add_toc_field(paragraph):
    run = paragraph.add_run()
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_char_separate = OxmlElement("w:fldChar")
    fld_char_separate.set(qn("w:fldCharType"), "separate")
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char_begin)
    run._r.append(instr)
    run._r.append(fld_char_separate)
    run._r.append(fld_char_end)

toc_para = b.document.add_paragraph()
add_toc_field(toc_para)
b.add_page_break()
```

Word pide al usuario actualizar el TOC al abrir (o lo auto-actualiza según la configuración). Los TOCs generados están vacíos hasta que el lector acepta la actualización.

## Cabeceras personalizadas

El helper `set_footer_page_numbers` configura un pie centrado sencillo. Para una cabecera con logo + título:

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

section = b.document.sections[0]
header = section.header
para = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
para.alignment = WD_ALIGN_PARAGRAPH.LEFT
run = para.add_run()
run.add_picture("assets/logo.png", width=Inches(1.2))
run = para.add_run("    Política de retención — Confidencial")
run.bold = True
```

## Embedding de fuentes

Word 2016+ en Windows / macOS honra fuentes embebidas en `word/fontTable.xml`. El flujo:

1. Construye el DOCX normalmente con tus fuentes de display y cuerpo referenciadas por nombre.
2. Descomprime el DOCX producido.
3. Añade los ficheros TTF a un directorio `word/fonts/` dentro del ZIP.
4. Edita `word/fontTable.xml` para que cada familia embebida tenga `<w:embedRegular r:id="..."/>` (y variantes bold / italic cuando aplique) apuntando a los ficheros empaquetados.
5. Registra las relaciones dentro de `word/_rels/fontTable.xml.rels`.
6. Recomprime el ZIP.

LibreOffice y Word Online ignoran estos embeddings (sustituyen por la mejor coincidencia del sistema), así que el embedding es sobre todo para entregas pixel-exactas en Windows / macOS.

## Documentos multi-sección

Un único DOCX puede tener varias secciones con tamaños, orientaciones y cabeceras independientes. Útil para documentos donde una tabla apaisada se inserta en un informe mayormente en retrato:

```python
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.shared import Cm

b.add_paragraph("Contenido en retrato...")
new_section = b.document.add_section(WD_SECTION.NEW_PAGE)
new_section.orientation = WD_ORIENT.LANDSCAPE
new_section.page_width = Cm(29.7)
new_section.page_height = Cm(21.0)
b.add_heading("Sección de tabla ancha", level=1)
b.add_table(headers=[...], rows=[...])
# Vuelve a retrato para el resto si lo necesitas
third = b.document.add_section(WD_SECTION.NEW_PAGE)
third.orientation = WD_ORIENT.PORTRAIT
third.page_width = Cm(21.0)
third.page_height = Cm(29.7)
```

## Encabezados numerados ("1.", "1.1", ...)

Por defecto, los estilos H1–H3 de Word no llevan numeración. Para obtener "1. Alcance", "1.1 Subalcance" necesitas una definición de numeración:

```python
# En numbering.xml: define un abstractNum con numeración multinivel,
# luego enlázalo a Heading 1 / Heading 2 / Heading 3 mediante referencias pStyle.
```

Como esto requiere editar `numbering.xml` (que `python-docx` expone vía oxml de bajo nivel), es más fácil confeccionar una numeración abstracta una vez, escribirla en un DOCX plantilla, y abrir la plantilla como documento inicial:

```python
from docx import Document as _Document

template = _Document("shared-skills/docx-writer/templates/encabezados_numerados.docx")
```

(No hay plantilla empaquetada en Fase 1. Si la necesitas, créala una vez, versiónala en las `skills/` locales del agente y cárgala desde ahí.)

## Comentarios y cambios rastreados

Fuera del alcance de esta skill en Fase 1. Modifica con cuidado a nivel XML si lo necesitas, o usa Word / LibreOffice para insertarlos a posteriori.

## Trabajar desde un DOCX existente como punto de partida

Para los casos en los que "generar un DOCX" realmente significa "rellenar una plantilla corporativa":

```python
from docx import Document as _Document

template = _Document("templates/membrete_corporativo.docx")
# Insertar contenido en el documento existente
template.add_heading("Asunto: actualización de política", level=1)
template.add_paragraph("Estimado destinatario, ...")
template.save("output/carta.docx")
```

En ese caso el valor de `DOCXBuilder` es sobre todo la capa de primitivas estilizadas; adáptalo construyendo en un documento temporal y copiando sus elementos de cuerpo dentro de tu plantilla. Alternativa: construye con `DOCXBuilder`, luego usa `find_replace_docx` sobre un placeholder estilo plantilla (`{{nombre_destinatario}}`) para rellenar valores.

## Rondas de validación

Regenera e inspecciona en bucle corto al iterar diseño:

```python
# bucle: ajusta aesthetic, regenera, mira páginas
b = DOCXBuilder(aesthetic_direction={"tone": "corporate",
                                     "font_pair": ["Instrument Serif", "Crimson Pro"]})
# ... construye ...
b.save("iter_1.docx")
# shell: visual_validate.py iter_1.docx --out /tmp/preview_1 --dpi 100
# Inspecciona el PNG, ajusta palette_override, repite.
```

Mantén el DPI a 100 durante la iteración (rasterización más rápida) y súbelo a 150–200 solo para el preview final.

## Generación por lotes

Para generar N documentos a partir de un dataset:

```python
from pathlib import Path

out_dir = Path("output/cartas")
out_dir.mkdir(parents=True, exist_ok=True)

for row in rows:  # iterable de dicts
    b = DOCXBuilder(aesthetic_direction={"tone": "corporate"})
    b.add_cover(title=row["title"], subtitle=row["subtitle"],
                author=row["author"])
    b.add_paragraph(row["body"])
    b.save(out_dir / f"{row['id']}.docx")
```

Cada DOCXBuilder es independiente; construirlos en bucle es barato (~20 ms por documento simple en hardware estándar).
