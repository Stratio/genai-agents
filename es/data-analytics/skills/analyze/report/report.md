# Generación de Informes

Sub-guía de la skill `analyze`. La carga `analyze/SKILL.md` (Fase 4) después de que el workflow analítico haya producido datos y gráficos en `output/[ANALYSIS_DIR]/`. Genera entregables profesionales en múltiples formatos (PDF, DOCX, web interactiva con Plotly, PowerPoint).

## 1. Determinar Formato, Estructura y Estilo

Parsear argumento: $ARGUMENTS

Si el formato no está especificado, preguntar al usuario las 3 preguntas siguientes en una sola interacción, siguiendo la convención de preguntas.

**Reglas de presentación — OBLIGATORIAS**:
- Presentar **todas** las opciones literalmente, una por línea. Nunca agrupar, resumir, omitir ni parafrasear opciones, aunque alguna parezca "avanzada" o secundaria. El usuario debe ver todas para decidir con criterio.
- Seguir la convención de preguntas para el mecanismo de entrega — el agente usa una herramienta interactiva de pregunta cuando el entorno la provee, o una lista numerada en chat en otro caso. No fijar el nombre de la herramienta; dejar que la convención lo resuelva.
- Cada pregunta es su propio bloque numerado en el renderizado en chat.
- Mantener los **labels** (Corporativo, Académico, Moderno, Design-first, Scaffold base, Al vuelo, Documento, Web, PowerPoint) literales — se mapean a routing interno. Solo se traduce la prosa circundante si el usuario trabaja en otro idioma.

### Pregunta 1 — ¿En qué formatos quieres los entregables? (selección múltiple)
- **Documento** — PDF + DOCX
- **Web** — HTML interactivo con Plotly
- **PowerPoint** — `.pptx`

### Pregunta 2 — ¿Qué estructura prefieres para el informe? (selección única)
- **Scaffold base** *(Recomendado)* — resumen ejecutivo → metodología → datos → análisis → conclusiones
- **Al vuelo** — estructura libre según el contexto

### Pregunta 3 — ¿Qué estilo visual prefieres? (selección única)
- **Corporativo** *(Recomendado)* — `corporate.css`, limpio y profesional
- **Académico** — `academic.css`, tipografía serif, márgenes amplios, estilo paper
- **Moderno** — `modern.css`, color y gradientes, visualmente atractivo
- **Design-first** — compromiso con una dirección estética deliberada (tono, emparejamiento tipográfico, paleta, presupuesto de motion) derivada de la materia del informe. Recomendado cuando el entregable es una pieza de alta visibilidad — resúmenes ejecutivos para un consejo, briefs de lanzamiento, informes narrativos donde la voz visual es parte del mensaje. Ver §4.1 para el workflow.

Notas:
- La pregunta 1 SIEMPRE permite selección múltiple (el usuario puede querer varios formatos).
- Si no se selecciona ningún formato, solo se da respuesta textual en el chat.
- Siempre se genera `output/[ANALISIS_DIR]/report.md` automáticamente como documentación interna (no necesita opción).
- Si el formato viene en el argumento (`$ARGUMENTS`), saltar directamente a las preguntas 2 y 3.

### 1.1 Convención de nombres para deliverables

Los entregables orientados al usuario se escriben con un prefijo descriptivo para que sean reconocibles tras descargarlos, fuera de su carpeta:

- `<slug>-report.pdf`, `<slug>-report.docx` (formato Document)
- `<slug>-dashboard.html` (formato Web)
- `<slug>-presentation.pptx` (formato PowerPoint)

`<slug>` es la parte descriptiva de `[ANALISIS_DIR]` — la carpeta es `YYYY-MM-DD_HHMM_<slug>/`, así que `<slug>` es todo lo que va después del prefijo de timestamp. Los ficheros internos (`plan.md`, `reasoning.md`, `report.md`, `validation.md`, `aesthetic.json`) se quedan sin prefijo.

## 2. Verificar Datos Disponibles

- Comprobar si existen datos previos en `output/[ANALISIS_DIR]/data/` (CSVs, DataFrames)
- Comprobar si existen gráficas en `output/[ANALISIS_DIR]/assets/`
- Si no hay datos: informar al usuario que primero necesita ejecutar un análisis
- Si hay datos parciales: preguntar si reutilizar o regenerar

### 2.1 Visualización y storytelling

Leer y seguir [../visualization.md](../visualization.md) para:
- Selección de tipo de gráfica según pregunta analítica (sec 1)
- Principios de visualización y accesibilidad (sec 2)
- Data storytelling: estructura narrativa Hook→Contexto→Hallazgos→Tensión→Resolución (sec 3)
- Mapping hallazgos analíticos → rol narrativo (sec 4)

**Específico de report — Layout anti-solapamiento**: Título como insight arriba, contexto como subtítulo, leyenda posicionada debajo del gráfico o a la derecha exterior. Usar `tools/chart_layout.py` para layout estándar.

## 3. Setup del Entorno

```bash
bash setup_env.sh
```
Verificar que las dependencias del formato están disponibles (weasyprint para PDF, python-pptx para PowerPoint, etc.).

**Imports Python desde scripts generados**: los módulos generadores viven en `skills/analyze/report/tools/`. Cuando el agente escriba un script generador (ej: `output/[ANALYSIS_DIR]/scripts/make_report.py`), añadir esa carpeta a `sys.path` al inicio del script para que imports como `from pdf_generator import PDFGenerator` resuelvan correctamente:

```python
import sys
sys.path.insert(0, "skills/analyze/report/tools")

from pdf_generator import PDFGenerator
from css_builder import build_css, get_palette
```

Invocaciones CLI (ej: `md_to_report.py`) se llaman por ruta completa desde la raíz del agente: `python skills/analyze/report/tools/md_to_report.py ...`.

## 3.1 Idioma de los Deliverables Generados

Todos los generadores (`DOCXGenerator`, `PDFGenerator`, `DashboardBuilder`, `md_to_report.py`) usan un catálogo i18n compartido en `tools/i18n.py` para sus labels estáticos (títulos del scaffold "Resumen Ejecutivo" / "Metodología" / …, labels de cover "Autor:" / "Dominio:" / "Fecha:", chrome del dashboard "Filtros" / "Limpiar filtros" / "KPIs", el atributo HTML `lang`, el título por defecto del informe, etc.).

**Pasar el idioma del usuario explícitamente al invocar cualquier generador** para que el chrome estático coincida con el idioma del chat:

- API Python (`DOCXGenerator`, `PDFGenerator`, `DashboardBuilder`): pasar `lang="<código>"` a `render_scaffold` / `render_from_markdown` / `render_from_html` / el constructor (según aplique). Opcionalmente pasar `labels={...}` para sobrescribir claves concretas.
- CLI (`md_to_report.py`): pasar `--lang <código>` (y opcionalmente `--labels-json '{...}'`).

Orden de resolución cuando no se pasa `lang`: fichero `.agent_lang` escrito al empaquetar → `"en"`. Así un paquete hecho con `--lang es` usa español por defecto aunque no se pase `lang` explícito. Idiomas del catálogo hoy: `en`, `es`. Códigos desconocidos hacen fallback a inglés por clave; pasar `labels={...}` para inyectar traducciones a otros idiomas.

## 4. Herramientas de Estilo

Todos los formatos comparten la misma fuente de verdad para colores y fuentes:

- **CSS (PDF, Web):** `build_css(style, target)` de `tools/css_builder.py` ensambla tokens + theme + target
- **No-CSS (PPTX, DOCX):** `get_palette(style)` de `tools/css_builder.py` devuelve colores RGB y fuentes
- **Reasoning (Markdown → PDF/HTML):** `tools/md_to_report.py` con opciones `--style`, `--cover`, `--author`, `--domain`

```python
import sys
sys.path.insert(0, "skills/analyze/report/tools")

from css_builder import build_css, get_palette
css, name = build_css("corporate", "pdf")    # CSS ensamblado
palette = get_palette("corporate")           # {"primary": (0x1a,0x36,0x5d), "font_main": "Inter", ...}
```

## 4.1 Workflow Design-first (cuando la pregunta 3 elige "Design-first")

Cuando el usuario elige "Design-first" en la pregunta 3, ejecuta este checklist de cinco pasos **antes** de invocar ningún generador. Persiste el resultado en `output/[ANALYSIS_DIR]/aesthetic.json` y pásalo como `aesthetic_direction` a `DashboardBuilder`, `PDFGenerator`, `DOCXGenerator`, `create_presentation`, `chart_layout.get_chart_colors`, y `md_to_report.py --aesthetic`. Así el HTML, el PDF, el DOCX y el PPTX quedan visualmente coherentes.

1. **Clasifica el artefacto** — `executive-dashboard` / `technical-report` / `editorial-brief` / `forensic-audit`. La clase gobierna las siguientes cinco decisiones.
2. **Elige un tono (uno, comprometido)** — `editorial-serious` / `technical-minimal` / `executive-editorial` / `forensic-audit` / `maximalist-analytical` / `brutalist-data`. Mitad-y-mitad no es opción.
3. **Emparejamiento tipográfico** — una fuente display + una body desde la tabla "Emparejamientos tipográficos por clase de artefacto" en [dashboard-aesthetics.md](dashboard-aesthetics.md). Escribe el resultado como `font_pair: [display, body]`.
4. **Paleta** — deriva un acento dominante de la materia de los datos (finanzas → azul profundo u oxblood; operaciones → acero frío o bosque; auditoría → rojo profundo sobre hueso; consumo → un primario saturado). Rellena un dict `palette_override` con claves a nivel CSS (`"--primary"`, `"--accent"`, `"--text-primary"`, …) coherentes con los tokens del estilo base elegido. *Nota:* en `academic`, el token del rol "primary" es `--heading-color`; sobrescribir `--primary` allí es inerte — consulta la nota "Caveat — `academic`" en [dashboard-aesthetics.md](dashboard-aesthetics.md).
5. **Presupuesto de motion** (solo dashboards) — `none` / `minimal` / `expressive`. Nada de JS, CSS puro, `@keyframes` prefijados con `dashboard-`, `prefers-reduced-motion` respetado.
6. **Estilo de fondo** (opcional) — `solid` / `gradient-mesh` / `noise` / `grain`. Decide si el artefacto se gana atmósfera más allá de una superficie plana.

Escribe el `aesthetic.json` resultante con este schema (claves extra las rechaza `md_to_report.py --aesthetic`):

```json
{
  "tone": "editorial-serious",
  "palette_override": {"--primary": "#0a2540", "--accent": "#d9472b"},
  "font_pair": ["Fraunces", "Inter"],
  "motion_budget": "expressive",
  "background_style": "gradient-mesh"
}
```

**Orden de operaciones**: crea `output/[ANALYSIS_DIR]/` antes de escribir `aesthetic.json`. Si el fichero ya existe de una ejecución anterior y el usuario elige ahora un estilo distinto, sobrescríbelo y añade una línea a `reasoning.md`:

> *Dirección estética (contenido de `aesthetic.json`)*: tone=…, palette_override=…, font_pair=…, motion_budget=…, background_style=….

Consulta [dashboard-aesthetics.md](dashboard-aesthetics.md) para la guía específica interactiva (motion, hover, fondos, tipografía para pantalla) y `skills-guides/visual-craftsmanship.md` para los principios transversales (anti-patrones, roles de paleta, checklist de artesanía).

## 5. Generación por Formato

### 5.1 Documento (PDF + DOCX)
Si el usuario seleccionó "Documento": ver [document-guide.md](document-guide.md) para el pipeline completo de PDFGenerator, DOCXGenerator y pitfalls.

### 5.2 Web (Dashboard Interactivo)
Si el usuario seleccionó "Web": ver [web-guide.md](web-guide.md) para el pipeline completo de DashboardBuilder, capacidades, workflow y pitfalls.

### 5.3 PowerPoint
Si el usuario seleccionó "PowerPoint": ver [powerpoint-guide.md](powerpoint-guide.md) para el pipeline completo de pptx_layout, diseño de slides y pitfalls.

### 5.4 Markdown (siempre generado)
Se genera automáticamente en todos los análisis, sin necesidad de que el usuario lo seleccione.
1. Escribir .md directo con:
   - Tablas markdown para datos tabulares
   - Bloques mermaid para diagramas de flujo o relaciones
   - Referencias a gráficas en `output/[ANALISIS_DIR]/assets/`
2. Guardar en `output/[ANALISIS_DIR]/report.md`

## 6. Reasoning

Generar reasoning según la profundidad seleccionada (ver sec "Reasoning" de AGENTS.md):

- **Rápido**: No generar fichero. Notas clave en el chat.
- **Estándar/Profundo**: Generar `output/[ANALISIS_DIR]/reasoning/reasoning.md`. Si el usuario solicitó override a otros formatos (PDF, HTML, DOCX), convertir con `tools/md_to_report.py --style corporate --lang <idioma_usuario>` (añadir `--docx` si aplica).

Documentando:
- Formato(s) generado(s) y justificación
- Estructura elegida y por que
- Datos utilizados y sus fuentes
- Decisiones de diseño
- Rutas de todos los archivos generados

## 7. Entrega

**Antes de reportar**, ejecutar verificación de existencia:
```bash
ls -lh output/[ANALISIS_DIR]/
```
Si algún fichero solicitado no aparece en el listado → volver al paso 5 (generación) y regenerarlo. Solo reportar al usuario cuando todos los ficheros estén confirmados en disco.

A continuación reportar en el chat:
- Formato(s) generado(s)
- Ruta(s) de los archivos
- Vista previa del contenido (resumen ejecutivo)
- Instrucciones para abrir/usar el deliverable
