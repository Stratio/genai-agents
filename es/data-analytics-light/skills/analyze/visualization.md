# Guía: Visualización y Data Storytelling

Principios compartidos por `/analyze`.

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

## 2. Principios Generales

- Max 5-7 elementos por gráfica (agrupar en "Otros" si hay más)
- Título descriptivo como insight + subtítulo con periodo/filtro
- Eje Y comenzar en 0 para barras (evitar manipulación visual)
- Anotaciones para puntos notables (picos, caidas, anomalías)
- **Accesibilidad**: Paletas colorblind-friendly, no depender solo del color (usar formas/patrones si es posible)
- **Escalas dispares**: Si múltiples series difieren por más de 3x en magnitud, usar subplots con escalas Y independientes en lugar de eje compartido

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
- Números siempre con contexto comparativo (vs periodo anterior, vs objetivo, vs media)
- No presentar datos sin interpretación — cada tabla o gráfica necesita un párrafo explicativo
- Adaptar nivel de detalle y vocabulario a la audiencia

## 4. Mapping Hallazgos → Narrativa

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

## 5. Paleta Corporate

Usar en orden de prioridad:

| Orden | Hex | Nombre | Uso |
|-------|---------|--------|-----|
| 1 | `#1a365d` | Azul oscuro | Primary — serie principal, barras destacadas |
| 2 | `#2b6cb0` | Azul medio | Primary light — serie secundaria |
| 3 | `#3182ce` | Azul claro | Accent — líneas de tendencia, destacados |
| 4 | `#38a169` | Verde | Success — valores positivos, crecimiento |
| 5 | `#d69e2e` | Ambar | Warning — valores de atención |
| 6 | `#e53e3e` | Rojo | Danger — valores negativos, caidas |
