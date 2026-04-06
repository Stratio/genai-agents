# Guia: Visualizacion y Data Storytelling

Principios compartidos por `/analyze`.

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

## 2. Principios Generales

- Max 5-7 elementos por grafica (agrupar en "Otros" si hay mas)
- Titulo descriptivo como insight + subtitulo con periodo/filtro
- Eje Y comenzar en 0 para barras (evitar manipulacion visual)
- Anotaciones para puntos notables (picos, caidas, anomalias)
- **Accesibilidad**: Paletas colorblind-friendly, no depender solo del color (usar formas/patrones si es posible)
- **Escalas dispares**: Si multiples series difieren por mas de 3x en magnitud, usar subplots con escalas Y independientes en lugar de eje compartido

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

## 4. Mapping Hallazgos → Narrativa

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

## 5. Paleta Corporate

Usar en orden de prioridad:

| Orden | Hex | Nombre | Uso |
|-------|---------|--------|-----|
| 1 | `#1a365d` | Azul oscuro | Primary — serie principal, barras destacadas |
| 2 | `#2b6cb0` | Azul medio | Primary light — serie secundaria |
| 3 | `#3182ce` | Azul claro | Accent — lineas de tendencia, destacados |
| 4 | `#38a169` | Verde | Success — valores positivos, crecimiento |
| 5 | `#d69e2e` | Ambar | Warning — valores de atencion |
| 6 | `#e53e3e` | Rojo | Danger — valores negativos, caidas |
