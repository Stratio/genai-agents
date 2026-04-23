---
name: docx-writer
description: "Crea documentos Word (.docx) con diseño intencional y realiza operaciones estructurales sobre los existentes. Usa esta skill siempre que necesites producir un documento Word pulido (carta, memo, contrato, nota de política, whitepaper, newsletter, manual, informe multipágina) o manipular DOCX existentes (fusionar, dividir, buscar-y-reemplazar, convertir .doc heredados, renderizar una previsualización visual). Esta skill se toma el diseño en serio — cada documento que produce tiene tipografía, color y ritmo intencionales, nunca el Calibri-por-defecto genérico. NO la uses para: salidas data-heavy o single-visual (pdf-writer / canvas-craft), web interactiva (web-craft), ni informes analíticos generados dentro de /analyze (que tiene su propio DOCXGenerator). Para patrones avanzados (TOC, embedding de fuentes, multi-sección, títulos numerados, batch), carga REFERENCE.md. Para merge / split / find-replace / conversión .doc heredada, carga STRUCTURAL_OPS.md."
argument-hint: "[tipo o descripción del documento]"
---

# Skill: DOCX Writer

Word es la superficie que la mayoría de destinatarios abre por defecto.
Un DOCX generado sin atención al diseño parece un accidente de
procesador de texto — Calibri a todos los tamaños, bordes grises
sobre grises, sin jerarquía, el mismo margen de 2,54 cm por los cuatro
lados. Ese es el baseline que esta skill resiste activamente.

Antes de escribir una sola línea de código, comprométete con una
dirección de diseño. El código sirve al diseño, no al revés.

## 1. Flujo design-first

Cada tarea de generación DOCX, sin importar su tamaño, sigue cinco
decisiones:

1. **Clasifica el documento** — ¿a qué categoría pertenece? (Ver la
   taxonomía abajo.) Esto gobierna tamaño de página, márgenes, tono y
   peso aguas abajo.
2. **Elige un tono visual** — editorial-serio, técnico-minimalista,
   cálido-revista, sobrio-legal, corporativo-formal,
   amable-moderno. Elige uno y ejecútalo con confianza. Un documento
   sin compromiso "un poco de todo" es el peor resultado.
3. **Selecciona un par tipográfico** — una fuente de display para
   encabezados y una de cuerpo para prosa. Dos tipografías suele ser
   suficiente. Como DOCX usa las fuentes del sistema del lector salvo
   que las embebas (§4), elige pares que se degraden bien — Calibri /
   Aptos / Arial / Times New Roman / Georgia / Cambria son valores
   universales y seguros.
4. **Define una paleta** — un color de acento dominante (usado en el
   5–15% de la superficie: encabezados, reglas, llamadas de atención),
   un neutro profundo para el cuerpo (rara vez negro puro — `#1f2937`
   es más amable), un neutro claro para bandas de tabla o márgenes, y
   colores de estado (éxito/warning/peligro) con parsimonia. Saturación
   real, no pasteles lavados por defecto.
5. **Fija el ritmo** — márgenes (2,5 cm ISO por defecto; 3 cm para
   editorial generoso; 2 cm para manual de referencia denso),
   espaciado entre párrafos, aire alrededor de encabezados, interlineado.
   Un DOCX apretado se lee como un primer borrador; los blancos
   generosos se leen como el producto final.

Solo entonces abre `python-docx`.

### Taxonomía de documentos y puntos de partida

| Categoría | Tono típico | Tamaño página | Display | Cuerpo | Márgenes |
|---|---|---|---|---|---|
| Nota de política / whitepaper | Editorial-serio | A4 | Crimson Pro / IBM Plex Serif | Crimson Pro / Inter | 2,5 cm |
| Contrato / legal | Sobrio-preciso | A4 / Letter | Libre Baskerville | Libre Baskerville | 2,5 cm |
| Carta / memo | Corporativo-formal | A4 / Letter | Calibri / Aptos | Calibri / Aptos | 2,5 cm |
| Newsletter / briefing interno | Cálido-revista | A4 | Big Shoulders / Lora | Lora / Inter | 2,0 cm |
| Manual / how-to | Técnico-minimalista | A4 / Letter | IBM Plex Sans | IBM Plex Sans | 2,0 cm |
| Informe multipágina | Editorial-serio | A4 | Instrument Serif / Crimson Pro | Crimson Pro / Inter | 2,5 cm |
| Académico / investigación | Académico-sobrio | A4 | Libre Baskerville | Libre Baskerville | 2,5 cm |

Son puntos de partida, no mandatos. Rómpelos cuando el brief lo pida.
El objetivo es **no caer nunca en la plantilla Calibri 11 pt en blanco
por defecto de python-docx**.

### Cuándo esta skill no es la indicada

- **Informes analíticos dentro de `/analyze`** — el agente
  `data-analytics` tiene su propio pipeline DOCX opinionado en
  `skills/analyze/report/tools/docx_generator.py` con un scaffold
  analítico (resumen ejecutivo → metodología → análisis →
  conclusiones). Dentro de la Fase 4 de `/analyze`, usa ese pipeline.
  Esta skill es para documentos fuera del flujo analítico.
- **PDF tipográfico multipágina** (factura, contrato para entregar,
  informe largo de prosa donde la fidelidad importa) — `pdf-writer`
  preserva fuentes y layout exactamente; DOCX no puede igualar esa
  fidelidad una vez el lector abre el archivo en otra máquina.
- **Pieza visual de una página** (póster, portada, certificado,
  flyer de una cara) — `canvas-craft`.
- **Frontend interactivo** — `web-craft`.
- **Informe de cobertura de calidad** — la skill `quality-report`
  tiene un generador de layout fijo afinado para ese contenido.

## 2. Tamaño de página, márgenes, orientación

DOCX soporta A4 (21 × 29,7 cm) y Letter (21,59 × 27,94 cm). Elige
según la geografía de entrega — A4 para la mayor parte del mundo,
Letter para lectores en EEUU. No envíes silenciosamente contenido A4
a una impresora Letter: la última línea de cada página caerá fuera.

El apaisado (landscape) es legítimo para tablas anchas o dashboards
insertados en un documento principalmente vertical. Usa una sección
dedicada (§Documentos multi-sección en `REFERENCE.md`) para que las
páginas apaisadas vivan en su propia sección y las verticales
mantengan su geometría.

Ajusta los márgenes según la intención del documento, no según el
default de python-docx de 2,54 cm (1 pulgada) — esa es una herencia
US-céntrica que rara vez sirve al diseño intencional. Editorial
generoso: 3 cm. ISO por defecto: 2,5 cm. Manual denso: 2 cm.
Newsletter con margen: asimétrico (izquierda 2 cm, derecha 4 cm).

## 3. Una plantilla de arranque apropiada

En lugar de estirar la mano hacia `Document()` y rezar, usa este
scaffold y adáptalo:

```python
from pathlib import Path
from docx import Document
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# 1. Comprométete con los tokens de diseño al principio — no cambian
#    a mitad de documento.
DESIGN = {
    # Paleta (strings hex — convertir a RGBColor en el punto de uso)
    "primary":  "#0a2540",   # azul marino (acento / encabezados)
    "ink":      "#1f2937",   # texto cuerpo (no negro puro)
    "muted":    "#6b7280",   # pies de figura, metadatos
    "rule":     "#d1d5db",   # divisores, reglas inferiores de tabla
    "bg_alt":   "#f3f4f6",   # neutro claro para bandas de tabla
    "state_danger":  "#b91c1c",
    "state_warn":    "#b45309",
    "state_ok":      "#047857",
    # Tipografía
    "display":  "Instrument Serif",  # encabezados; fallback Times
    "body":     "Crimson Pro",       # prosa; fallback Georgia
    "mono":     "JetBrains Mono",    # código; fallback Consolas
    # Tamaños (pt)
    "size_h1":    22,
    "size_h2":    16,
    "size_h3":    13,
    "size_body":  11,
    "size_small":  9,
    # Página
    "page_size":  "A4",              # "A4" o "Letter"
    "margin_cm":  2.5,
}


def hex_to_rgb(h: str) -> RGBColor:
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# 2. Construye el documento y ajusta la geometría de página.
doc = Document()
section = doc.sections[0]
if DESIGN["page_size"] == "A4":
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
else:  # Letter
    section.page_width = Cm(21.59)
    section.page_height = Cm(27.94)
section.left_margin = section.right_margin = Cm(DESIGN["margin_cm"])
section.top_margin = section.bottom_margin = Cm(DESIGN["margin_cm"])


# 3. Redefine los estilos incorporados para que cada párrafo herede
#    los tokens de diseño. Nunca los renombres: Word busca "Heading 1",
#    "Normal" y "Caption" por sus IDs exactos para TOC e interoperabilidad.
styles = doc.styles
normal = styles["Normal"]
normal.font.name = DESIGN["body"]
normal.font.size = Pt(DESIGN["size_body"])
normal.font.color.rgb = hex_to_rgb(DESIGN["ink"])

for level, size_key in [(1, "size_h1"), (2, "size_h2"), (3, "size_h3")]:
    h = styles[f"Heading {level}"]
    h.font.name = DESIGN["display"]
    h.font.size = Pt(DESIGN[size_key])
    h.font.bold = True
    h.font.color.rgb = hex_to_rgb(DESIGN["primary"])


# 4. Helpers pequeños para las composiciones que repetirás.
def add_cover(doc, title: str, subtitle: str | None = None,
              metadata: dict | None = None) -> None:
    # Regla de acento sobre el título.
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
            run = p.add_run(f"{key}: ")
            run.bold = True
            run.font.size = Pt(DESIGN["size_small"])
            run = p.add_run(f"{value}    ")
            run.font.size = Pt(DESIGN["size_small"])

    # Fuerza un salto de página tras la portada.
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# 5. Compón el documento.
add_cover(
    doc,
    title="Política de Retención de Datos",
    subtitle="Gobernando registros de cliente bajo el marco 2026",
    metadata={"Ref": "POL-042", "Versión": "1.0", "Autor": "Equipo Compliance"},
)

doc.add_heading("Alcance", level=1)
doc.add_paragraph(
    "Este documento define cómo los registros de cliente se retienen, "
    "archivan y eliminan a través de los dominios de datos gobernados."
)

doc.add_heading("Dimensiones", level=2)
# Tablas, callouts, figuras: ver REFERENCE.md para snippets listos
# para adaptar.

out_path = Path("output/politica_retencion.docx")
out_path.parent.mkdir(parents=True, exist_ok=True)
doc.save(out_path)
```

Cuatro reglas que el scaffold refuerza:

- **Redefine siempre los estilos `Normal`, `Heading 1–3` y `Caption`
  por ID.** No inventes nombres de estilo nuevos — el TOC de Word, el
  tooling de accesibilidad y los round-trips a Google Docs /
  LibreOffice buscan los IDs exactos.
- **Fija siempre la geometría de página explícitamente.** python-docx
  asume Letter con márgenes de 1 pulgada — raramente lo que quieres.
- **Deriva tamaños y colores desde los tokens de diseño**, nunca
  literales inline a mitad de documento. Si cambia el color de
  acento, solo cambia `DESIGN`.
- **Compón con primitivos + helpers pequeños.** Extrae un helper
  local al módulo en cuanto repitas un patrón tres veces; no construyas
  una abstracción por adelantado.

## 4. Fuentes

DOCX usa las fuentes instaladas en el lector salvo que las embebas
dentro de `word/fontTable.xml`. Consecuencias:

- **Camino por defecto**: usa tipografías instaladas de forma amplia
  (Calibri, Aptos, Arial, Times New Roman, Georgia, Cambria, Courier
  New). Funciona en todas partes sin pasos extra.
- **Camino embedding**: elige cualquier display o cuerpo OFL y
  embébela con el procedimiento en `REFERENCE.md` §Embedding de
  fuentes. El tamaño del archivo crece 80–150 KB por familia. Solo
  honrado plenamente por Word 2016+ en Windows/macOS; LibreOffice y
  Word Online sustituyen silenciosamente.

Recomendación: quédate en los valores seguros salvo que el documento
solo se vaya a abrir en Word 2016+ Windows/macOS. Informa al usuario
si el par elegido requiere una fuente no estándar.

## 5. Guía de paleta

Un documento diseñado tiene como mucho tres familias de color en
cualquier página: primary (un color de acento, saturado, usado en
el 5–15% de la superficie: encabezados, fondo de cabecera de tabla,
reglas de acento), neutral (texto cuerpo y fondos), y colores de
estado (éxito/warning/peligro) usados con parsimonia en llamadas de
atención.

Cuando te inventes una paleta, elige valores hex concretos al inicio
y respétalos. No mezcles dos azules distintos, dos rojos distintos o
dos saturaciones distintas del mismo acento en el mismo documento.
Si el brief sugiere un tono ("corporativo" / "editorial" / "legal"),
elige valores que vendan ese tono — el azul marino corporativo es
`#0a2540`, no un azul cielo pastel; académico es un carbón sobrio y
beige cálido, no color saturado en absoluto.

Paletas de referencia para los tonos más comunes viven en
`REFERENCE.md` §Referencia de paleta. Copia una verbatim o úsala
como semilla y ajusta.

## 6. Bloques de documento que compondrás

Estos son los building blocks que vale la pena dominar. Los snippets
de cada uno viven en `REFERENCE.md`; aquí el menú.

- **Portada** — título, subtítulo, metadatos (ref, versión, autor,
  fecha), regla de acento. Salto de página después.
- **Encabezado** (niveles 1–3) — estilado vía los estilos
  incorporados redefinidos. Usa `outlineLevel` para que los TOC
  automáticos los recojan.
- **Párrafo** — prosa cuerpo con alineado justificado o a la izquierda,
  negrita / cursiva / código inline.
- **Tabla** — fila de cabecera sombreada, bandas alternas en cuerpo,
  sin reglas verticales, `cantSplit` por fila para que no se rompan a
  mitad de página.
- **Figura** — imagen centrada con `keep_with_next` para que el pie
  nunca quede huérfano en la página siguiente.
- **Callout** — caja sombreada con un bloque corto de texto;
  variantes `info`, `warning`, `success`, `danger` tintan la regla
  izquierda.
- **Lista** — numeración nativa de Word para ordenadas, viñetas
  nativas para no ordenadas. Nunca insertes `•` manualmente.
- **Bloque de código** — monoespaciado, fondo suave, preserva
  whitespace.
- **Regla horizontal** — borde inferior a nivel de párrafo, no una
  tabla vacía.
- **Salto de página** — `<w:br w:type="page"/>` explícito dentro de
  un párrafo.

## 7. Tablas

Una tabla DOCX sin decisiones de diseño se lee como un pantallazo de
hoja de cálculo. **Sobrescribe siempre el estilo por defecto.** El
override base, en palabras:

- Fila de cabecera: rellena con el color primary, texto blanco,
  negrita, cuerpo o display a 10 pt, alineada a la izquierda para
  columnas de prosa y a la derecha para columnas numéricas.
- Filas de cuerpo: sin reglas verticales, una regla horizontal sutil
  entre filas usando el color `rule`, banda alterna (`bg_alt` en
  filas pares) para legibilidad a golpe de vista.
- Alto de fila: ligeramente generoso (2–3 mm de padding interno);
  filas apretadas se leen como exports de primer borrador de Excel.
- `cantSplit="true"` en cada fila para que no se rompan a mitad de
  página.
- `<w:tblHeader/>` en la fila de cabecera para que se repita en salto
  de página.
- `<w:shd w:val="clear">` para los rellenos de celda — **nunca**
  `solid`, que renderiza como negro en algunos visores (el famoso bug
  "¿por qué mi celda está en negro?").

Snippet completo en `REFERENCE.md` §Tabla con override de estilo;
cópialo literal para cada documento que genere tablas.

## 8. Figuras

Incrustadas vía `doc.add_picture(path, width=Cm(...))`. Dos reglas:

- **Solo PNG.** `python-docx` no acepta SVG. Convierte con `cairosvg`
  o `pillow` antes de llamar a `add_picture`.
- **Empareja figura + pie con `keep_with_next`** para que el pie no
  quede huérfano en la nueva página. Snippet en `REFERENCE.md`
  §Figura con pie.

Para numeración de figuras ("Figura 3 — Curva de cohorte de
retención") usa un contador local al módulo o campos `SEQ` hechos a
mano — ver `REFERENCE.md` §Campos SEQ para numeración.

## 9. Cabeceras, pies, números de página

Todo documento multipágina se beneficia de chrome recorriendo — un
título de cabecera, un contador de página en el pie, ocasionalmente
un logo. El baseline:

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH

section = doc.sections[0]
header = section.header
p = header.paragraphs[0]
p.text = "Política de Retención — Confidencial"
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
for run in p.runs:
    run.font.size = Pt(DESIGN["size_small"])
    run.font.color.rgb = hex_to_rgb(DESIGN["muted"])
```

Para centrado `Página N de M`, y cabeceras de logo+título, ver
`REFERENCE.md` §Cabeceras, pies, números de página.

Salta el chrome en la portada marcando la primera sección
`different_first_page_header_footer = True` y dejando sus párrafos
de cabecera/pie vacíos (snippet también en REFERENCE.md).

## 10. Validación post-build y export a PDF

Después de construir, verifica siempre el resultado. Tres snippets
en `REFERENCE.md`:

- **Validación estructural** (§Validación estructural): reabre el DOCX
  guardado y emite un manifest — páginas, párrafos, tablas, figuras,
  conteo de encabezados por nivel, invariantes OOXML
  (`xml:space="preserve"` en runs con whitespace inicial/final).
  Detecta corrupción, secciones perdidas o invariantes rotos *antes*
  de entregar el archivo. Corre en ~100 ms; hazlo en cada build.
- **Validación visual** (§Pipeline de validación visual): convierte a
  PDF vía LibreOffice y rasteriza PNGs por página con `pdftoppm`.
  Inspecciona cada PNG buscando overflow, contraste raro, espaciado
  apretado, figuras rotas. Regenera y revalida; 2–3 iteraciones es lo
  normal.
- **Export a PDF** (§Export PDF): one-liner vía
  `soffice --headless --convert-to pdf`. El entregable por defecto es
  el DOCX solo. Añade un PDF hermano solo cuando el usuario lo pide
  explícitamente o cuando el brief implica claramente distribución
  fuera de Word (envío externo, attachment de email, audiencia sin
  Office, "lo reparto", publicación). Si dudas, entrega solo el DOCX
  — el usuario puede pedir el PDF después.

La validación visual y el export a PDF requieren `libreoffice` y
`poppler-utils`. La validación estructural solo necesita `python-docx`
y `lxml`.

## 11. Plantillas del usuario

Cuando el usuario aporte una plantilla corporativa — con su logo,
letterhead, estilos y paleta — ignora el scaffold del §3 y carga su
archivo:

```python
from docx import Document

doc = Document("templates/letterhead_empresa.docx")
# Inspecciona los estilos que aporta la plantilla.
for style in doc.styles:
    if style.type is not None:
        print(style.name, style.type)

# Usa los estilos integrados de la plantilla por nombre — no los
# redefinas.
doc.add_heading("Asunto: Actualización de política", level=1)
doc.add_paragraph("Estimado/a destinatario/a, ...")
doc.save("output/carta.docx")
```

Al usar una plantilla del cliente:

- **No redefinas `Normal` ni `Heading 1–3`.** El diseñador de la
  plantilla eligió esas fuentes y colores por una razón.
- **Reutiliza los estilos custom de la plantilla** si existen
  (`Quote`, `Sidebar`, `Signature Block`). Búscalos por nombre.
- **Valida visualmente igual** — una plantilla puede estar
  desactualizada o parcialmente rota; solo lo detectarás
  renderizando e inspeccionando.

Para un patrón fill-in-the-blank (`{{destinatario}}` → nombre real),
ver `REFERENCE.md` §Trabajar con un DOCX existente como punto de
partida.

## 12. Operaciones estructurales

Para manipular documentos existentes (fusionar varios DOCX, dividir
por nivel de encabezado o salto de página, find-replace con regex
sobre cuerpo / cabeceras / pies, convertir binario heredado `.doc` a
`.docx`), ver `STRUCTURAL_OPS.md`. Esos son snippets copy-paste;
ejecútalos desde un script pequeño, no intentes importarlos como
módulo.

## 13. Pitfalls

Contrastado con `python-docx` 1.1 y la spec ECMA-376:

- **Fija el tamaño de página explícitamente.** python-docx asume
  Letter con márgenes de 1 pulgada. A4 ≠ Letter — produce documentos
  para la geografía del destinatario.
- **La paginación es decisión del visor.** No intentes forzar saltos
  pixel-perfect. Usa `cantSplit` en filas atómicas y
  `keep_with_next` / `keep_together` en pares figura + pie.
- **Repite la fila de cabecera en tablas largas** vía
  `<w:tblHeader/>`. Sin eso, los lectores pierden contexto en la
  página dos.
- **Solo PNG para imágenes embebidas.** `python-docx` no acepta SVG.
  Convierte antes con `cairosvg` o `pillow`.
- **No insertes nunca caracteres de viñeta Unicode manualmente**
  (`•`, `\u2022`). Usa `doc.add_paragraph(..., style="List Bullet")`.
  Las viñetas solo sobreviven round-trips a través de la numeración
  nativa de Word.
- **Los saltos de página deben vivir dentro de un párrafo.** Emítelos
  como `paragraph.add_run().add_break(WD_BREAK.PAGE)`.
- **Usa `w:shd w:val="clear"` para rellenos de celda.** `solid`
  renderiza como negro en algunos visores. Esta es la fuente del bug
  "¿por qué mi celda está en negro?".
- **No uses tablas como reglas horizontales.** Las celdas tienen un
  alto mínimo y renderizan como cajas visibles en cabeceras / pies.
  Usa un borde inferior a nivel de párrafo (snippet en REFERENCE.md).
- **Sobrescribe los estilos incorporados de encabezado por sus IDs
  exactos** (`Heading 1`, `Heading 2`, `Heading 3`, `Normal`,
  `Caption`). Nombres custom rompen la generación de TOC.
- **Incluye `outlineLevel`** en cada estilo de encabezado si quieres
  generación automática de TOC. H1 → `outlineLevel="0"`, H2 → `"1"`,
  H3 → `"2"`.
- **Las figuras necesitan `keep_with_next`** para que el pie no quede
  huérfano. Ponlo en el párrafo que contiene la imagen, no en el pie.
- **`xml:space="preserve"` en `<w:t>` con whitespace inicial/final**
  importa cuando usas find-replace en strings que empiezan o
  terminan con espacio; sin él se colapsa.

## 14. Limitaciones conocidas

`python-docx` cubre ~85% de la autoría real de documentos
limpiamente. El 15% restante o necesita manipulación OOXML en crudo
o no está soportado:

- **Comentarios y control de cambios** — no soportados. Insértalos
  con Word o LibreOffice después.
- **Content controls (`<w:sdt>`)** — solo lectura. Rellenar plantillas
  de formulario requiere trabajo a nivel XML; ver REFERENCE.md
  §Content controls para el patrón.
- **Ecuaciones** — no soportadas nativamente. Renderiza como PNG vía
  LaTeX o Mathpix y embebe como figura.
- **Gráficos** — `python-docx` no expone creación de gráficos.
  Renderiza con matplotlib / plotly, exporta a PNG a `dpi=200`, y
  embebe como figura.
- **TOC automático con entradas numeradas y páginas** — el campo TOC
  se inserta correctamente pero Word lo rellena solo cuando el
  usuario abre el archivo (o acepta el diálogo "actualizar campos").
  Muestra al usuario cómo dispararlo.
- **Renderizado de fuente exacta en cualquier máquina** — ver §4.

Documenta la limitación en un apéndice corto o en un callout cuando
afecte al entregable.

## 15. Cheat sheet

| Tarea | Enfoque |
|---|---|
| Crear documento | `Document()` y luego ajustar geometría en `doc.sections[0]` |
| Redefinir estilos incorporados | por ID exacto: `styles["Normal"]`, `"Heading 1"` |
| Portada | ver `REFERENCE.md` §Portada |
| Encabezado | `doc.add_heading(text, level=N)` con estilos predefinidos |
| Párrafo | `doc.add_paragraph(text)` con runs inline para formato |
| Lista viñeta / numerada | `add_paragraph(..., style="List Bullet")` / `"List Number"` |
| Tabla con override | ver `REFERENCE.md` §Tabla con override de estilo |
| Figura con pie | ver `REFERENCE.md` §Figura con pie |
| Callout | ver `REFERENCE.md` §Callout |
| Bloque de código | ver `REFERENCE.md` §Bloque de código |
| Regla horizontal | borde inferior a nivel de párrafo; ver REFERENCE.md |
| Cabeceras / pies / páginas | ver `REFERENCE.md` §Cabeceras, pies, números de página |
| TOC | ver `REFERENCE.md` §Tabla de contenidos |
| Landscape mid-documento | ver `REFERENCE.md` §Documentos multi-sección |
| Preview visual | `soffice --convert-to pdf` + `pdftoppm -r 150` |
| Export PDF | `soffice --headless --convert-to pdf out.docx` |
| Merge / split / find-replace | ver `STRUCTURAL_OPS.md` |
| Convertir `.doc` heredado | `soffice --headless --convert-to docx old.doc` |
| Plantilla del usuario | carga `.docx` / `.dotx` directamente; reusa sus estilos |

## 16. Cuándo cargar REFERENCE.md

- Snippets completos para cada bloque (portada, encabezados, párrafos,
  tablas con overrides, figuras, callouts, listas, bloques de código,
  reglas horizontales)
- Referencia de paleta (editorial-serio, corporativo-formal,
  técnico-minimalista, cálido-revista, sobrio-legal,
  académico-sobrio)
- Campo de tabla de contenidos
- Cabeceras / pies / números de página (centrado, logo+título,
  skip-first-page)
- Documentos multi-sección (vertical / apaisado mezclado)
- Encabezados numerados (`1.`, `1.1`, `1.1.1`)
- Procedimiento de embedding de fuentes (para entrega exacta en
  Word 2016+)
- Trabajar con un DOCX existente como punto de partida
- Pipeline de validación visual (DOCX → PDF → PNG por página)
- Export a PDF en una línea
- Labels i18n (inglés / español) para cover / footer
- Campos SEQ para numeración de figuras / tablas
- Content controls (inspección read-only)
- Generación batch (N documentos desde un dataset)
