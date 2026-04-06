# Guia Compartida: Visualizacion y Data Storytelling

Principios compartidos por `/analyze` y `/report`.

## 1. Seleccion de Tipo de Grafica

Elegir segun la pregunta analitica:

| Pregunta analitica | Tipo recomendado | Evitar |
|---|---|---|
| Composicion (partes de un todo) | Stacked bar, treemap, pie (<=5 categorias) | Pie con >5 categorias |
| Comparacion entre categorias | Bar chart (horizontal si nombres largos) | Line chart |
| Tendencia temporal | Line chart, area chart | Bar chart (salvo periodos discretos) |
| Distribucion | Histograma, box plot, violin | Pie chart |
| Correlacion | Scatter plot, heatmap | Bar chart |
| Ranking | Bar chart horizontal ordenado | Tabla sin ordenar |
| Geografico | Mapa coropletico | Tablas con codigos de region |
| KPIs destacados | Cards con valor + cambio % + sparkline | Solo numeros en texto |

## 2. Principios de Visualizacion

- Max 5-7 elementos por grafica (agrupar en "Otros" si hay mas)
- Siempre titulo descriptivo + subtitulo con periodo/filtro
- Eje Y comenzar en 0 para barras (evitar manipulacion visual)
- Colores coherentes con el tema elegido (via `get_palette()`, nunca hardcodear)
- **Transparencia**: Para colores con alpha (bandas de confianza, fill_between, areas superpuestas), usar `to_rgba(color, alpha)` de `tools/chart_layout.py`. Acepta hex (`"#1a365d"`) o tupla RGB y devuelve `"rgba(R,G,B,A)"` compatible con Plotly y matplotlib. **NUNCA** concatenar alpha a hex (`"#1a365d80"`) — Plotly lo rechaza
- Anotaciones para puntos notables (picos, caidas, anomalias)
- **Accesibilidad**: Usar paletas colorblind-friendly, no depender solo del color (usar formas/patrones), texto alternativo en imagenes
- **Backend sin display**: Usar `matplotlib.use('Agg')` al inicio del script y `bbox_inches='tight'` en `savefig()`. Si la imagen no renderiza, fallback a SVG
- **Layout anti-solapamiento**: Titulo como insight arriba, contexto como subtitulo, leyenda posicionada debajo del grafico o a la derecha exterior. Usar `tools/chart_layout.py` (`apply_chart_layout` / `apply_plotly_layout`) para layout estandar. **NUNCA** `fig.tight_layout()` despues de `fig.suptitle()` — usar `fig.subplots_adjust()`
- **Figsize para PDF/HTML**: Usar `figsize=(7, 4.5)` como maximo para graficas individuales (el area imprimible del A4 con los margenes por defecto es ~160mm ≈ 6.3"). Para subplots de 2 columnas usar `figsize=(12, 4.5)`. Exceder estas dimensiones provoca desbordamiento en WeasyPrint porque `md_to_report.py` convierte `![alt](img.png)` en `<p><img>` (no `<figure>`), sin CSS de contencion de ancho.
- **Escalas dispares**: Antes de graficar multiples series en el mismo eje, verificar si las magnitudes difieren por mas de 3x. Si es asi, usar subplots con escalas Y independientes en lugar de eje compartido. Para barras con multiples series, usar barras agrupadas (dodge), nunca superponer con alpha. **Checklist obligatorio antes de graficar series juntas:**
  1. Calcular `max(serie_A) / max(serie_B)`. Si ratio > 3 → subplots separados con escalas Y independientes
  2. Calcular rango de variacion de cada serie (`max - min`). Si difieren por mas de 10x → las barras agrupadas son engañosas (una serie parece plana). Separar en subplots o usar indices (base 100)
  3. Media movil: solo anadirla si aporta informacion visual. Si la media movil es casi identica a la serie original (ventana pequena, serie suave), NO anadirla — genera lineas superpuestas que confunden sin aportar insight
  4. Barras agrupadas comparativas: si los valores de una categoria oscilan 5pp y la otra 50pp, las barras de la primera se ven planas. Usar subplots separados o normalizar ambas a indice

## 3. Data Storytelling

Estructura narrativa para presentar hallazgos (no solo secuencial):

1. **Hook**: El dato mas impactante o sorprendente primero — capturar atencion
2. **Contexto**: Por que importa, cual era la situacion previa o el objetivo
3. **Hallazgos**: De lo general a lo especifico, cada uno con su "so what"
4. **Tension**: Que no encaja, que es sorprendente, que requiere atencion urgente
5. **Resolucion**: Recomendaciones concretas con impacto estimado

**Principios:**
- Cada seccion del reporte debe contar una historia, no solo mostrar datos
- Titulos de graficos como insights ("La region Norte concentra el 45%"), no descripciones ("Ventas por region")
- **Verificacion titulo-grafica obligatoria**: Antes de finalizar una grafica, verificar que el patron visual que se ve en el grafico corresponde con el insight del titulo. Errores comunes:
  - Titulo dice "trayectorias divergentes" pero las lineas se cruzan multiples veces → el patron real es volatilidad cruzada, no divergencia
  - Titulo dice "estabilidad" pero el eje Y amplifica variaciones pequenas → ajustar escala o reformular insight
  - Titulo destaca un patron de una serie pero la grafica muestra otra serie que domina visualmente → repensar la composicion
- Numeros siempre con contexto comparativo (vs periodo anterior, vs objetivo, vs media)
- No presentar datos sin interpretacion — cada tabla o grafica necesita un parrafo explicativo
- Adaptar nivel de detalle y vocabulario a la audiencia
- **Anomalias conocidas**: Si un dato es anomalia confirmada (ej: primer mes con acumulacion de apertura), excluirlo de las graficas comparativas o marcarlo claramente con anotacion + opacidad reducida. No dejarlo como un punto normal que distorsiona la escala visual y confunde al lector

## 4. Mapping Hallazgos Analiticos → Narrativa

Mapear cada hallazgo a su rol narrativo:

| Tipo de hallazgo | Rol en la narrativa | Ubicacion en reporte |
|-----------------|---------------------|---------------------|
| Insight CRITICO (alto impacto + alta confianza) | **Hook** | Apertura — primer dato mencionado |
| Hipotesis CONFIRMADA (esperada) | **Context / Findings** | Cuerpo — baseline |
| Hipotesis REFUTADA / anomalia | **Tension** | Hallazgos inesperados |
| Recomendacion de alto impacto + alta confianza | **Resolution** | Cierre — call to action |
| Limitacion de datos o analisis | **Caveat** | Metodologia o pie del hallazgo |
| Hallazgo INFORMATIVO (bajo impacto) | **Supporting detail** | Apendice |

**Minimo narrativo**: Hook + al menos 1 Tension + Resolution. Si todo confirma expectativas, buscar el matiz menos obvio para la Tension.

## 5. Dashboard Interactivo

Principios para componer dashboards web con `tools/dashboard_builder.py` (`DashboardBuilder`).

### 5.1 Cuando usar dashboard vs graficas sueltas

| Situacion | Formato recomendado |
|-----------|-------------------|
| El usuario necesita explorar datos por diferentes dimensiones (region, periodo, segmento) | **Dashboard con filtros** |
| Audiencia ejecutiva: resumen de KPIs + 2-3 graficas clave | **Dashboard simple** (KPIs + graficas, sin filtros o con 1 filtro) |
| Informe formal con narrativa extensa y metodologia | **PDF/DOCX** (no dashboard) |
| Hallazgos puntuales sin interactividad necesaria | **Graficas sueltas** en chat o report |

### 5.2 Layout del dashboard

Orden recomendado de secciones (de arriba a abajo):

1. **Portada** (opcional) — titulo, subtitulo, autor, dominio, fecha
2. **Filtros globales** — solo los relevantes para el analisis (ver 5.3)
3. **KPI cards** — 3-6 metricas clave con cambio % vs periodo anterior
4. **Graficas principales** — los hallazgos mas importantes primero (Hook)
5. **Graficas de detalle** — desglose y contexto (Findings)
6. **Tablas ordenables** — datos de soporte para drill-down manual
7. **Conclusiones** (seccion HTML) — resumen y recomendaciones

**Principios de layout:**
- Max 6 KPI cards — mas de 6 diluye la atencion. Priorizar por impacto de negocio
- Alternar graficas y texto — no apilar 5 graficas seguidas sin interpretacion
- Cada seccion con `nav_label` corto (max 2-3 palabras) para la sticky nav
- **Grid multi-columna**: Usar `width="half"` en `add_html_section()` para colocar contenido HTML comparativo lado a lado (2 columnas). Secciones consecutivas half-width se agrupan automaticamente. En movil colapsan a 1 columna. **Las graficas Plotly son siempre full-width** — los titulos insight-style y la toolbar de Plotly necesitan ancho completo para mostrarse correctamente

### 5.3 Filtros: cuando y cuales

| Tipo de datos | Filtro recomendado | Ejemplo |
|--------------|-------------------|---------|
| Dimension categorica con <=15 valores | **Dropdown** (`filter_type="select"`) | Region, Segmento, Canal |
| Dimension temporal | **Date range** (`filter_type="date"`) | Periodo de analisis |
| Dimension categorica con >15 valores | No usar filtro — agregar en "Otros" o usar tabla ordenable | SKUs, codigos postales |
| Metrica continua | No usar filtro — usar grafica interactiva (zoom/hover de Plotly) | Importe, cantidad |

**Reglas:**
- Max 3-4 filtros — mas de 4 abruma al usuario y complica el custom JS
- Cada filtro debe afectar al menos 2 secciones del dashboard (si solo afecta a 1, ponerlo como control local de esa seccion)
- Siempre incluir "Todos" como opcion por defecto en dropdowns
- Si hay filtro de fecha, poblar `start`/`end` con el rango real de los datos

### 5.4 Tablas ordenables vs graficas

| Usar tabla ordenable cuando... | Usar grafica cuando... |
|-------------------------------|----------------------|
| El usuario necesita buscar valores especificos (ej: "cuanto vendio el producto X") | La pregunta es sobre patrones (tendencia, concentracion, distribucion) |
| Hay >7 dimensiones que comparar | Hay <=7 categorias que comparar visualmente |
| Los datos tienen precision importante (decimales, fechas exactas) | Los ordenes de magnitud importan mas que los valores exactos |
| Es una tabla de referencia/detalle de soporte | Es un hallazgo clave del analisis |

**Tip**: Usar `sort_value` custom para columnas con formato (ej: mostrar "1,234 EUR" pero ordenar por `1234`). Esto permite que la tabla sea legible y funcional al mismo tiempo.

### 5.5 Rendimiento del dashboard

#### Tamano de datos embebidos

| Tamano del dataset | Estrategia | Ejemplo |
|-------------------|-----------|---------|
| <1,000 filas | Embeber directamente con `set_data()` | Ventas mensuales por region (12 meses x 5 regiones = 60 filas) |
| 1,000-10,000 filas | Pre-agregar en pandas antes de embeber. Embeber solo las agregaciones necesarias para KPIs, graficas y tablas | Transacciones diarias de un anio → agregar a semanal por segmento |
| >10,000 filas | Agregar en MCP (`query_data`). Embeber solo el resumen. Nunca traer detalle transaccional al dashboard | Millones de transacciones → top 20 productos, tendencia mensual, KPIs globales |

**Regla**: El JSON embebido en `DASHBOARD_DATA` no deberia superar ~500 KB. Mas de eso ralentiza la carga inicial del HTML.

#### Limites por componente

| Componente | Limite recomendado | Si se excede |
|-----------|-------------------|-------------|
| Line chart | <500 puntos por serie | Downsample: agregar a granularidad mayor (diario → semanal) |
| Bar chart | <50 categorias | Agrupar en "Otros" o usar top-N + "Resto" |
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
