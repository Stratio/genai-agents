# Guia de Generacion Web (Dashboard Interactivo)

Referencia operativa para el pipeline de dashboard web dentro de `/report`.

## Principio

HTML autonomo (un solo archivo, sin servidor). CSS inline con `build_css(style, "web")`. Plotly con CDN. Datos embebidos en JSON para funcionamiento offline.

## DashboardBuilder

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

## Capacidades del Dashboard

- **Filtros globales**: Dropdowns y date range que actualizan KPIs, graficas y tablas via `applyFilters()`. El agente define `updateKPIs(filters)`, `updateCharts(filters)` y `updateTables(filters)` en custom JS
- **KPI cards dinamicos**: Valor + cambio % con flecha e indicador de color (verde positivo, rojo negativo). Actualizables via `updateKPICard(id, value, change)`
- **Tablas ordenables**: Click en header para sort asc/desc. Soporte para `sort_value` custom (ej: mostrar "1,234" pero ordenar por 1234)
- **Grid layout**: `width="half"` en `add_html_section()` para colocar contenido HTML en 2 columnas. Secciones consecutivas half-width se agrupan automaticamente en CSS grid. Las graficas Plotly (`add_chart_section()`) son siempre full-width para que los titulos insight-style y la toolbar se muestren correctamente
- **Formato de numeros**: `formatValue(value, format)` disponible en JS — soporta `'currency'` ($1.2M), `'percent'` (45.1%), `'number'` (2.3K). Usarla en custom JS para evitar reescribir logica de formateo
- **Datos JSON embebidos**: `DASHBOARD_DATA` disponible en JS para filtrado sin servidor
- **Print media**: Oculta filtros y nav, ajusta graficas a 700px, evita page-break dentro de secciones
- **Responsive**: Filtros apilados en movil, tablas con scroll horizontal

## Workflow de Generacion

1. Generar script: `output/[ANALISIS_DIR]/scripts/generate_web.py --style modern`
2. El script importa `DashboardBuilder` y construye el dashboard programaticamente
3. Guardar en `output/[ANALISIS_DIR]/dashboard.html`

## Pitfalls Comunes

- `include_plotlyjs=True` duplica la libreria (~3MB) si hay multiples graficas → `DashboardBuilder` ya incluye Plotly via CDN en `<head>` y genera graficas con `full_html=False`
- Sin `<meta name="viewport">` el HTML no es responsive en movil → `DashboardBuilder` lo incluye automaticamente
- Usar los estilos de `styles/web/base.css` que ya tienen nav sticky, hover, filtros, tablas ordenables, print media y responsive → `DashboardBuilder` ensambla CSS via `build_css(style, "web")`
- Solapamiento titulo/leyenda: NUNCA dejar la leyenda en posicion default cuando la grafica tiene titulo con texto descriptivo. Usar `apply_plotly_layout` de `tools/chart_layout.py` o configurar manualmente: title con `y=0.95`, legend horizontal abajo con `y=-0.12`, `margin.t=100` y `margin.b=80`
- **Custom JS**: Las funciones `updateKPIs(filters)`, `updateCharts(filters)` y `updateTables(filters)` se llaman automaticamente cuando cambia un filtro. Si no se definen, los filtros no tendran efecto — el agente DEBE implementarlas via `add_custom_js()` con la logica especifica del analisis
- **Datos embebidos**: Llamar siempre a `db.set_data()` con los datos necesarios para filtrado. Sin datos embebidos, los filtros no pueden funcionar offline. Ver `skills-guides/visualization.md` sec 5.5 para limites de tamano y pre-agregacion
- **Grid layout**: Las graficas Plotly son siempre full-width (no aceptan parametro `width`). Solo `add_html_section()` soporta `width="half"` para contenido HTML ligero en 2 columnas (ej: callouts, tablas de resumen, texto comparativo). No usar grid para graficas — los titulos insight-style desbordan en contenedores estrechos
- **formatValue**: Usar `formatValue(value, 'currency')` en custom JS en lugar de escribir logica de formateo manual. Soporta `'currency'`, `'percent'` y `'number'` con abreviaturas K/M/B
