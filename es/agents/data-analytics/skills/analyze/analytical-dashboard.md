# Dashboard Analítico — Guía

Guía consumida por `web-craft` cuando el agente le pide construir un dashboard interactivo como entregable de un flujo analítico (cargada desde `/analyze` Fase 4 cuando el usuario seleccionó **Dashboard web** como uno de los formatos en §4.1).

Esta guía captura las convenciones que hacen que un dashboard analítico sea reconocible: KPI cards arriba, filtros globales que cascadean sobre todo, tablas de soporte ordenables, gráficas Plotly con títulos-insight y una composición que se lee como análisis y no como marketing. `web-craft` sigue aplicando sus cinco decisiones (tono / pairing tipográfico / paleta / motion / composición) encima de esta guía — los tokens vienen de la skill de theming centralizado elegida en el plan; esta guía aporta los **patrones analíticos**.

## 1. Cuándo aplicar esta guía

Aplicar silenciosamente cuando el agente llame a `web-craft` desde `/analyze` Fase 4 con un entregable Dashboard web Y el usuario no haya señalado libertad de diseño. Saltarse por completo cuando el brief del usuario contiene frases como:

- "rompe el molde", "dashboard creativo", "experimental", "narrativo", "más libre"
- "algo diferente", "fuera del patrón habitual", "dashboard personalizado"

En esos casos `web-craft` opera con sus cinco decisiones desde cero, produciendo un dashboard válido pero sin el layout analítico estándar.

## 2. Layout — 2 columnas, top-down

Orden de secciones recomendado:

1. **Portada (opcional)** — título, subtítulo, autor, dominio, fecha.
2. **Navegación sticky** — un `nav_label` por sección (máx 2-3 palabras cada uno).
3. **Filtros globales** — dropdowns y rangos de fecha (ver §3).
4. **KPI cards** — 3 a 6 métricas clave con cambio vs periodo anterior (ver §4).
5. **Gráficas principales** — los hallazgos más impactantes primero (Hook). Siempre full-width.
6. **Gráficas de detalle** — desglose y contexto (Findings). Pueden ser half-width via grid HTML.
7. **Tablas ordenables** — para drill-down manual (ver §5).
8. **Conclusiones** — sección HTML libre con resumen y recomendaciones.

Principios:

- Máx **6 KPI cards** — más diluye la atención. Priorizar por impacto de negocio.
- Alternar gráficas y texto — no apilar 5 gráficas seguidas sin interpretación.
- Las gráficas Plotly son **siempre full-width**: los títulos insight-style y la toolbar necesitan el espacio.
- Secciones HTML consecutivas con `width="half"` se agrupan en grid de 2 columnas; apilan en móvil.

## 3. Filtros globales — cuándo y cuáles

| Tipo de dato | Filtro | Ejemplo |
|---|---|---|
| Dimensión categórica con ≤15 valores | Dropdown (`<select>`) | Región, Segmento, Canal |
| Dimensión temporal | Date range (dos `<input type="date">`) | Periodo de análisis |
| Dimensión categórica con >15 valores | No usar filtro — agregar en "Otros" o usar tabla ordenable | SKUs, códigos postales |
| Métrica continua | No usar filtro — usar interactividad Plotly (zoom, hover) | Importe, cantidad |

Reglas:

- **Máx 3-4 filtros**. Más abruma al usuario y complica el custom JS.
- Cada filtro debe afectar a **al menos 2 secciones** (KPIs + gráficas o tablas). Si solo afecta a una, ponerlo como control local en esa sección.
- Siempre incluir una opción "Todos" / "All" como defecto en dropdowns.
- Si hay filtro de fecha, poblar `start`/`end` con el rango real de los datos.

Patrón de implementación (vanilla JS — sin framework):

```html
<div class="filters">
  <select data-filter="region">
    <option value="">Todas las regiones</option>
    <option value="north">Norte</option>
    ...
  </select>
  <input type="date" data-filter="from" value="2025-01-01">
  <input type="date" data-filter="until" value="2025-12-31">
</div>

<script>
const filters = {};
document.querySelectorAll('[data-filter]').forEach(el => {
  el.addEventListener('change', () => {
    filters[el.dataset.filter] = el.value;
    applyFilters(filters);
  });
});

function applyFilters(f) {
  updateKPIs(f);
  updateCharts(f);
  updateTables(f);
}
</script>
```

El agente es responsable de implementar `updateKPIs()`, `updateCharts()`, `updateTables()` con la lógica específica del análisis. Sin ellas, los filtros no hacen nada.

**Contrato de datos** — tu HTML debe embeber los slices pre-agregados como un objeto global `DASHBOARD_DATA`; los callbacks de los filtros leen de él y re-renderizan. Patrón de ejemplo (estructura del código que contiene tu HTML — el estilo visual es decisión de web-craft):

```javascript
const DASHBOARD_DATA = {
  sales_by_region: [
    {region: 'north', month: '2025-01', revenue: 420000, orders: 1200},
    {region: 'south', month: '2025-01', revenue: 310000, orders: 980},
    // ...
  ],
  top_products: [ /* ... */ ],
};

function updateKPIs(f) {
  let rows = DASHBOARD_DATA.sales_by_region;
  if (f.region) rows = rows.filter(r => r.region === f.region);
  if (f.from)   rows = rows.filter(r => r.month >= f.from);
  if (f.until)  rows = rows.filter(r => r.month <= f.until);
  const total = rows.reduce((s, r) => s + r.revenue, 0);
  document.querySelector('[data-kpi="revenue"] .kpi-value').textContent = formatValue(total, 'currency');
}
```

`updateCharts()` y `updateTables()` siguen el mismo patrón: leer de `DASHBOARD_DATA`, filtrar, re-renderizar. `web-craft` decide el CSS concreto, las transiciones y el microcopy — el contrato aquí es puramente sobre el flujo de datos.

## 4. KPI cards

Cada KPI card contiene:

- **Etiqueta** (una línea corta).
- **Valor** (periodo actual, formateado con número locale-aware: `1,234` / `1.234` / `1.2M` / `1.2K`).
- **Cambio vs periodo anterior**: flecha (↑ / ↓), porcentaje, color (positivo = `state_ok`, negativo = `state_danger`, neutral = muted).
- Opcional: sparkline pequeño (SVG minimal o barras CSS, sin librería de charts) con los últimos N periodos.

Patrón HTML/CSS:

```html
<div class="kpi-card">
  <div class="kpi-label">Ingresos</div>
  <div class="kpi-value">€ 1.2M</div>
  <div class="kpi-change positive">↑ 15% vs Q3</div>
</div>
```

```css
.kpi-card {
  background: var(--bg-alt);
  border-left: 4px solid var(--primary);
  padding: 1.5rem;
  border-radius: 4px;
}
.kpi-value { font-family: var(--font-display); font-size: 2rem; }
.kpi-change.positive { color: var(--state-ok); }
.kpi-change.negative { color: var(--state-danger); }
```

Helper de formato (vanilla, locale-aware). La moneda es configurable así USD, GBP, MXN, etc. están a un argumento de distancia:

```javascript
function formatValue(v, kind, opts = {}) {
  const lang = document.documentElement.lang;
  if (kind === 'currency') return new Intl.NumberFormat(lang, {style:'currency', currency: opts.currency || 'EUR', notation:'compact'}).format(v);
  if (kind === 'percent')  return new Intl.NumberFormat(lang, {style:'percent', maximumFractionDigits:1}).format(v);
  return new Intl.NumberFormat(lang, {notation:'compact'}).format(v);
}

// Uso: formatValue(1234000, 'currency', {currency: 'USD'}) → "$1.2M"
//      formatValue(0.127, 'percent')                       → "12,7 %" (es) / "12.7%" (en)
```

Cuando el KPI necesita un prefijo/sufijo no monetario (ej. "× 1.2M transacciones", "1.234 kg CO₂"), concatena la unidad en el HTML renderizado junto al número formateado en lugar de sobrecargar `formatValue`.

## 5. Tablas ordenables

Para datos de referencia / drill-down. Click en un `<th>` reordena la columna.

```html
<table class="sortable" data-rows="top-products">
  <thead>
    <tr>
      <th data-sort="text">Producto</th>
      <th data-sort="number">Ventas</th>
      <th data-sort="percent">Margen</th>
    </tr>
  </thead>
  <tbody id="tbody-top-products"></tbody>
</table>
```

- Atributo `data-sort` declara el tipo de columna (`text`, `number`, `date`, `percent`).
- Números mostrados formateados (ej. `"1.234"`) pero ordenados por valor crudo — usar un `data-value` oculto en cada `<td>` o almacenar los números crudos en `DASHBOARD_DATA` y renderizar on-demand.
- Por defecto: sin orden. Click asc, click otra vez desc.
- Usar tablas ordenables cuando el usuario necesita valores exactos o hay >7 dimensiones. Usar gráficas cuando la pregunta es sobre patrones (tendencia, concentración).

## 6. Gráficas — Plotly con títulos-insight

Plotly vía CDN (un único `<script src="https://cdn.plot.ly/plotly-2.x.min.js">` en `<head>`). Figuras embebidas como JSON en `DASHBOARD_DATA`, renderizadas en `DOMContentLoaded` con `Plotly.newPlot()`.

Reglas anti-solapamiento (no negociables):

- Título como **insight** ("Norte concentra el 45%"), no descripción ("Ventas por región").
- Contexto como subtítulo bajo el título ("Q4 2025, por región").
- Leyenda **fuera del área de trazado**: abajo para pocas series, a la derecha exterior para muchas.
- Nunca `fig.tight_layout()` después de `fig.suptitle()` en gráficas matplotlib — usar `fig.subplots_adjust()`. Ver `chart_layout.py` para el helper.
- `figsize=(7, 4.5)` máximo para gráficas individuales; `figsize=(12, 4.5)` para subplots de 2 columnas. Tamaños mayores desbordan el área imprimible cuando las skills writer incluyen la gráfica en un PDF.

Colores: extraer la paleta `chart_categorical` de los tokens de marca (§8). Aplicar vía Plotly `layout.colorway`:

```javascript
Plotly.newPlot(el, data, {
  ...layoutConfig,
  colorway: BRAND_TOKENS.chart_categorical  // array de 5-8 strings hex
});
```

## 7. Rendimiento — presupuesto de datos embebidos

El JSON embebido en `DASHBOARD_DATA` **no debería superar ~500 KB**. Por encima, la carga inicial del HTML se siente lenta.

| Tamaño del dataset | Estrategia |
|---|---|
| <1.000 filas | Embeber directamente |
| 1.000-10.000 filas | Pre-agregar en pandas antes de embeber. Mantener solo lo que necesitan KPIs, gráficas y tablas |
| >10.000 filas | Agregar en MCP vía `query_data`. Embeber solo resúmenes. Nunca enviar detalle transaccional |

Límites por componente:

- Line chart: <500 puntos por serie → downsample a granularidad más gruesa.
- Bar chart: <50 categorías → top-N + "Otros".
- Tabla ordenable: <200 filas → "mostrando top N; detalle completo en exportación CSV".

Ejemplo de pre-agregación (pandas):

```python
# Mal: 50.000 transacciones (~5 MB)
data = {"transactions": df.to_dict(orient="records")}

# Bien: slices pre-agregados (~2 KB)
data = {
  "monthly": df.groupby("month").agg(revenue=("amount","sum"), orders=("id","count")).reset_index().to_dict(orient="records"),
  "by_region": df.groupby("region").agg(revenue=("amount","sum")).reset_index().to_dict(orient="records"),
  "top_products": df.groupby("product").agg(revenue=("amount","sum")).nlargest(20, "revenue").reset_index().to_dict(orient="records"),
}
```

## 8. Integración con tokens de marca

El tema fijado en el plan (ver instrucciones del agente §8.3) produce un bundle de tokens. El dashboard los consume en dos sitios:

**CSS custom properties en `:root`**:

```css
:root {
  --primary: #0a2540;
  --accent:  #d9472b;
  --text:    #1f2937;
  --muted:   #6b7280;
  --rule:    #d1d5db;
  --bg:      #ffffff;
  --bg-alt:  #f3f4f6;
  --state-ok:     #047857;
  --state-warn:   #b45309;
  --state-danger: #b91c1c;
  --font-display: 'Fraunces', Georgia, serif;
  --font-body:    'Inter', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', Consolas, monospace;
}
```

**Plotly `layout.colorway`**: usar `chart_categorical` del bundle de tokens (5-8 colores hex ordenados). Mantiene las gráficas en conversación con el resto del artefacto.

Si el tema declara extensiones opcionales (`motion_budget`, `radius`, `dark_mode`, `chart_sequential`), respetarlas. `motion_budget` controla el CSS de transiciones; `dark_mode` habilita `@media (prefers-color-scheme: dark)`; `chart_sequential` es para heatmaps.

## 9. Motion

Solo CSS, sin JS. Usar keyframes con prefijo `dashboard-*` para evitar colisiones. Respetar `prefers-reduced-motion: reduce` cancelando animaciones.

| Budget (de los tokens de marca) | Efecto |
|---|---|
| `none` | Sin motion extra. Dashboards estáticos, para imprimir, contextos donde el movimiento distrae |
| `minimal` (por defecto) | 320 ms `dashboard-fade-in` en KPI cards y secciones al montar |
| `expressive` | `dashboard-rise` escalonado en KPI cards (80 ms por card), reveal de sección, card hover lift |

Mantener el motion de carga bajo ~500 ms total. Plotly ejecuta sus propias animaciones — no adjuntar CSS a descendientes de `.js-plotly-plot`.

```css
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}

@keyframes dashboard-fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: none; }
}
.kpi-card { animation: dashboard-fade-in 320ms ease-out both; }
```

## 10. Estados hover y focus

Cada elemento interactivo (filtro, sort handle, nav link, KPI card cuando es clickable) necesita hover y focus deliberados:

- **Hover**: translate 1-2 px hacia arriba o expansión de sombra de 180 ms. Hover solo-color se lee como accidental.
- **Focus**: outline en `--primary`, visible al navegar por teclado (`:focus-visible`).
- **Active**: estado presionado — translate baseline, superficie ligeramente más oscura.

## 11. Fondos

Opcional (solo si el tema de marca declara la extensión `background_style`):

- `solid` — gana la superficie base. Por defecto.
- `gradient-mesh` — gradientes radiales tintados por el accent. Bueno para dashboards editoriales.
- `noise` — ruido SVG estático tras el contenido. Bueno para tonos maximalistas o brutalistas. Evitar en tablas densas — baja el contraste.
- `grain` — patrón dotted fino a 3 px. Bueno para tonos analógicos o editoriales.

Todos renderizados inline, sin assets externos.

## 12. Idioma y accesibilidad

- Setear `<html lang="<user_lang>">` acorde al idioma que el agente está conversando (pasado por el agente como `lang=<código>`).
- Los strings de chrome de UI ("Filtros", "KPIs", "Limpiar filtros", "Ordenar", encabezados de columna, dropdown "Todos") deben ir en el idioma del usuario. No hardcodear inglés.
- Paletas colorblind-friendly (el `chart_categorical` del tema está ya curado; no sustituir salvo override explícito).
- No depender solo del color — usar iconos, etiquetas o patrones para estado (OK / warn / danger).
- Alt text en cualquier gráfica rasterizada a imagen.
- Navegación por teclado para todos los elementos interactivos (filtros, tablas ordenables, nav links).

**Patrón de labels** — tu HTML debe incluir un objeto `LABELS` con las strings UI traducidas al idioma del usuario. El chrome renderiza esas strings literalmente desde este objeto. Ejemplo:

```javascript
const LABELS = {
  filters_title: "Filtros",
  filter_all:    "Todos",
  clear_filters: "Limpiar",
  kpis_section:  "Indicadores clave",
  sort_asc:      "Orden ascendente",
  sort_desc:     "Orden descendente",
  // ...una entrada por cada string UI que muestre el dashboard
};
```

Mantén las claves neutras al idioma; los valores van traducidos. Si una clave falta, hacer fallback al default en inglés — no dejar visible un `{{placeholder}}`.

## 13. Responsive

Breakpoint en `768px`:

- Debajo: todas las secciones apilan verticalmente. `width="half"` colapsa a full. Las tablas llevan `overflow-x: auto`.
- Encima: grid de dos columnas para secciones HTML `width="half"`; fila de filtros horizontal.

La nav sticky va arriba; ocultar en móvil si compite con los filtros.

## 14. Gráficas que viven al lado: `chart_layout.py`

El helper local `skills/analyze/chart_layout.py` provee `apply_plotly_layout()`, `apply_chart_layout()` (matplotlib) y `to_rgba()` para evitar que títulos / subtítulos / leyendas se solapen. Usarlo para cualquier gráfica exportada como PNG (Plotly o matplotlib) antes de que el dashboard la embeba. Las figuras Plotly embebidas directamente (como JSON) pueden usar `apply_plotly_layout()` sobre la figura antes de la serialización.

## 15. Pitfalls analíticos a evitar

Estos son modos de fallo específicos del dominio del dashboard analítico — los pitfalls web genéricos (viewport meta, font-display, estados hover) ya los gestiona la disciplina de web-craft, no los repitas aquí.

- **Duplicación del bundle de Plotly** — cuando embebes múltiples figuras de Plotly, carga Plotly UNA VEZ vía `<script src="https://cdn.plot.ly/plotly-2.x.min.js">` en `<head>` y renderiza cada figura con `Plotly.newPlot(el, data, layout)`. Nunca exportes cada figura con `include_plotlyjs=True` / `full_html=True`: cada copia pesa ~3 MB, tres gráficas se convierten en un HTML de 9 MB.
- **Solapamiento título / leyenda en Plotly** — los títulos-insight son más largos que los títulos por defecto. Usa `apply_plotly_layout()` de `chart_layout.py`, que reserva espacio seteando `title.y = 0.95`, leyenda debajo del área de trazado (`y = -0.12`) y márgenes `t=100, b=80, l=60, r=40`. Nunca dejes la posición de leyenda por defecto cuando la gráfica tiene un título-insight.
- **Filtros que no hacen nada** — cada filtro global debe disparar `updateKPIs(filters)`, `updateCharts(filters)` y `updateTables(filters)`. Si alguna de las tres falta, el filtro cambia visualmente pero el dashboard no reacciona. Define las tres aunque una sea un no-op.
- **`DASHBOARD_DATA` ausente** — los filtros corren en el navegador; los datos que filtran deben estar embebidos. Si el agente olvida definir `DASHBOARD_DATA` antes de que los scripts corran, los filtros lanzan error y el dashboard se rompe silenciosamente. Embebe los slices pre-agregados como JSON inline antes de los scripts que los leen.
- **Plotly en grid half-width** — el grid de 2 columnas (`width="half"`) es solo para secciones HTML (callouts, cards resumen, texto comparativo). Las gráficas Plotly van siempre full-width porque los títulos-insight y la toolbar necesitan el espacio. Intentar renderizar una gráfica Plotly en una columna half-width trunca el título o la toolbar.

## 16. Lo que esta guía NO dicta

`web-craft` mantiene el control de estas decisiones:

- Tono específico (editorial-serious, technical-minimal, etc.) — viene del tema.
- Tipografía exacta — viene de `font_pair` en el tema.
- Valores exactos de accent / neutrales — vienen del tema.
- La micro-composición de secciones individuales (layout interno del card, encuadre de gráficas, styling de conclusiones) — `web-craft` los diseña según su workflow de cinco decisiones, coherente con el tema.

Esta guía restringe el **contrato analítico** (qué contiene un dashboard de `/analyze` y cómo se comporta); `web-craft` aporta la **voz visual**.
