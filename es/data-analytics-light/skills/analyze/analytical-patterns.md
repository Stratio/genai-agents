# Patrones Analíticos Adicionales

Implementación detallada de patrones cuyo trigger está en sec 3.2 (tabla de patrones operacionalizados).

## Concentración (Lorenz/Gini)
- **Query MCP**: "métrica acumulada por [entidad] ordenada de mayor a menor"
- **Python**: Ordenar desc, `cumsum() / total` para curva de Lorenz. Gini = 1 - 2 * área bajo curva (`np.trapz`)
- **Visualización**: Curva de Lorenz (línea acumulada) + diagonal de igualdad perfecta + Gini anotado en leyenda. `legend_position="inside"` (<=3 items)
- **Interpretación**: Gini > 0.6 = alta concentración ("El 20% de clientes genera el X% de ingresos")

## Análisis de mix
- **Query MCP**: "métrica desglosada por componentes (volumen, precio unitario) en periodo A y periodo B"
- **Python**: Descomponer delta total en: efecto volumen (Δvol × precio_base), efecto precio (Δprecio × vol_base), efecto mix (Δvol × Δprecio)
- **Visualización**: Waterfall chart con contribución de cada factor al cambio total
- **Interpretación**: "El crecimiento de €X se explica en un Y% por volumen y un Z% por precio"

## Indexación (base 100)
- **Query MCP**: "métricas [mensuales] por [dimensión] del [periodo]"
- **Python**: `(serie / serie.iloc[0]) * 100` por cada grupo. Permite comparar evoluciones relativas
- **Visualización**: Line chart con todas las series partiendo de 100 en el periodo base. `legend_position="bottom"` (múltiples series)
- **Interpretación**: "Desde base, la categoría A creció un 45% mientras B solo un 12%"

## Desviación vs referencia
- **Query MCP**: "métrica por [dimensión]", calcular media o buscar target en knowledge
- **Python**: `desviacion = valor - referencia` por categoría, ordenar
- **Visualización**: Bar chart divergente (horizontal) centrado en la referencia (0). Positivos a derecha, negativos a izquierda. Sin leyenda (cada barra es su categoría)
- **Interpretación**: "5 de 12 regiones superan la media. La mayor desviación positiva es X (+23%)"

## Análisis gap
- **Query MCP**: "métrica actual y objetivo por [dimensión]"
- **Python**: `gap = target - actual`, `pct_gap = gap / target * 100`, ordenar por gap descendente
- **Visualización**: Lollipop chart (punto = actual, línea hasta target) o bullet chart por dimensión
- **Interpretación**: "La mayor brecha está en X (€45K, 23% del target). Cerrar las 3 mayores brechas aporta €120K"
