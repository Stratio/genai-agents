# Guía de Generación Web (Dashboard Interactivo)

Referencia operativa para el pipeline de dashboard web dentro de `/report`.

> **Idioma**: Todos los ejemplos de código omiten `lang=` y `labels=` por brevedad. En invocaciones reales, **pasar siempre `lang="<código_idioma_usuario>"` a `DashboardBuilder(...)`** para que el chrome UI (Filters/All/Clear filters/KPIs/footer, atributo HTML `lang`) coincida con el idioma del usuario. Ver sec 3.1 de `SKILL.md` para las reglas de resolución y claves del catálogo.

## Principio

HTML autónomo (un solo archivo, sin servidor). CSS inline con `build_css(style, "web")`. Plotly con CDN. Datos embebidos en JSON para funcionamiento offline.

## DashboardBuilder

Usar `tools/dashboard_builder.py` (`DashboardBuilder`) para generar dashboards interactivos con filtros, KPI cards dinámicos y tablas ordenables:

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

db.save("output/[ANALISIS_DIR]/<slug>-dashboard.html")  # <slug> = parte descriptiva de [ANALISIS_DIR] tras el timestamp — ver SKILL.md §1.1
```

## Capacidades del Dashboard

- **Filtros globales**: Dropdowns y date range que actualizan KPIs, gráficas y tablas vía `applyFilters()`. El agente define `updateKPIs(filters)`, `updateCharts(filters)` y `updateTables(filters)` en custom JS
- **KPI cards dinámicos**: Valor + cambio % con flecha e indicador de color (verde positivo, rojo negativo). Actualizables vía `updateKPICard(id, value, change)`
- **Tablas ordenables**: Click en header para sort asc/desc. Soporte para `sort_value` custom (ej: mostrar "1,234" pero ordenar por 1234)
- **Grid layout**: `width="half"` en `add_html_section()` para colocar contenido HTML en 2 columnas. Secciones consecutivas half-width se agrupan automáticamente en CSS grid. Las gráficas Plotly (`add_chart_section()`) son siempre full-width para que los títulos insight-style y la toolbar se muestren correctamente
- **Formato de números**: `formatValue(value, format)` disponible en JS — soporta `'currency'` ($1.2M), `'percent'` (45.1%), `'number'` (2.3K). Usarla en custom JS para evitar reescribir lógica de formateo
- **Datos JSON embebidos**: `DASHBOARD_DATA` disponible en JS para filtrado sin servidor
- **Print media**: Oculta filtros y nav, ajusta gráficas a 700px, evita page-break dentro de secciones
- **Responsive**: Filtros apilados en móvil, tablas con scroll horizontal

## Workflow de Generación

1. Generar script: `output/[ANALISIS_DIR]/scripts/generate_web.py --style modern`
2. El script importa `DashboardBuilder` y construye el dashboard programáticamente
3. Guardar en `output/[ANALISIS_DIR]/<slug>-dashboard.html`

## Pitfalls Comunes

- `include_plotlyjs=True` duplica la librería (~3MB) si hay múltiples gráficas → `DashboardBuilder` ya incluye Plotly vía CDN en `<head>` y genera gráficas con `full_html=False`
- Sin `<meta name="viewport">` el HTML no es responsive en móvil → `DashboardBuilder` lo incluye automáticamente
- Usar los estilos de `styles/web/base.css` que ya tienen nav sticky, hover, filtros, tablas ordenables, print media y responsive → `DashboardBuilder` ensambla CSS vía `build_css(style, "web")`
- Solapamiento título/leyenda: NUNCA dejar la leyenda en posición default cuando la gráfica tiene título con texto descriptivo. Usar `apply_plotly_layout` de `tools/chart_layout.py` o configurar manualmente: title con `y=0.95`, legend horizontal abajo con `y=-0.12`, `margin.t=100` y `margin.b=80`
- **Custom JS**: Las funciones `updateKPIs(filters)`, `updateCharts(filters)` y `updateTables(filters)` se llaman automáticamente cuando cambia un filtro. Si no se definen, los filtros no tendrán efecto — el agente DEBE implementarlas vía `add_custom_js()` con la lógica específica del análisis
- **Datos embebidos**: Llamar siempre a `db.set_data()` con los datos necesarios para filtrado. Sin datos embebidos, los filtros no pueden funcionar offline. Ver `skills-guides/visualization.md` sec 5.5 para limites de tamaño y pre-agregacion
- **Grid layout**: Las gráficas Plotly son siempre full-width (no aceptan parámetro `width`). Solo `add_html_section()` soporta `width="half"` para contenido HTML ligero en 2 columnas (ej: callouts, tablas de resumen, texto comparativo). No usar grid para gráficas — los títulos insight-style desbordan en contenedores estrechos
- **formatValue**: Usar `formatValue(value, 'currency')` en custom JS en lugar de escribir lógica de formateo manual. Soporta `'currency'`, `'percent'` y `'number'` con abreviaturas K/M/B
