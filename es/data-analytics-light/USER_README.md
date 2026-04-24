# Data Analytics Light Agent

Agente ligero de Business Intelligence y Business Analytics orientado a conversación: analiza datos gobernados y responde directamente en el chat con visualizaciones embebidas.

## Qué es este agente

Data Analytics Light es una versión conversacional del agente de BI/BA. Conecta con los datos gobernados de tu organización para realizar análisis y responde con insights directamente en el chat. A diferencia del agente Data Analytics completo, **no genera entregables en fichero** — ni PDF, ni DOCX, ni PowerPoint, ni Excel — y tampoco lee documentos existentes. Su fortaleza es el análisis interactivo rápido con visualizaciones profesionales embebidas en la propia conversación.

El agente sí puede aplicar identidad visual consistente a los gráficos inline mediante el catálogo centralizado de temas, para que los gráficos renderizados en chat se ajusten a tu look & feel corporativo.

## Capacidades

- Explorar dominios de datos gobernados y descubrir tablas, columnas y reglas de negocio
- Responder preguntas de negocio con datos reales (KPIs, métricas, tendencias)
- Realizar análisis estadísticos (correlaciones, distribuciones, tests de hipótesis)
- Generar visualizaciones profesionales directamente en el chat
- Aplicar identidad visual corporativa (colores, paletas de gráficos, tipografía) a los gráficos inline mediante el catálogo centralizado de temas (10 temas curados, extensible por cliente)
- **Evaluar la cobertura de calidad del dato** y producir resúmenes de calidad en chat (solo lectura, sin salida a fichero). Para informes en fichero en cualquier formato usa el agente Data Analytics completo.
- Proponer términos de negocio al diccionario de gobernanza

> **Alcance.** Este agente no genera informes formales (ni PDF, ni DOCX, ni PowerPoint, ni Excel) y no lee documentos existentes. Para entregables en fichero, lectura de documentos o creación de reglas de calidad, usa los agentes hermanos indicados más abajo.

## Qué puedes preguntarle

### Consultas rápidas
- "¿Cuántos clientes tenemos?"
- "¿Cuál fue el total de ventas del último trimestre?"
- "¿Qué tablas hay en el dominio de facturación?"

### Análisis conversacional
- "Analiza la tendencia de ventas por mes en el último año"
- "¿Hay correlación entre el gasto en marketing y las ventas?"
- "¿Qué productos tienen más rotación?"
- "Compara los ingresos por canal de venta"
- "Segmenta los clientes por comportamiento de compra"

### Exploración
- "¿Qué dominios de datos hay disponibles?"
- "Describe las tablas del dominio de clientes"
- "¿Qué significa el campo 'lifetime_value'?"

### Cobertura de calidad (solo chat)
- "Evalúa la cobertura de calidad del dominio ventas"
- "¿Qué reglas de calidad tiene la tabla clientes?"
- "¿Qué dimensiones no están cubiertas en la tabla facturación?"

### Identidad visual
- "Usa el tema luxury-refined para los gráficos de este análisis"
- "Aplica nuestra paleta corporativa a las visualizaciones inline"

> **Nota sobre el alcance.** Este agente entrega análisis y gráficos **solo en chat**. Para ficheros (PDF / DOCX / PowerPoint / Excel / Markdown / dashboard web / póster), usa el agente **Data Analytics** completo. Para crear o programar reglas de calidad, usa los agentes **Data Quality** o **Governance Officer**.

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/analyze` | Análisis de datos: descubrimiento de dominio, planificación, queries, análisis estadístico y visualizaciones inline |
| `/explore-data` | Exploración rápida de dominios, tablas, columnas y terminología de negocio |
| `/assess-quality` | Evaluación de cobertura de calidad (dimensiones, reglas existentes, gaps) |
| `/quality-report` | Resumen de cobertura de calidad **solo en chat** (sin salida a fichero en este agente) |
| `/propose-knowledge` | Proponer términos de negocio descubiertos al diccionario de gobernanza |
| `/brand-kit` | Catálogo centralizado de temas aplicado a los gráficos inline (10 temas curados, extensible por cliente) |

## Conexiones necesarias

- **MCP de datos** (`stratio_data`): consultas SQL, exploración de dominios, profiling de tablas y columnas — configurado vía `MCP_SQL_URL` / `MCP_SQL_API_KEY`
- **MCP de gobernanza** (`stratio_gov`, solo lectura): dimensiones de calidad y metadata de reglas para la evaluación de cobertura — configurado vía `MCP_GOV_URL` / `MCP_GOV_API_KEY`

## Primeros pasos

Inicia el agente y pregunta: "¿Qué dominios de datos hay disponibles?"
