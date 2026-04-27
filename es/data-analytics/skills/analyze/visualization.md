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
