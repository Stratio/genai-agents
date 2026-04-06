# Patrones Analiticos Adicionales

Implementacion detallada de patrones cuyo trigger esta en sec "Patrones analiticos operacionalizados" de AGENTS.md (tabla de patrones operacionalizados).

## Concentracion (Lorenz/Gini)
- **Query MCP**: "metrica acumulada por [entidad] ordenada de mayor a menor"
- **Python**: Ordenar desc, `cumsum() / total` para curva de Lorenz. Gini = 1 - 2 * area bajo curva (`np.trapz`)
- **Visualizacion**: Curva de Lorenz (linea acumulada) + diagonal de igualdad perfecta + Gini anotado en leyenda. `legend_position="inside"` (<=3 items)
- **Interpretacion**: Gini > 0.6 = alta concentracion ("El 20% de clientes genera el X% de ingresos")

## Analisis de mix
- **Query MCP**: "metrica desglosada por componentes (volumen, precio unitario) en periodo A y periodo B"
- **Python**: Descomponer delta total en: efecto volumen (Δvol × precio_base), efecto precio (Δprecio × vol_base), efecto mix (Δvol × Δprecio)
- **Visualizacion**: Waterfall chart con contribucion de cada factor al cambio total
- **Interpretacion**: "El crecimiento de €X se explica en un Y% por volumen y un Z% por precio"

## Indexacion (base 100)
- **Query MCP**: "metricas [mensuales] por [dimension] del [periodo]"
- **Python**: `(serie / serie.iloc[0]) * 100` por cada grupo. Permite comparar evoluciones relativas
- **Visualizacion**: Line chart con todas las series partiendo de 100 en el periodo base. `legend_position="bottom"` (multiples series)
- **Interpretacion**: "Desde base, la categoria A crecio un 45% mientras B solo un 12%"

## Desviacion vs referencia
- **Query MCP**: "metrica por [dimension]", calcular media o buscar target en knowledge
- **Python**: `desviacion = valor - referencia` por categoria, ordenar
- **Visualizacion**: Bar chart divergente (horizontal) centrado en la referencia (0). Positivos a derecha, negativos a izquierda. Sin leyenda (cada barra es su categoria)
- **Interpretacion**: "5 de 12 regiones superan la media. La mayor desviacion positiva es X (+23%)"

## Analisis gap
- **Query MCP**: "metrica actual y objetivo por [dimension]"
- **Python**: `gap = target - actual`, `pct_gap = gap / target * 100`, ordenar por gap descendente
- **Visualizacion**: Lollipop chart (punto = actual, linea hasta target) o bullet chart por dimension
- **Interpretacion**: "La mayor brecha esta en X (€45K, 23% del target). Cerrar las 3 mayores brechas aporta €120K"
