# Guía de Segmentación por Reglas y RFM

Referencia operativa para segmentación como herramienta analítica dentro de `/analyze`. Usa exclusivamente pandas — sin dependencias de ML.

## 1. Tabla de Decisión

| Situación | Enfoque | Cuando preferir |
|-----------|---------|-----------------|
| Segmentos ya definidos por negocio (VIP, Regular, Nuevo) | Rule-based con umbrales | Reglas claras, interpretabilidad máxima |
| Datos transaccionales, segmentación estándar retail | RFM con quintiles | Pocas variables, fácil de comunicar |

## 2. RFM (Recency, Frequency, Monetary)

**Query MCP**: "fecha de última compra, número total de compras y total gastado por cliente"

**Cálculo**:
1. R = días desde última compra (menor = mejor)
2. F = número de compras (mayor = mejor)
3. M = total gastado (mayor = mejor)
4. Quintiles: `pd.qcut(serie, q=5, labels=[1,2,3,4,5])`. Invertir R (5 = más reciente)
5. Score: concatenar R+F+M como string o sumar para score numérico

**Etiquetas de negocio** (obligatorio — nunca "Segmento 1, 2, 3"):

| Score RFM | Etiqueta | Descripción |
|-----------|----------|-------------|
| 555, 554, 544 | Champions | Compraron reciente, compran frecuente, gastan mucho |
| 543, 444, 435 | Leales | Compras regulares con buen gasto |
| 512, 511, 422 | Potenciales | Compra reciente pero poca frecuencia |
| 155, 154, 144 | En riesgo | Fueron buenos pero hace mucho que no compran |
| 111, 112, 121 | Hibernando | Baja actividad en todas las dimensiones |

Adaptar etiquetas al dominio específico. La tabla es orientativa.

## 3. Profiling Obligatorio

Tras asignar segmentos (ya sea por reglas o RFM), SIEMPRE generar perfil de negocio:

1. **Media por segmento como índice base 100**: `(media_segmento / media_total) * 100` por variable
   - Índice > 120 = característica distintiva del segmento
   - Índice < 80 = debilidad relativa del segmento
2. **Tabla resumen**: Una fila por segmento, columnas = variables + tamaño (n y %)
3. **Naming**: Asignar nombre de negocio basado en el perfil. Nunca "Segmento 0, 1, 2"
   - Ejemplo: "Alto valor digital" (índice gasto online = 180, frecuencia = 150)
   - Ejemplo: "Compradores ocasionales" (índice frecuencia = 45, recencia = 60)
4. **Visualización**: Heatmap de índices (segmentos x variables), radar/spider chart por segmento
