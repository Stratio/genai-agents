# Guía Compartida: Visualización y Data Storytelling

Principios compartidos por `/analyze` (fase analítica y su sub-guía de empaquetado `report/report.md`).

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
- Colores coherentes con el tema elegido (vía `get_palette()`, nunca hardcodear)
- **Transparencia**: Para colores con alpha (bandas de confianza, fill_between, areas superpuestas), usar `to_rgba(color, alpha)` de `skills/analyze/report/tools/chart_layout.py`. Acepta hex (`"#1a365d"`) o tupla RGB y devuelve `"rgba(R,G,B,A)"` compatible con Plotly y matplotlib. **NUNCA** concatenar alpha a hex (`"#1a365d80"`) — Plotly lo rechaza
- Anotaciones para puntos notables (picos, caidas, anomalías)
- **Accesibilidad**: Usar paletas colorblind-friendly, no depender solo del color (usar formas/patrones), texto alternativo en imágenes
- **Backend sin display**: Usar `matplotlib.use('Agg')` al inicio del script y `bbox_inches='tight'` en `savefig()`. Si la imagen no renderiza, fallback a SVG
- **Layout anti-solapamiento**: Título como insight arriba, contexto como subtítulo, leyenda posicionada debajo del gráfico o a la derecha exterior. Usar `skills/analyze/report/tools/chart_layout.py` (`apply_chart_layout` / `apply_plotly_layout`) para layout estándar. **NUNCA** `fig.tight_layout()` después de `fig.suptitle()` — usar `fig.subplots_adjust()`
- **Figsize para PDF/HTML**: Usar `figsize=(7, 4.5)` como máximo para gráficas individuales (el área imprimible del A4 con los márgenes por defecto es ~160mm ≈ 6.3"). Para subplots de 2 columnas usar `figsize=(12, 4.5)`. Exceder estas dimensiones provoca desbordamiento en WeasyPrint porque `skills/analyze/report/tools/md_to_report.py` convierte `![alt](img.png)` en `<p><img>` (no `<figure>`), sin CSS de contención de ancho.
- **Escalas dispares**: Antes de graficar múltiples series en el mismo eje, verificar si las magnitudes difieren por más de 3x. Si es así, usar subplots con escalas Y independientes en lugar de eje compartido. Para barras con múltiples series, usar barras agrupadas (dodge), nunca superponer con alpha. **Checklist obligatorio antes de graficar series juntas:**
  1. Calcular `max(serie_A) / max(serie_B)`. Si ratio > 3 → subplots separados con escalas Y independientes
  2. Calcular rango de variación de cada serie (`max - min`). Si difieren por más de 10x → las barras agrupadas son engañosas (una serie parece plana). Separar en subplots o usar índices (base 100)
  3. Media móvil: solo añadirla si aporta información visual. Si la media móvil es casi idéntica a la serie original (ventana pequeña, serie suave), NO añadirla — genera líneas superpuestas que confunden sin aportar insight
  4. Barras agrupadas comparativas: si los valores de una categoría oscilan 5pp y la otra 50pp, las barras de la primera se ven planas. Usar subplots separados o normalizar ambas a índice

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

Principios para componer dashboards web con `skills/analyze/report/tools/dashboard_builder.py` (`DashboardBuilder`).

### 5.1 Cuándo usar dashboard vs gráficas sueltas

| Situación | Formato recomendado |
|-----------|-------------------|
| El usuario necesita explorar datos por diferentes dimensiones (región, periodo, segmento) | **Dashboard con filtros** |
| Audiencia ejecutiva: resumen de KPIs + 2-3 gráficas clave | **Dashboard simple** (KPIs + gráficas, sin filtros o con 1 filtro) |
| Informe formal con narrativa extensa y metodología | **PDF/DOCX** (no dashboard) |
| Hallazgos puntuales sin interactividad necesaria | **Gráficas sueltas** en chat o report |

### 5.2 Layout del dashboard

Orden recomendado de secciones (de arriba a abajo):

1. **Portada** (opcional) — título, subtítulo, autor, dominio, fecha
2. **Filtros globales** — solo los relevantes para el análisis (ver 5.3)
3. **KPI cards** — 3-6 métricas clave con cambio % vs periodo anterior
4. **Gráficas principales** — los hallazgos más importantes primero (Hook)
5. **Gráficas de detalle** — desglose y contexto (Findings)
6. **Tablas ordenables** — datos de soporte para drill-down manual
7. **Conclusiones** (sección HTML) — resumen y recomendaciones

**Principios de layout:**
- Max 6 KPI cards — más de 6 diluye la atención. Priorizar por impacto de negocio
- Alternar gráficas y texto — no apilar 5 gráficas seguidas sin interpretación
- Cada sección con `nav_label` corto (max 2-3 palabras) para la sticky nav
- **Grid multi-columna**: Usar `width="half"` en `add_html_section()` para colocar contenido HTML comparativo lado a lado (2 columnas). Secciones consecutivas half-width se agrupan automáticamente. En móvil colapsan a 1 columna. **Las gráficas Plotly son siempre full-width** — los títulos insight-style y la toolbar de Plotly necesitan ancho completo para mostrarse correctamente

### 5.3 Filtros: cuando y cuales

| Tipo de datos | Filtro recomendado | Ejemplo |
|--------------|-------------------|---------|
| Dimensión categórica con <=15 valores | **Dropdown** (`filter_type="select"`) | Región, Segmento, Canal |
| Dimensión temporal | **Date range** (`filter_type="date"`) | Periodo de análisis |
| Dimensión categórica con >15 valores | No usar filtro — agregar en "Otros" o usar tabla ordenable | SKUs, códigos postales |
| Métrica continua | No usar filtro — usar gráfica interactiva (zoom/hover de Plotly) | Importe, cantidad |

**Reglas:**
- Max 3-4 filtros — más de 4 abruma al usuario y complica el custom JS
- Cada filtro debe afectar al menos 2 secciones del dashboard (si solo afecta a 1, ponerlo como control local de esa sección)
- Siempre incluir "Todos" como opción por defecto en dropdowns
- Si hay filtro de fecha, poblar `start`/`end` con el rango real de los datos

### 5.4 Tablas ordenables vs gráficas

| Usar tabla ordenable cuando... | Usar gráfica cuando... |
|-------------------------------|----------------------|
| El usuario necesita buscar valores específicos (ej: "cuanto vendio el producto X") | La pregunta es sobre patrones (tendencia, concentración, distribución) |
| Hay >7 dimensiones que comparar | Hay <=7 categorías que comparar visualmente |
| Los datos tienen precisión importante (decimales, fechas exactas) | Los ordenes de magnitud importan más que los valores exactos |
| Es una tabla de referencia/detalle de soporte | Es un hallazgo clave del análisis |

**Tip**: Usar `sort_value` custom para columnas con formato (ej: mostrar "1,234 EUR" pero ordenar por `1234`). Esto permite que la tabla sea legible y funcional al mismo tiempo.

### 5.5 Rendimiento del dashboard

#### Tamaño de datos embebidos

| Tamaño del dataset | Estrategia | Ejemplo |
|-------------------|-----------|---------|
| <1,000 filas | Embeber directamente con `set_data()` | Ventas mensuales por región (12 meses x 5 regiones = 60 filas) |
| 1,000-10,000 filas | Pre-agregar en pandas antes de embeber. Embeber solo las agregaciones necesarias para KPIs, gráficas y tablas | Transacciones diarias de un año → agregar a semanal por segmento |
| >10,000 filas | Agregar en MCP (`query_data`). Embeber solo el resumen. Nunca traer detalle transaccional al dashboard | Millones de transacciones → top 20 productos, tendencia mensual, KPIs globales |

**Regla**: El JSON embebido en `DASHBOARD_DATA` no debería superar ~500 KB. Más de eso ralentiza la carga inicial del HTML.

#### Limites por componente

| Componente | Limite recomendado | Si se excede |
|-----------|-------------------|-------------|
| Line chart | <500 puntos por serie | Downsample: agregar a granularidad mayor (diario → semanal) |
| Bar chart | <50 categorías | Agrupar en "Otros" o usar top-N + "Resto" |
| Tabla ordenable | <200 filas | Mostrar top-N con nota "mostrando los N principales". Para detalle completo, exportar CSV |
| KPI cards | 3-6 | Priorizar por impacto de negocio (ya cubierto en 5.2) |
| Filtros | 3-4 | Ya cubierto en 5.3 |

#### Pre-agregacion en pandas

Antes de llamar a `set_data()`, agregar los datos al nivel necesario para cada componente del dashboard:

```python
# NO: embeber 50,000 transacciones
db.set_data({"transactions": df.to_dict(orient="records")})  # ~5 MB

# SI: pre-agregar para cada componente
data = {
    "monthly": df.groupby("month").agg({"revenue": "sum", "orders": "count"}).reset_index().to_dict(orient="records"),
    "by_region": df.groupby("region").agg({"revenue": "sum"}).reset_index().to_dict(orient="records"),
    "top_products": df.groupby("product").agg({"revenue": "sum"}).nlargest(20, "revenue").reset_index().to_dict(orient="records"),
}
db.set_data(data)  # ~2 KB
```
