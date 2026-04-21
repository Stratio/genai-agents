# Estética de dashboards e informes

Guía específica interactiva cargada por `report.md` (Fase 4 de `/analyze`) cuando el usuario elige **Design-first** en la pregunta 3. Consúmela junto a los principios compartidos de `skills-guides/visual-craftsmanship.md` (proporcionada en la raíz del agente).

## Emparejamientos tipográficos por clase de artefacto

Empareja una fuente display con una body. El display aparece en titulares, KPIs hero y marcas; el body en prosa, celdas de tabla y etiquetas.

| Clase de artefacto | Display | Body | Apropiado para |
|---|---|---|---|
| Dashboard ejecutivo | Fraunces (variable) | Inter | Consejos, reportes trimestrales, estrategia |
| Informe técnico | Instrument Serif | IBM Plex Sans | Audiencias de ingeniería, revisiones de incidencias |
| Brief editorial | Crimson Pro | Inter o Work Sans | Informes narrativos, recomendaciones |
| Auditoría forense | IBM Plex Serif | IBM Plex Mono | Regulatorio, auditoría, QA |
| Analítica maximalista | Archivo Black | Inter | Decks de lanzamiento, KPIs muy visuales |
| Datos brutalistas | Archivo Black | IBM Plex Mono | Previews de research, release notes |

Sirve las fuentes vía `@import` desde un foundry o Google Fonts en el HTML generado, o empaqueta copias WOFF2 junto al artefacto y referéncialas con `@font-face`. Dos fuentes bastan; tres es el techo.

## Dirección de paleta por materia

Deriva el acento dominante del tema de los datos. Un color hace casi todo el trabajo; los neutros lo sostienen.

| Materia | Acento dominante | Neutro profundo | Neutro claro |
|---|---|---|---|
| Finanzas, banca | `#0a2540` (azul naval) o `#8a3324` (oxblood) | `#201a16` | `#f5ecdf` (crema) |
| Operaciones, cadena de suministro | `#1f4a3a` (bosque) o `#315a82` (acero) | `#16191f` | `#eef3f7` |
| Auditoría, compliance | `#5a1c1c` (rojo profundo) | `#121212` | `#f2ebe8` (hueso) |
| Productos de consumo | `#d9472b` (tomate) o `#7a3ea6` (mora) | `#1a1a1f` | `#f6f1e7` |
| Salud, farma | `#135169` (teal-azul) | `#16222b` | `#edf2f3` |
| Industrial, energía | `#c28b2c` (ámbar) o `#3c3c3c` (grafito) | `#111111` | `#efece7` |

Al emitir `palette_override`, usa tokens CSS que el estilo base elegido declare:

- `corporate` y `modern` definen `--primary`, `--accent`, `--text-primary`, `--bg-light`, `--font-main`, `--font-mono`.
- **Caveat — `academic`** no define `--primary`. Su rol `primary` se mapea a `--heading-color` (ver `_PALETTE_MAP` en `tools/css_builder.py`). Sobrescribir `--primary` en `academic` no tiene efecto; sobrescribe `--heading-color` o cambia el estilo base a `corporate`.

## Motion (solo en dashboards)

CSS puro, sin JS. Usa keyframes prefijados `dashboard-*` para evitar colisiones con la página host. Respeta `prefers-reduced-motion: reduce` cancelando animaciones y transiciones.

| Presupuesto | Cuándo elegirlo | Qué emite |
|---|---|---|
| `none` | Dashboards para lectura estática, impresión, contextos donde el motion distrae | Nada extra |
| `minimal` | Mayoría de dashboards | `dashboard-fade-in` de 320 ms en tarjetas KPI y secciones |
| `expressive` | Dashboards de lanzamiento, revelados hero, narrativas de producto | `dashboard-rise` escalonado (80 ms pasos), reveal de sección, hover lift |

Mantén el motion de carga de página por debajo de ~500 ms total. Plotly anima sus gráficas imperativamente — no apliques animaciones CSS a descendientes de `.js-plotly-plot`.

## Fondos

La clave `background_style` soporta cuatro modos; cada uno se renderiza inline sin assets externos.

- `solid` — sin CSS extra, gana la superficie base.
- `gradient-mesh` — gradientes radiales apilados tintados por el acento; bueno para dashboards editoriales.
- `noise` — filtro SVG estático de ruido por detrás del contenido; bueno para dashboards maximalistas o brutalistas.
- `grain` — patrón de puntos finos a 3 px; bueno para tonos analógicos o editoriales.

Evita noise en tablas densas — baja el contraste.

## Estados hover y focus

Cada elemento interactivo (filtro, sort, nav link, tarjeta KPI en modo drill-down) necesita hover y focus deliberados. Reglas:

- **Hover**: desplazamiento de 1–2 px hacia arriba o expansión de sombra en 180 ms. Hover solo de color lee como accidental.
- **Focus**: outline en el color de acento, visible en navegación por teclado (`:focus-visible`).
- **Active**: estado hundido — vuelve al translate baseline, superficie ligeramente más oscura.

## Schema canónico de `aesthetic.json`

Es el fichero que `report.md` escribe en `output/[ANALYSIS_DIR]/aesthetic.json` y pasa a cada generador.

```json
{
  "tone": "editorial-serious",
  "palette_override": {
    "--primary": "#0a2540",
    "--accent": "#d9472b",
    "--text-primary": "#1a1a1f"
  },
  "font_pair": ["Fraunces", "Inter"],
  "motion_budget": "expressive",
  "background_style": "gradient-mesh"
}
```

Todas las claves son opcionales; claves desconocidas las rechaza `md_to_report.py --aesthetic` y el validador interno. `font_pair` debe ser una lista de dos elementos `[display, body]`. `tone` es hoy informacional (trazabilidad en `reasoning.md`); no conduce CSS directamente — la paleta y las fuentes sí.

### Cómo lo consumen los generadores

| Destino | Herramienta | Entry point | Qué cambia |
|---|---|---|---|
| Dashboard HTML | `DashboardBuilder(aesthetic_direction=…)` | `.build()` | Tokens CSS sobrescritos, regla de display font, CSS de motion, fondos |
| PDF (scaffold/HTML) | `PDFGenerator(aesthetic_direction=…)` | `.render_scaffold()` / `.render_from_html()` | Tokens CSS sobrescritos |
| DOCX | `DOCXGenerator(aesthetic_direction=…)` | `.render_scaffold()` / `.render_from_markdown()` | Paleta sobrescrita (las fuentes solo afectan a encabezados hoy) |
| PPTX | `create_presentation(style, aesthetic_direction=…)` | devuelve `(prs, palette)` | Paleta sobrescrita |
| Gráficas | `chart_layout.get_chart_colors(style, n, aesthetic_direction=…)` | devuelve lista hex | Los colores de Plotly casan con el resto del artefacto |
| CLI (markdown → PDF) | `md_to_report.py --aesthetic aesthetic.json` | argparse | Fluye por `convert()` a PDF + DOCX opcional |
