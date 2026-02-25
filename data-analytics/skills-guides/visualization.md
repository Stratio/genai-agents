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
- Anotaciones para puntos notables (picos, caidas, anomalias)
- **Accesibilidad**: Usar paletas colorblind-friendly, no depender solo del color (usar formas/patrones), texto alternativo en imagenes
- **Layout anti-solapamiento**: Titulo como insight arriba, contexto como subtitulo, leyenda posicionada debajo del grafico o a la derecha exterior. Usar `tools/chart_layout.py` (`apply_chart_layout` / `apply_plotly_layout`) para layout estandar. **NUNCA** `fig.tight_layout()` despues de `fig.suptitle()` — usar `fig.subplots_adjust()`
- **Figsize para PDF/HTML**: Usar `figsize=(7, 4.5)` como maximo para graficas individuales (el area imprimible del A4 con los margenes por defecto es ~160mm ≈ 6.3"). Para subplots de 2 columnas usar `figsize=(12, 4.5)`. Exceder estas dimensiones provoca desbordamiento en WeasyPrint porque `md_to_report.py` convierte `![alt](img.png)` en `<p><img>` (no `<figure>`), sin CSS de contencion de ancho.
- **Escalas dispares**: Antes de graficar multiples series en el mismo eje, verificar si las magnitudes difieren por mas de 3x. Si es asi, usar subplots con escalas Y independientes en lugar de eje compartido. Para barras con multiples series, usar barras agrupadas (dodge), nunca superponer con alpha.

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
- Numeros siempre con contexto comparativo (vs periodo anterior, vs objetivo, vs media)
- No presentar datos sin interpretacion — cada tabla o grafica necesita un parrafo explicativo
- Adaptar nivel de detalle y vocabulario a la audiencia

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
