# Guia de Segmentacion por Reglas y RFM

Referencia operativa para segmentacion como herramienta analitica dentro de `/analyze`. Usa exclusivamente pandas — sin dependencias de ML.

## 1. Tabla de Decision

| Situacion | Enfoque | Cuando preferir |
|-----------|---------|-----------------|
| Segmentos ya definidos por negocio (VIP, Regular, Nuevo) | Rule-based con umbrales | Reglas claras, interpretabilidad maxima |
| Datos transaccionales, segmentacion estandar retail | RFM con quintiles | Pocas variables, facil de comunicar |

## 2. RFM (Recency, Frequency, Monetary)

**Query MCP**: "fecha de ultima compra, numero total de compras y total gastado por cliente"

**Calculo**:
1. R = dias desde ultima compra (menor = mejor)
2. F = numero de compras (mayor = mejor)
3. M = total gastado (mayor = mejor)
4. Quintiles: `pd.qcut(serie, q=5, labels=[1,2,3,4,5])`. Invertir R (5 = mas reciente)
5. Score: concatenar R+F+M como string o sumar para score numerico

**Etiquetas de negocio** (obligatorio — nunca "Segmento 1, 2, 3"):

| Score RFM | Etiqueta | Descripcion |
|-----------|----------|-------------|
| 555, 554, 544 | Champions | Compraron reciente, compran frecuente, gastan mucho |
| 543, 444, 435 | Leales | Compras regulares con buen gasto |
| 512, 511, 422 | Potenciales | Compra reciente pero poca frecuencia |
| 155, 154, 144 | En riesgo | Fueron buenos pero hace mucho que no compran |
| 111, 112, 121 | Hibernando | Baja actividad en todas las dimensiones |

Adaptar etiquetas al dominio especifico. La tabla es orientativa.

## 3. Profiling Obligatorio

Tras asignar segmentos (ya sea por reglas o RFM), SIEMPRE generar perfil de negocio:

1. **Media por segmento como indice base 100**: `(media_segmento / media_total) * 100` por variable
   - Indice > 120 = caracteristica distintiva del segmento
   - Indice < 80 = debilidad relativa del segmento
2. **Tabla resumen**: Una fila por segmento, columnas = variables + tamano (n y %)
3. **Naming**: Asignar nombre de negocio basado en el perfil. Nunca "Segmento 0, 1, 2"
   - Ejemplo: "Alto valor digital" (indice gasto online = 180, frecuencia = 150)
   - Ejemplo: "Compradores ocasionales" (indice frecuencia = 45, recencia = 60)
4. **Visualizacion**: Heatmap de indices (segmentos x variables), radar/spider chart por segmento
