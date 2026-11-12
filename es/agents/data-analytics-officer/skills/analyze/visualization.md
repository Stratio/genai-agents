# Guía Compartida: Visualización y Data Storytelling

Principios compartidos por las fases analítica y de entrega de `/analyze`. Los patrones específicos de composición, filtros, tablas ordenables y performance de dashboards viven en `analytical-dashboard.md` (esta skill).

## 1. Selección de Tipo de Gráfica

Elegir según la pregunta analítica:

| Pregunta analítica | Tipo recomendado | Evitar |
|---|---|---|
| Composición (partes de un todo) | Stacked bar, treemap, pie (<=5 categorías) | Pie con >5 categorías |
| Comparación entre categorías | Bar chart (horizontal si nombres largos) | Line chart |
| Tendencia temporal | Line chart, área chart | Bar chart (salvo periodos discretos) |
| Distribución | Histograma, box plot, violin | Pie chart |
| Correlación | Scatter plot, heatmap | Bar chart |
| Ranking | Bar chart horizontal ordenado | Tabla sin ordenar |
| Geográfico | Mapa coroplético | Tablas con códigos de región |
| KPIs destacados | Cards con valor + cambio % + sparkline | Solo números en texto |

## 2. Principios de Visualización

- Max 5-7 elementos por gráfica (agrupar en "Otros" si hay más)
- Siempre título descriptivo + subtítulo con periodo/filtro
- Eje Y comenzar en 0 para barras (evitar manipulación visual)
- Colores coherentes con el tema de marca activo — usar la paleta `chart_categorical` que proporciona `brand-kit` (ver AGENTS.md §8.3), nunca hardcodear
- **Transparencia**: Para colores con alpha (bandas de confianza, fill_between, areas superpuestas), usar `to_rgba(color, alpha)` de `skills/analyze/chart_layout.py`. Acepta hex (`"#1a365d"`) o tupla RGB y devuelve `"rgba(R,G,B,A)"` compatible con Plotly y matplotlib. **NUNCA** concatenar alpha a hex (`"#1a365d80"`) — Plotly lo rechaza
- Anotaciones para puntos notables (picos, caidas, anomalías)
- **Accesibilidad**: Usar paletas colorblind-friendly, no depender solo del color (usar formas/patrones), texto alternativo en imágenes
- **Backend sin display**: Usar `matplotlib.use('Agg')` al inicio del script y `bbox_inches='tight'` en `savefig()`. Si la imagen no renderiza, fallback a SVG
- **Layout anti-solapamiento**: Título como insight arriba, contexto como subtítulo, leyenda posicionada debajo del gráfico o a la derecha exterior. Usar `skills/analyze/chart_layout.py` (`apply_chart_layout` / `apply_plotly_layout`) para layout estándar. **NUNCA** `fig.tight_layout()` después de `fig.suptitle()` — usar `fig.subplots_adjust()`
- **Figsize para PDF/HTML**: Usar `figsize=(7, 4.5)` como máximo para gráficas individuales (área imprimible de A4 ≈ 160mm ≈ 6.3"). Para subplots de 2 columnas usar `figsize=(12, 4.5)`. Las skills writer aplican su propia contención de ancho vía sus templates — mantenerse dentro de estos tamaños asegura legibilidad en PDF, DOCX y HTML.
- **Escalas dispares**: Antes de graficar múltiples series en el mismo eje, verificar si las magnitudes difieren por más de 3x. Si es así, usar subplots con escalas Y independientes en lugar de eje compartido. Para barras con múltiples series, usar barras agrupadas (dodge), nunca superponer con alpha. **Checklist obligatorio antes de graficar series juntas:**
  1. Calcular `max(serie_A) / max(serie_B)`. Si ratio > 3 → subplots separados con escalas Y independientes
  2. Calcular rango de variación de cada serie (`max - min`). Si difieren por más de 10x → las barras agrupadas son engañosas (una serie parece plana). Separar en subplots o usar índices (base 100)
  3. Media móvil: solo añadirla si aporta información visual. Si la media móvil es casi idéntica a la serie original (ventana pequeña, serie suave), NO añadirla — genera líneas superpuestas que confunden sin aportar insight
  4. Barras agrupadas comparativas: si los valores de una categoría oscilan 5pp y la otra 50pp, las barras de la primera se ven planas. Usar subplots separados o normalizar ambas a índice

**Implementación obligatoria**: Siempre que un script Python pinte múltiples series en el mismo eje, incluir el siguiente helper y llamarlo antes de `px.bar` / `px.line`. Si devuelve `False`, sustituir el gráfico combinado por `make_subplots(rows=N, cols=1)` — una serie por fila — o normalizar ambas series a índice base 100 cuando el foco es la comparación relativa.

```python
def _escalas_compatibles(series: dict) -> bool:
    """Devuelve True si las series comparten una escala comparable (eje único es seguro).
    series: {etiqueta: pd.Series, ...}
    Umbrales de visualization.md sec 2: ratio-máximos <= 3, ratio-rangos <= 10.
    """
    maxs = {k: v.abs().max() for k, v in series.items()}
    rangos = {k: v.max() - v.min() for k, v in series.items()}
    ratio_max = max(maxs.values()) / (min(maxs.values()) + 1e-9)
    ratio_rango = max(rangos.values()) / (min(rangos.values()) + 1e-9)
    return ratio_max <= 3 and ratio_rango <= 10

# Ejemplo: gráfico MoM con dos segmentos de negocio
# series = {"Comercial": df_com["MoM_Growth"], "Empresas": df_emp["MoM_Growth"]}
# if not _escalas_compatibles(series):
#     # construir make_subplots(rows=2, cols=1) en lugar de un único px.bar
```

## 3. Data Storytelling

Estructura narrativa para presentar hallazgos (no solo secuencial):

1. **Hook**: El dato más impactante o sorprendente primero — capturar atención
2. **Contexto**: Por que importa, cuál era la situación previa o el objetivo
3. **Hallazgos**: De lo general a lo específico, cada uno con su "so what"
4. **Tensión**: Que no encaja, que es sorprendente, que requiere atención urgente
5. **Resolución**: Recomendaciones concretas con impacto estimado

**Principios:**
- Cada sección del reporte debe contar una historia, no solo mostrar datos
- Títulos de gráficos como insights ("La región Norte concentra el 45%"), no descripciones ("Ventas por región")
- **Verificación título-gráfica obligatoria**: Antes de finalizar una gráfica, verificar que el patrón visual que se ve en el gráfico corresponde con el insight del título. Errores comunes:
  - Título dice "trayectorias divergentes" pero las líneas se cruzan múltiples veces → el patrón real es volatilidad cruzada, no divergencia
  - Título dice "estabilidad" pero el eje Y amplifica variaciones pequeñas → ajustar escala o reformular insight
  - Título destaca un patrón de una serie pero la gráfica muestra otra serie que domina visualmente → repensar la composición
- Números siempre con contexto comparativo (vs periodo anterior, vs objetivo, vs media)
- No presentar datos sin interpretación — cada tabla o gráfica necesita un párrafo explicativo
- Adaptar nivel de detalle y vocabulario a la audiencia
- **Anomalías conocidas**: Si un dato es anomalía confirmada (ej: primer mes con acumulación de apertura), excluirlo de las gráficas comparativas o marcarlo claramente con anotación + opacidad reducida. No dejarlo como un punto normal que distorsiona la escala visual y confunde al lector

## 4. Mapping Hallazgos Analíticos → Narrativa

Mapear cada hallazgo a su rol narrativo:

| Tipo de hallazgo | Rol en la narrativa | Ubicación en reporte |
|-----------------|---------------------|---------------------|
| Insight CRITICO (alto impacto + alta confianza) | **Hook** | Apertura — primer dato mencionado |
| Hipótesis CONFIRMADA (esperada) | **Context / Findings** | Cuerpo — baseline |
| Hipótesis REFUTADA / anomalía | **Tensión** | Hallazgos inesperados |
| Recomendación de alto impacto + alta confianza | **Resolution** | Cierre — call to action |
| Limitación de datos o análisis | **Caveat** | Metodología o pie del hallazgo |
| Hallazgo INFORMATIVO (bajo impacto) | **Supporting detail** | Apéndice |

**Mínimo narrativo**: Hook + al menos 1 Tensión + Resolution. Si todo confirma expectativas, buscar el matiz menos obvio para la Tensión.

## 5. Dashboard Interactivo

Para composición, layout, filtros, tablas ordenables, KPI cards y patrones de performance del dashboard, ver [analytical-dashboard.md](analytical-dashboard.md). Esa guía la carga `web-craft` cuando el agente produce un dashboard analítico desde `/analyze` Fase 4.

## 6. Gráficas en el Chat

Una gráfica que se muestra en la conversación (el formato Chat, o una gráfica que el usuario pide en una respuesta) nunca es texto. Una gráfica sencilla es un bloque `chart` que GenAI UI dibuja como gráfica interactiva; cualquier otra es un PNG.

**Gráfica sencilla → bloque `chart`.** Uno de los tipos de abajo, con hasta ~50 filas (un `pinmap` o `map` hasta ~200): escribir un bloque de código con el lenguaje `chart` que contenga un objeto JSON, junto al insight que apoya:

````
```chart
{"type": "bar", "title": "El BAI se mantiene en torno a 80K al mes", "x": "mes", "y": ["bai"], "data": [{"mes": "2023-05", "bai": 81470.07}, {"mes": "2023-06", "bai": 79281.40}]}
```
````

| `type` | Para (§1) | Campos además de `data` |
|---|---|---|
| `bar`, `line`, `area` | Comparación, tendencia | `x`: columna de categorías o periodos; `y`: columna numérica, o una lista para varias series |
| `pie` | Composición, <=5 categorías | `x`: las porciones; `y`: su valor (se dibuja la primera) |
| `waterfall` | Cómo pasa un total de un valor a otro (puente de variaciones) | `x`: los pasos en orden; `y`: la variación de cada paso, positiva o negativa |
| `scatter` | Correlación entre dos columnas numéricas | `x`, `y`: las dos columnas numéricas (se dibuja la primera `y`) |
| `radar` | Perfiles comparados en varias métricas | `x`: los nombres de las métricas; `y`: una columna numérica por perfil |
| `progress` | Un KPI frente a su objetivo | `y`: la columna del KPI, leída de la primera fila; `goal`: el objetivo, > 0 |
| `gauge` | Un KPI sobre tramos con nombre | `y`: la columna del KPI, leída de la primera fila; `segments`: `[{"min": 0, "max": 45, "label": "Bueno"}, …]` que cubran su rango |
| `bubble` | Una dispersión con una tercera medida | `x`, `y` como en `scatter`; `size`: la columna numérica que da tamaño a cada punto |
| `histogram` | Distribución de una medida | `counts`: filas por tramo; `bin_edges`: los límites de los tramos, uno más que `counts`; sin `data` |
| `map` | Un valor por geografía | `region`: `world_countries`, `Spain-communities`, `Spain-provinces` o `United States`; `x`: la columna de las regiones, como códigos ISO (`ES`, `ES-MD`, `ES-M`, `US-CA`); `y`: su valor |
| `pinmap` | Lugares en un mapa | `lat`, `lon`: las columnas de las coordenadas de cada punto |
| `table` | Valores exactos para ordenar y comparar | ninguno: las filas tal cual |

- `title`: el insight (§3), opcional
- `data`: las filas, cada valor un número, un texto o `null`; las columnas `y` números (o `null`). Tomar los valores de los resultados del MCP tal cual, nunca redondeados ni inventados, y ordenar los periodos
- Solo JSON válido (comillas dobles, sin comentarios ni comas finales). Un bloque que GenAI UI no puede dibujar se muestra como código, y el usuario puede descargar cada gráfica como PNG

**Diagrama → bloque `mermaid`.** Un proceso, un flujo, una secuencia, una jerarquía o una línea temporal (flowchart, sequence, Gantt, mindmap…) va en un bloque de código con el lenguaje `mermaid`, que GenAI UI dibuja como diagrama. Una gráfica de datos es un bloque `chart`, no una gráfica de Mermaid (`xychart-beta`, `pie`): solo un bloque `chart` toma sus valores como datos y la dibuja como el resto de gráficas de GenAI UI.

**Cualquier otra gráfica → PNG.** Mapas de calor, diagramas de caja, subplots, anotaciones o más filas:

- **Nunca dibujar una gráfica con caracteres** (`█`, `▇`, `#`, barras ASCII o Unicode, sparklines de texto en un bloque de código). Nadie puede leer valores en ellas y GenAI UI no puede mostrarlas como gráfica. Los valores exactos van en una tabla markdown
- **Dibujarla como PNG** con un script, siguiendo la §2: guardarla en `output/[ANALISIS_DIR]/assets/<nombre_descriptivo>.png` con `dpi=150` y `bbox_inches='tight'`
- **Ejecutar el script.** Un script que dibuja una gráfica no es la gráfica: ejecutarlo en el mismo turno, comprobar que el PNG existe y no está vacío (`ls -l`), y corregirlo y volver a ejecutarlo si falla. Nunca entregar solo el script
- **Nombrar la imagen en la respuesta** por su ruta desde la raíz del proyecto, entre backticks, junto al insight que apoya: `` `output/2026-11-11_1630_bai_mensual/assets/bai_mensual.png` ``. GenAI UI muestra en línea, bajo la respuesta, cada imagen que la respuesta nombra. No usar la sintaxis de imagen de markdown (`![...](...)`): el chat no puede resolver en ella una ruta del workspace
