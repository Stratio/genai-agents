---
name: report
description: Generacion de informes profesionales en multiples formatos (PDF, DOCX, web interactiva con Plotly, PowerPoint) a partir de analisis de datos. Usar cuando el usuario necesite generar informes, dashboards, presentaciones o documentacion a partir de datos analizados.
argument-hint: '[formato: pdf|web|pptx] [tema (opcional)]'
---

# Skill: Generacion de Informes

Guia para generar informes profesionales en multiples formatos a partir de datos y analisis.

## 1. Determinar Formato, Estructura y Estilo

Parsear argumento: $ARGUMENTS

Si el formato no esta especificado, preguntar al usuario las 3 preguntas siguientes en una sola interaccion, siguiendo la convencion de preguntas de CLAUDE.md sec 12 (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no). Las opciones son literales — no inventar, no omitir, no sustituir:

| # | Pregunta | Opciones (literales) | Seleccion |
|---|----------|---------------------|-----------|
| 1 | ¿En que formatos quieres los deliverables? | **Documento** (PDF + DOCX) · **Web** (HTML interactivo con Plotly) · **PowerPoint** (.pptx) | Multiple |
| 2 | ¿Que estructura prefieres para el reporte? | **Scaffold base** (Recomendado): resumen ejecutivo → metodologia → datos → analisis → conclusiones · **Al vuelo**: estructura libre segun contexto | Unica |
| 3 | ¿Que estilo visual prefieres? | **Corporativo** (`corporate.css`, Recomendado): limpio, profesional · **Formal/academico** (`academic.css`): serif, margenes amplios, estilo paper · **Moderno/creativo** (`modern.css`): colores, gradientes, visualmente atractivo | Unica |

- La pregunta 1 SIEMPRE permite seleccion multiple (el usuario puede querer varios formatos)
- Si no selecciona ningun formato, solo se da respuesta textual en el chat
- Siempre se genera `output/[ANALISIS_DIR]/report.md` automaticamente como documentacion interna (no necesita opcion)
- Si el formato viene en el argumento ($ARGUMENTS), saltar directamente a preguntar estructura y estilo (preguntas 2 y 3)

## 2. Verificar Datos Disponibles

- Comprobar si existen datos previos en `output/[ANALISIS_DIR]/data/` (CSVs, DataFrames)
- Comprobar si existen graficas en `output/[ANALISIS_DIR]/assets/`
- Si no hay datos: informar al usuario que primero necesita ejecutar un analisis
- Si hay datos parciales: preguntar si reutilizar o regenerar

### 2.1-2.3 Visualizacion y storytelling

Leer y seguir `skills-guides/visualization.md` para:
- Seleccion de tipo de grafica segun pregunta analitica (sec 1)
- Principios de visualizacion y accesibilidad (sec 2)
- Data storytelling: estructura narrativa Hook→Contexto→Hallazgos→Tension→Resolucion (sec 3)
- Mapping hallazgos analiticos → rol narrativo (sec 4)

**Especifico de report — Layout anti-solapamiento**: Titulo como insight arriba, contexto como subtitulo, leyenda posicionada debajo del grafico o a la derecha exterior. Usar `tools/chart_layout.py` para layout estandar.

## 3. Setup del Entorno

```bash
bash setup_env.sh
```
Verificar que las dependencias del formato estan disponibles (weasyprint para PDF, python-pptx para PowerPoint, etc.).

## 4. Herramientas de Estilo

Todos los formatos comparten la misma fuente de verdad para colores y fuentes:

- **CSS (PDF, Web):** `build_css(style, target)` de `tools/css_builder.py` ensambla tokens + theme + target
- **No-CSS (PPTX, DOCX):** `get_palette(style)` de `tools/css_builder.py` devuelve colores RGB y fuentes
- **Reasoning (Markdown → PDF/HTML):** `tools/md_to_report.py` con opciones `--style`, `--cover`, `--author`, `--domain`

```python
from css_builder import build_css, get_palette
css, name = build_css("corporate", "pdf")    # CSS ensamblado
palette = get_palette("corporate")           # {"primary": (0x1a,0x36,0x5d), "font_main": "Inter", ...}
```

## 5. Generacion por Formato

### 5.1 Documento (PDF + DOCX)
1. Usar `tools/pdf_generator.py` (`PDFGenerator`) con el estilo visual elegido por el usuario
2. Si estructura **scaffold**: usar `render_scaffold()` con KPIs, tablas, figuras y secciones estructuradas. Usa templates Jinja2 de `templates/pdf/`
3. Si estructura **al vuelo**: usar `render_from_html()` con HTML libre generado en el script. Solo envuelve con CSS, portada opcional, base64 y metadata
4. Ambos modos generan portada automatica, numeracion de paginas, headers, e imagenes embebidas en base64
5. Generar script: `output/[ANALISIS_DIR]/scripts/generate_pdf.py` que importe y use `PDFGenerator`
6. Guardar en `output/[ANALISIS_DIR]/report.pdf`
7. `save()` genera automáticamente `report.html` junto al PDF (mismo contenido renderizado). Si por algún motivo no se desea, pasar `also_save_html=False`
8. Generar DOCX: instanciar `DOCXGenerator(style=estilo)` con los MISMOS datos que el PDF. Si scaffold → `render_scaffold()` con los mismos parametros. Si al vuelo → `render_from_markdown()` con el markdown source
9. Guardar en `output/[ANALISIS_DIR]/report.docx`

**Pitfalls DOCX:**
- Imagenes DEBEN ser PNG (no SVG) — python-docx no soporta SVG
- Tablas muy anchas (>7 columnas) pueden desbordarse — dividir o transponer
- No hay paginacion controlable — Word decide los saltos de pagina
- Fuentes: usar fallback Arial/Calibri si la fuente del tema no esta instalada
- **Imagenes inline**: Las secciones HTML (`executive_summary`, `analysis`, etc.) renderizan `<figure>`, `<img>`, `<table>`, `<h3>`, `<ul>`, `<ol>`, `<div class="callout">` y `<blockquote>` en su posicion correcta dentro del texto. Las imagenes base64 (`data:image/png;base64,...`) se decodifican automaticamente
- **No duplicar imagenes**: Si una imagen ya esta embebida en el HTML de una seccion (ej. `<figure><img src="data:..."/></figure>`), NO pasarla tambien en el parametro `figures=` — se duplicaria en el documento
- Las tablas, listas y subheadings dentro de secciones HTML tambien se renderizan inline en su posicion correcta

### 5.2 Web (Dashboard Interactivo)
**Principio**: HTML autonomo (un solo archivo, sin servidor). CSS inline con `build_css(style, "web")`. Plotly con CDN. Datos embebidos en JSON para funcionamiento offline.

Usar `tools/dashboard_builder.py` (`DashboardBuilder`) para generar dashboards interactivos con filtros, KPI cards dinamicos y tablas ordenables:

```python
from dashboard_builder import DashboardBuilder

db = DashboardBuilder(title="Analisis Q4", style="corporate",
                      subtitle="Periodo Oct-Dic 2025", author="Equipo BI",
                      domain="Ventas", date="2025-12-15")

# 1. Filtros globales (dropdowns y/o date range)
db.add_filter("region", "Region", options=["Norte", "Sur", "Este", "Oeste"])
db.add_filter("periodo", "Periodo", filter_type="date")

# 2. KPI cards con indicador de cambio %
db.add_kpi("revenue", "Ingresos", "1.2M", change=15, prefix="EUR ")
db.add_kpi("clients", "Clientes activos", "8,432", change=-3)

# 3. Secciones con graficas Plotly
fig = px.bar(df, x="region", y="ventas")
apply_plotly_layout(fig, insight="Norte concentra el 45%",
                    context="Ventas por region, Q4 2025")
db.add_chart_section("ventas-region", "Ventas por Region", fig,
                     nav_label="Ventas")

# 4. Tablas ordenables (click-to-sort por columna)
db.add_table("top-products", "Top Productos",
             headers=["Producto", "Ventas", "Margen"],
             rows=[["Widget A", {"display": "1,234", "sort_value": "1234"}, "23%"]])

# 5. Secciones HTML libres (comentarios, callouts)
db.add_html_section("conclusiones", "Conclusiones",
                    "<p>Texto libre con hallazgos...</p>",
                    nav_label="Conclusiones")

# 6. Datos embebidos para filtrado offline
db.set_data({"sales": df.to_dict(orient="records")})

# 7. JS custom para logica de filtrado (updateKPIs, updateCharts, updateTables)
db.add_custom_js("""
function updateKPIs(filters) {
    var data = DASHBOARD_DATA.sales;
    if (filters.region) data = data.filter(r => r.region === filters.region);
    var total = data.reduce((s, r) => s + r.ventas, 0);
    updateKPICard('revenue', formatValue(total, 'currency'));
}
""")

db.save("output/[ANALISIS_DIR]/dashboard.html")
```

**Capacidades del dashboard:**
- **Filtros globales**: Dropdowns y date range que actualizan KPIs, graficas y tablas via `applyFilters()`. El agente define `updateKPIs(filters)`, `updateCharts(filters)` y `updateTables(filters)` en custom JS
- **KPI cards dinamicos**: Valor + cambio % con flecha e indicador de color (verde positivo, rojo negativo). Actualizables via `updateKPICard(id, value, change)`
- **Tablas ordenables**: Click en header para sort asc/desc. Soporte para `sort_value` custom (ej: mostrar "1,234" pero ordenar por 1234)
- **Grid layout**: `width="half"` (2 columnas) o `width="third"` (3 columnas) en `add_chart_section()` y `add_html_section()`. Secciones consecutivas con el mismo ancho se agrupan automaticamente en CSS grid. Default: `"full"` (ancho completo)
- **Formato de numeros**: `formatValue(value, format)` disponible en JS — soporta `'currency'` ($1.2M), `'percent'` (45.1%), `'number'` (2.3K). Usarla en custom JS para evitar reescribir logica de formateo
- **Datos JSON embebidos**: `DASHBOARD_DATA` disponible en JS para filtrado sin servidor
- **Print media**: Oculta filtros y nav, ajusta graficas a 700px, evita page-break dentro de secciones
- **Responsive**: Filtros apilados en movil, tablas con scroll horizontal

**Workflow de generacion:**
1. Generar script: `output/[ANALISIS_DIR]/scripts/generate_web.py --style modern`
2. El script importa `DashboardBuilder` y construye el dashboard programaticamente
3. Guardar en `output/[ANALISIS_DIR]/dashboard.html`

**Pitfalls comunes:**
- `include_plotlyjs=True` duplica la libreria (~3MB) si hay multiples graficas → `DashboardBuilder` ya incluye Plotly via CDN en `<head>` y genera graficas con `full_html=False`
- Sin `<meta name="viewport">` el HTML no es responsive en movil → `DashboardBuilder` lo incluye automaticamente
- Usar los estilos de `styles/web/base.css` que ya tienen nav sticky, hover, filtros, tablas ordenables, print media y responsive → `DashboardBuilder` ensambla CSS via `build_css(style, "web")`
- Solapamiento titulo/leyenda: NUNCA dejar la leyenda en posicion default cuando la grafica tiene titulo con texto descriptivo. Usar `apply_plotly_layout` de `tools/chart_layout.py` o configurar manualmente: title con `y=0.95`, legend horizontal abajo con `y=-0.12`, `margin.t=100` y `margin.b=80`
- **Custom JS**: Las funciones `updateKPIs(filters)`, `updateCharts(filters)` y `updateTables(filters)` se llaman automaticamente cuando cambia un filtro. Si no se definen, los filtros no tendran efecto — el agente DEBE implementarlas via `add_custom_js()` con la logica especifica del analisis
- **Datos embebidos**: Llamar siempre a `db.set_data()` con los datos necesarios para filtrado. Sin datos embebidos, los filtros no pueden funcionar offline. Ver `skills-guides/visualization.md` sec 5.5 para limites de tamano y pre-agregacion
- **Grid layout**: Usar `width="half"` o `width="third"` en secciones consecutivas para layout en 2 o 3 columnas. Util para graficas comparativas (ej: tendencia + composicion lado a lado). No mezclar `"half"` y `"third"` consecutivamente — usar el mismo width en cada grupo
- **formatValue**: Usar `formatValue(value, 'currency')` en custom JS en lugar de escribir logica de formateo manual. Soporta `'currency'`, `'percent'` y `'number'` con abreviaturas K/M/B

### 5.3 PowerPoint
1. Los scripts generados DEBEN importar helpers de `tools/pptx_layout.py`. NUNCA definir `add_slide_header`, `add_text`, `add_kpi_box`, `add_paragraph`, `fill_shape`, `add_rect`, etc. inline — importarlos del modulo
2. NUNCA hardcodear posiciones de contenido — usar `content_area()`, `chart_area()`, `footer_area()` para obtener coordenadas seguras
3. Para graficas: usar `add_image_safe()` que calcula posicion automaticamente dentro del safe area
4. Para notas al pie: usar `add_footer_note()` que posiciona en zona segura
5. Inicializacion: usar `create_presentation(style)` que devuelve `(prs, palette)` con dimensiones estandar (10x7.5")
6. Headers: `add_slide_header(slide, title, subtitle, palette)` retorna `CONTENT_TOP` — usar ese valor como punto de partida para el contenido
7. Colores: usar `rgb_color(palette["primary"])` para convertir tuplas RGB a `RGBColor`
8. Diseño de slides:
   - Portada: titulo del analisis, fecha, dominio
   - Resumen ejecutivo: 3-5 bullets con hallazgos clave (numeros grandes 60-72pt para KPIs via `add_kpi_box`)
   - Slides de datos: una grafica principal por slide (de `output/[ANALISIS_DIR]/assets/`), con titulo como insight
   - Tablas: datos clave en formato tabular cuando las graficas no sean suficientes
   - Conclusiones y recomendaciones: bullets accionables
9. Principios de diseño:
   - Paleta de color del tema elegido (via `get_palette`), no colores hardcodeados
   - Variedad de layouts: no repetir el mismo layout en slides consecutivos
   - Cada slide necesita al menos un elemento visual (grafica, tabla, diagrama, numero destacado)
   - Tipografia: titulos 36-44pt bold, cuerpo 14-16pt
   - Numero orientativo de slides: 8-12 para ejecutiva, 15-20 para detallada
10. Generar script: `output/[ANALISIS_DIR]/scripts/generate_pptx.py --style corporate`
11. Guardar en `output/[ANALISIS_DIR]/presentation.pptx`

**Slides con imagen + panel lateral:**
- Usar `add_image_with_aspect(slide, img_path, left, top, max_width, max_height)` que retorna `(actual_w, actual_h)` reales tras preservar aspect ratio
- Usar la constante `PANEL_GAP` (0.3") como separacion estandar entre imagen y panel lateral
- Calcular posicion del panel: `panel_left = left + actual_w + PANEL_GAP`

**Pitfalls comunes:**
- **Aspect ratio**: NUNCA pasar width Y height a `slide.shapes.add_picture()` directamente — siempre usar `add_image_with_aspect()` o `add_image_safe()` que preservan proporciones. Las graficas matplotlib landscape (18x7) se distorsionan si se fuerzan a areas cuadradas
- Las imagenes deben ser **PNG** (no SVG) — python-pptx no soporta SVG. Guardar graficas como PNG en `output/[ANALISIS_DIR]/assets/`
- python-pptx no soporta markdown — el texto debe formatearse con `runs` (negrita, cursiva, color via `run.font`)
- Usar `get_palette(style)` para colores de shapes y fonts, nunca hardcodear valores RGB
- Overflow: NUNCA colocar elementos debajo de CONTENT_BOTTOM (7.3"). Usar `check_bounds()` para validar posiciones custom. Para graficas usar `add_image_safe()` que calcula automaticamente
- Clearance header: El contenido SIEMPRE empieza en CONTENT_TOP (1.3"), nunca mas arriba. `add_slide_header()` retorna este valor
- Helpers inline: NUNCA redefinir `add_slide_header`, `add_text`, `add_kpi_box`, etc. en el script. Importar de `tools/pptx_layout`

### 5.4 Markdown (siempre generado)
Se genera automaticamente en todos los analisis, sin necesidad de que el usuario lo seleccione.
1. Escribir .md directo con:
   - Tablas markdown para datos tabulares
   - Bloques mermaid para diagramas de flujo o relaciones
   - Referencias a graficas en `output/[ANALISIS_DIR]/assets/`
2. Guardar en `output/[ANALISIS_DIR]/report.md`

## 6. Reasoning

Generar reasoning en `output/[ANALISIS_DIR]/reasoning/` en tres formatos (.md, .pdf, .html) — y .docx si el usuario selecciono "Documento". Cuando se genera DOCX, usar `--docx` en `md_to_report.py`:
```bash
python tools/md_to_report.py reasoning.md --style corporate --cover --docx
```

Documentando:
- Formato(s) generado(s) y justificacion
- Estructura elegida y por que
- Datos utilizados y sus fuentes
- Decisiones de diseno
- Rutas de todos los archivos generados

## 7. Entrega

Reportar en el chat:
- Formato(s) generado(s)
- Ruta(s) de los archivos
- Vista previa del contenido (resumen ejecutivo)
- Instrucciones para abrir/usar el deliverable
