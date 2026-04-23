---
name: pptx-writer
description: "Crea, manipula y pule decks de PowerPoint (.pptx) con diseño intencional. Usa esta skill siempre que necesites generar un deck nuevo (pitch, briefing de ventas, resumen ejecutivo, formación, académico, tipo-report, town-hall) o transformar uno existente (merge, split, reordenar, borrar slides, find-replace en texto de slide y notas del presentador, convertir .ppt legacy a .pptx, rasterizar slides, exportar a PDF). Esta skill se toma en serio el diseño — cada deck que produce tiene tipografía, color y layout intencionales, nunca el default genérico Calibri-por-todas-partes. Para rellenar charts OOXML nativos con datos reales en lugar de pegar imágenes de chart, carga REFERENCE.md."
argument-hint: "[tipo de deck o descripción]"
---

# Skill: PPTX Writer

Esta skill produce decks de PowerPoint que parecen diseñados, no
generados. La mayoría del output automático de PPT es visualmente
muerto: body en Calibri, negro puro sobre blanco, el aspect ratio
por defecto 10×7.5, una barra de heading azul si tienes suerte. Es
el baseline contra el que esta skill se rebela activamente.

Antes de escribir una sola línea de código, comprométete con una
dirección de diseño. El código sirve al diseño, no al revés.

## 1. Workflow design-first

Cada tarea de generación de deck, independientemente de su tamaño,
sigue cinco pasos:

1. **Clasifica el deck** — ¿de qué categoría es? (Ver la taxonomía
   de abajo.) Esto gobierna densidad, tono y estructura aguas abajo.
2. **Elige un tono visual** — editorial-moderno, corporativo-formal,
   técnico-minimalista, cálido-conversacional, académico-sobrio,
   lúdico-enérgico. Elige uno y ejecútalo con confianza. Un deck
   tímido "un poco de todo" es el peor outcome.
3. **Selecciona un emparejamiento tipográfico** — una face de
   display para títulos y headings, una face de body para prosa y
   bullets. Dos tipografías casi siempre bastan. Como PPT usa las
   fuentes del sistema del lector salvo que embebas, elige
   emparejamientos que degraden bien — Calibri / Aptos / Inter /
   Arial son defaults seguros universales.
4. **Define una paleta** — un color de acento dominante, un
   neutral profundo para body (raramente negro puro), un neutral
   pálido para fondos o reglas, más colores de estado (éxito /
   alerta / peligro) usados con moderación. Saturación real, no
   pasteles lavados por defecto.
5. **Marca el ritmo** — objetivo de densidad (pitch: 1 idea por
   slide; briefing ejecutivo: 3–4 bullets; formación: 5–7 bullets
   + figura), un divisor de sección cada 4–6 slides para que la
   audiencia respire, espaciado vertical consistente dentro de
   cada slide.

Solo entonces abre `python-pptx`.

### Taxonomía de decks y puntos de partida

| Categoría | Tono típico | Display | Body | Densidad |
|---|---|---|---|---|
| Pitch / deck de VC | Editorial-moderno | Inter / IBM Plex Sans | Inter | 1 idea/slide |
| Ventas / demo producto | Cálido-conversacional | Inter | Inter | visual-heavy |
| Briefing ejecutivo | Corporativo-formal | IBM Plex Serif | IBM Plex Serif | 3–4 bullets |
| Formación / how-to | Técnico-minimalista | IBM Plex Sans | IBM Plex Sans | 5–7 bullets + figuras |
| Académico / research | Académico-sobrio | Libre Baskerville | Libre Baskerville | prosa + fórmulas |
| Analítico tipo-report | Editorial-serio | Crimson Pro | Inter | tablas/charts densos |
| Town-hall / all-hands | Cálido-conversacional | Inter | Inter | KPIs grandes, emotivo |

Estos son puntos de partida, no mandatos. Rómpelos cuando el brief
lo pida. El objetivo es **nunca caer en el template blank Calibri-
sobre-blanco de python-pptx**.

### Cuándo esta skill no es la adecuada

- **Reports analíticos dentro de `/analyze`** — el agente
  `data-analytics` tiene su propio pipeline de PPT opinionado en
  `skills/analyze/report/tools/pptx_layout.py`. Dentro de la
  Phase 4 de `/analyze`, importa los helpers de ese módulo. Esta
  skill es para decks fuera del pipeline analítico.
- **Posters / portadas / certificados de una página** — artefactos
  estáticos dominados por composición pertenecen a `canvas-craft`.
- **Dashboards interactivos en navegador** — `web-craft` los cubre.

## 2. Aspect ratio

Los decks se entregan por defecto en **16:9 (10 × 5.625 pulgadas)**.
El legacy 4:3 (10 × 7.5 pulgadas) se reserva para decks que se
proyectarán en hardware antiguo o se embederán en plantillas de
documento antiguas. Nunca mezcles aspect ratios dentro del mismo
deck.

`python-pptx` crea decks 16:9 por defecto cuando cargas el scaffold
incluido (`assets/blank.pptx`). Si saltas el scaffold y llamas a
`Presentation()` directamente, obtienes el template interno de
python-pptx que es **4:3** — carga siempre el scaffold salvo que
una plantilla del usuario dicte otra cosa.

Si el usuario provee su propia plantilla corporativa `.pptx` o
`.potx` (ver §12), cárgala en su lugar; el master de la plantilla
fija el aspect ratio.

## 3. Una plantilla de inicio apropiada

En vez de caer en los defaults de `python-pptx`, usa este scaffold
y adáptalo:

```python
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt, Emu

# 1. Compromete tus tokens de diseño desde el principio — no cambian.
SCAFFOLD = Path(__file__).parent / "assets" / "blank.pptx"

DESIGN = {
    # Paleta (hex — convierte a RGBColor en el uso)
    "primary":     "#0a2540",   # azul navy profundo
    "accent":      "#d9472b",   # rojo cálido
    "ink":         "#1f2937",   # texto body
    "muted":       "#6b7280",   # captions, metadata
    "rule":        "#d1d5db",   # divisores
    "bg":          "#ffffff",
    "bg_alt":      "#f9fafb",   # pálido para bandas de tabla
    # Tipografía
    "display":     "IBM Plex Sans",
    "body":        "Inter",
    # Tamaños (pt)
    "size_title":        40,
    "size_subtitle":     22,
    "size_heading":      28,
    "size_body":         18,
    "size_small":        14,
}

def hex_to_rgb(h: str) -> RGBColor:
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

# 2. Carga el scaffold — es 16:9 y tiene un layout blank limpio.
prs = Presentation(str(SCAFFOLD))

# 3. Deriva constantes de safe-area dinámicamente desde el tamaño del slide.
SLIDE_W = prs.slide_width or Inches(10).emu
SLIDE_H = prs.slide_height or Inches(5.625).emu
MARGIN = Inches(0.5)
TITLE_TOP = Inches(0.4)
TITLE_H = Inches(0.9)
CONTENT_TOP = TITLE_TOP + TITLE_H + Inches(0.2)
CONTENT_H = SLIDE_H - CONTENT_TOP - Inches(0.5)
CONTENT_W = SLIDE_W - 2 * MARGIN
BLANK_LAYOUT = prs.slide_layouts[6]  # índice 6 es Blank en el scaffold incluido

# 4. Helpers pequeños (en uso real, llévalos a tu propio módulo).
def add_title(slide, text: str) -> None:
    box = slide.shapes.add_textbox(MARGIN, TITLE_TOP, CONTENT_W, TITLE_H)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = DESIGN["display"]
    run.font.size = Pt(DESIGN["size_title"])
    run.font.bold = True
    run.font.color.rgb = hex_to_rgb(DESIGN["primary"])

def add_accent_bar(slide, width_in: float = 1.6, height_in: float = 0.08) -> None:
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN, TITLE_TOP + TITLE_H + Emu(10000),
        Inches(width_in), Inches(height_in),
    )
    bar.line.fill.background()
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(DESIGN["accent"])

# 5. Construye slides.
cover = prs.slides.add_slide(BLANK_LAYOUT)
add_title(cover, "El título del deck")
add_accent_bar(cover)

content = prs.slides.add_slide(BLANK_LAYOUT)
add_title(content, "Heading de sección")
# ... añade bullets, tablas, figuras etc.

prs.save("output.pptx")
```

Tres reglas que el scaffold hace cumplir:

- **Siempre `slide_layouts[6]` (Blank)**. Otros layouts embeben
  placeholders que pelean con tu diseño. Posiciona todo
  explícitamente con `add_textbox` / `add_shape`.
- **Siempre `text_frame.word_wrap = True`**. Está off por defecto;
  sin él, python-pptx recorta silenciosamente el overflow.
- **Siempre calcula safe-area desde `prs.slide_width / slide_height`.**
  Constantes 4:3 hardcoded (como las del pipeline de `/analyze`)
  rompen sobre un scaffold 16:9.

## 4. Fuentes

PPT usa las fuentes del sistema del lector salvo que las embebas en
`ppt/fonts/`. Consecuencias:

- **Camino por defecto**: usa tipografías ampliamente instaladas
  (Calibri, Aptos, Inter, Arial, Times New Roman, Georgia, Cambria).
  Funciona en todas partes sin pasos extra.
- **Camino de embedding**: técnicamente posible escribiendo a
  `ppt/fonts/` y referenciando en `embeddedFontLst`, pero solo
  completamente honrado por PowerPoint 2016+ en Windows. Mac Office
  ignora silenciosamente las fuentes embebidas; LibreOffice es
  parcial; Web Office sustituye.

Recomendación: quédate en defaults seguros salvo que el deck solo
vaya a abrirse en Windows PowerPoint. Informa al usuario si un
pairing elegido requiere una face no estándar (p.ej. "IBM Plex
Serif + IBM Plex Mono funciona en Windows, se renderiza con
sustitución en Mac").

## 5. Guía de paleta

Un deck diseñado tiene como mucho tres familias de color en un
slide dado: primario (un color de acento, saturado, usado en 5–15%
de la superficie), neutrales (texto body y fondos), y colores de
estado (éxito/alerta/peligro) usados con moderación para KPIs o
callouts.

Cuando inventes una paleta para un deck, elige valores hex concretos
desde el principio y cíñete a ellos. No mezcles dos azules distintos,
dos rojos distintos o dos saturaciones de acento distintas en el
mismo deck. Si el brief sugiere un tono ("corporativo" / "lúdico" /
"académico"), elige valores que realmente vendan ese tono — corporate
navy es `#0a2540`, no un azul cielo pastel; académico es un carbón
moderado y un beige cálido, no color saturado para nada.

El módulo `pptx_layout.py` dentro de `/analyze` lleva tres paletas
de referencia (`corporate`, `academic`, `modern`) si quieres arte
previo; si no, inventa una paleta que sirva al brief.

## 6. Tipos de slide que construirás

Abajo están las composiciones que merece dominar. Los snippets para
cada uno viven en `REFERENCE.md`; aquí está el menú.

- **Portada** — título, subtítulo, autor, fecha, barra de acento.
  Sin otro contenido.
- **Agenda** — una lista numerada de secciones, cada una con un
  resumen de una línea. Limita a 3–7 ítems; más significa que el
  deck es demasiado largo.
- **Divisor de sección** — nombre de sección grande y negrita, a
  menudo con el número de sección ("01 / 05"). Fuerza a la
  audiencia a resetear atención entre bloques.
- **Título + contenido** — un solo heading y 3–7 bullets o un
  párrafo corto. El slide mula de carga.
- **Dos columnas** — listas paralelas, pro/contra, problema/solución.
- **Imagen con texto** — imagen hero (izquierda o derecha) con un
  título y caption corto al otro lado.
- **Slide de KPI** — un número grande (36–54 pt), una etiqueta
  concisa, una unidad opcional; o una fila de 3 KPIs.
- **Tabla** — datos estructurados, 3–10 filas típicamente; más de
  15 suele significar que va a página completa, no slide. Ver §7
  sobre el override de estilo de tabla que debes aplicar.
- **Chart** — chart OOXML nativo para bar/column/line/pie/area/
  scatter/radar/bubble (editable por el usuario); imagen
  pre-renderizada para cualquier cosa que python-pptx no soporte
  (waterfall, sunburst, sankey, combo).
- **Cita** — una frase, atribución, espacio en blanco visual. La
  tipografía es el sujeto del slide.
- **Conclusión / llamada a la acción** — 3 bullets o 1 headline +
  la línea de siguiente paso. Evita "Thank you" como slide final;
  termina con el mensaje.

## 7. Tablas

Las tablas de `python-pptx` heredan por defecto un estilo de tema
pastel que parece el default era-2003 de Microsoft. **Sobrescríbelo
siempre agresivamente**. El override baseline, en palabras:

- Fila de header: relleno con el color primario, texto blanco, bold,
  face de body o display a 16–18 pt, alineado a la izquierda para
  columnas de prosa y a la derecha para numéricas.
- Filas de body: sin líneas verticales, una regla horizontal sutil
  entre filas, color de banda alternado (white / `bg_alt`) para
  legibilidad.
- Altura de fila: ligeramente generosa (12–15 pt de padding interno);
  filas apretadas se leen como screenshot de hoja de cálculo.

El snippet completo vive en `REFERENCE.md` §Tabla con override de
estilo; llámalo desde cada slide que produzca tabla.

## 8. Imágenes

Colocadas vía `slide.shapes.add_picture(path, left, top, width,
height)`. Dos reglas:

- **Nunca distorsiones el aspect ratio.** Calcula dimensiones
  destino que encajen dentro de una caja de safe-area preservando
  proporciones. Snippet helper en `REFERENCE.md` §Imagen con aspect
  ratio preservado.
- **Prefiere PNG con fondo transparente** cuando el slide tenga
  fondo no blanco; un JPG con blanco horneado deja un rectángulo
  visible. Renderiza charts desde matplotlib / plotly con
  `dpi=200, facecolor="none"` antes de insertar.

## 9. Charts

Los charts de PPT tienen una ventaja enorme de calidad de vida
frente a las imágenes: el usuario puede hacer doble click y editar
los datos subyacentes en un diálogo estilo Excel. Para cualquier
tipo de chart soportado por python-pptx, prefiere un chart nativo
frente a una imagen renderizada.

Tipos soportados:

| Tipo | Enum python-pptx | Cuándo usar |
|---|---|---|
| Column / bar | `XL_CHART_TYPE.COLUMN_CLUSTERED`, `BAR_CLUSTERED` | comparando categorías |
| Line | `XL_CHART_TYPE.LINE` | tendencia en el tiempo |
| Pie / doughnut | `XL_CHART_TYPE.PIE`, `DOUGHNUT` | 3–6 porciones de un total |
| Area | `XL_CHART_TYPE.AREA` | acumulativo en el tiempo |
| Scatter | `XL_CHART_TYPE.XY_SCATTER` | correlación |
| Radar | `XL_CHART_TYPE.RADAR` | comparación multidimensional |
| Bubble | `XL_CHART_TYPE.BUBBLE` | scatter con tres variables |

No soportados (usa imagen pre-renderizada):

- Waterfall, sunburst, sankey, combo (bar+line en el mismo chart),
  charts de mapa, funnel, histogramas con binning custom.

Snippet en `REFERENCE.md` §Chart OOXML nativo — bar / column / line.

## 10. Notas del presentador

Pitch decks, briefings ejecutivos, decks de formación y
presentaciones académicas viven por sus notas del presentador — el
guion hablado que acompaña al visual. Un deck generado sin notas
es media entrega para estas categorías.

```python
slide.notes_slide.notes_text_frame.text = "La narrativa hablada para este slide."
```

Se soportan notas multi-párrafo; separa con `\n` o llama a
`add_paragraph()` para estructura más rica. Las notas heredan la
fuente por defecto de python-pptx; raramente necesitas estilarlas.

Para pitch y formación, trata "generar notas del presentador" como
parte de la definición de la tarea, no como bonus.

## 11. Validación visual y export a PDF

Tras construir, inspecciona siempre visualmente el output renderizado.
Dos snippets:

- **Validación visual** (`REFERENCE.md` §Validación visual):
  convierte a PDF vía LibreOffice y rasteriza PNGs por slide con
  `pdftoppm`. Inspecciona cada PNG por overflow, contraste
  awkward, espaciado apretado, imágenes rotas. Regenera y
  re-valida; 2–3 iteraciones es normal.
- **Export PDF** (`REFERENCE.md` §Export PDF): one-liner vía
  `soffice --headless --convert-to pdf`. El entregable por defecto
  es solo el PPTX. Añade un PDF hermano únicamente cuando el
  usuario lo pida explícitamente o cuando el brief implique
  distribución fuera de PowerPoint (compartir en externo, adjunto
  de email, audiencia sin Office, "lo mando por ahí", publicación).
  Si tienes dudas, entrega solo el PPTX — el usuario siempre puede
  pedir el PDF después.

Ambos comandos dependen de `libreoffice` y `poppler-utils` instalados.
Pre-instalados en el sandbox Stratio Cowork; ver README.md para
setup local.

## 12. Plantillas del usuario (`.potx` / `.pptx`)

Cuando el usuario provee una plantilla corporativa — con su logo,
master slide, fuentes y paleta — ignora el scaffold y carga su
fichero:

```python
from pptx import Presentation
prs = Presentation("ruta/a/plantilla_cliente.pptx")

# Inspecciona los layouts que la plantilla provee. Las plantillas
# corporativas suelen traer 5–10 layouts con nombre: Portada, Sección,
# Título+Contenido, Imagen+Caption, Dos Columnas, Tabla, KPI, Gracias.
for i, layout in enumerate(prs.slide_layouts):
    print(i, layout.name)

# Elige layouts que casen con tu intención. Respeta los placeholders —
# el diseñador de la plantilla los posicionó por algo.
cover = prs.slides.add_slide(prs.slide_layouts[0])
cover.placeholders[0].text = "El título del deck"  # placeholder de título
if len(cover.placeholders) > 1:
    cover.placeholders[1].text = "Subtítulo / fecha / autor"

content = prs.slides.add_slide(prs.slide_layouts[2])
content.placeholders[0].text = "Heading de sección"
# El placeholder de contenido suele ser el índice 1; su text frame
# acepta bullets vía párrafos con p.level.
```

Cuando uses una plantilla de cliente:

- **No sobrescribas el master**. Los colores, fuentes y logo son
  la identidad de la plantilla.
- **No uses `slide_layouts[6]` (Blank).** El sentido de la plantilla
  son sus layouts diseñados.
- **Sí usa `placeholders`** en lugar de `add_textbox`. La plantilla
  posicionó los placeholders.
- **Sigue forzando `word_wrap = True`** y sigue validando visualmente.

Snippet en `REFERENCE.md` §Usando una plantilla de cliente.

## 13. Operaciones estructurales

Para manipular decks existentes (merge, split, reordenar, borrar,
find-replace cross-slide y notas, convertir `.ppt` legacy), ver
`STRUCTURAL_OPS.md`. Son snippets copy-paste; ejecútalos desde un
script pequeño, no intentes importarlos como módulo.

## 14. Limitaciones conocidas

`python-pptx` cubre ~80% de la autoría real de decks de forma limpia.
El 20% restante requiere o bien manipulación OOXML cruda o no está
soportado en absoluto:

- **Animaciones y transiciones de slide** — no soportadas. Existe
  un snippet para la transición fade más simple en `REFERENCE.md`
  pero es frágil; prefiere sin transiciones en decks generados.
- **SmartArt** — no soportado. Dibuja el equivalente con llamadas a
  `add_shape` (flechas entre rectángulos para un process flow,
  rectángulos apilados para una jerarquía).
- **Vídeos / audios embebidos** — escribir funciona pero muchos
  renderizadores los pierden silenciosamente. No recomendado.
- **Macros (VBA)** — `.pptx` no tiene VBA. Si el usuario necesita
  macros, el fichero tiene que ser `.pptm` y eso está fuera de
  alcance.
- **Tipos avanzados de chart** (waterfall, sunburst, sankey, combo)
  — renderiza como imagen.
- **Renderizado exacto de fuente en cada máquina** — ver §4.

Documenta la limitación en las notas del presentador del deck o en
un slide de anexo cuando afecte al deliverable.

## 15. Cheat sheet de referencia rápida

| Tarea | Enfoque |
|---|---|
| Crear deck | `Presentation("assets/blank.pptx")` luego añade slides desde `slide_layouts[6]` |
| Slide nuevo | `prs.slides.add_slide(BLANK_LAYOUT)` |
| Texto de título | `add_textbox(...).text_frame` con `word_wrap=True` |
| Lista de bullets | text frame con un párrafo por bullet, `p.level` para indent |
| Tabla con override | ver `REFERENCE.md` §Tabla con override de estilo |
| Imagen preservando aspect | ver `REFERENCE.md` §Imagen con aspect ratio preservado |
| Caja de KPI | ver `REFERENCE.md` §Caja de KPI |
| Chart nativo | ver `REFERENCE.md` §Chart OOXML nativo |
| Notas del presentador | `slide.notes_slide.notes_text_frame.text = "..."` |
| Preview visual | `soffice --convert-to pdf` + `pdftoppm -r 150` |
| Export PDF | `soffice --headless --convert-to pdf out.pptx` |
| Merge / split / reordenar | ver `STRUCTURAL_OPS.md` |
| Convertir `.ppt` legacy | `soffice --headless --convert-to pptx old.ppt` |
| Plantilla de usuario | carga `.pptx`/`.potx` directamente como scaffold |

## 16. Cuándo cargar REFERENCE.md

- Snippets completos para cada tipo de slide (portada, agenda,
  divisor de sección, título+contenido, bullets, dos columnas,
  imagen-con-texto, KPI, tabla-con-override, chart, cita, conclusión)
- Construcción de charts OOXML nativos para bar / column / line /
  pie / area / scatter / radar / bubble
- Helpers dinámicos de safe-area funcionando para cualquier aspect ratio
- Pipeline de validación visual (PPTX → PDF → PNG por slide)
- One-liner de export PDF
- Etiquetas i18n (inglés / español) para Agenda / Conclusiones /
  Slide N de M
- Usando una plantilla de cliente (`.potx` / `.pptx`) — navegando
  layouts y placeholders
