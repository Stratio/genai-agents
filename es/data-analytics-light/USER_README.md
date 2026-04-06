# Data Analytics Light Agent

Agente ligero de Business Intelligence y Business Analytics orientado a conversacion: analiza datos gobernados y responde directamente en el chat.

## Que es este agente

Data Analytics Light es una version conversacional del agente de BI/BA. Conecta con los datos gobernados de tu organizacion para realizar analisis y responde con insights directamente en el chat. A diferencia de la version completa, no genera informes formales (PDF, DOCX, PowerPoint) — su fortaleza es el analisis interactivo rapido con visualizaciones en linea.

## Capacidades

- Explorar dominios de datos gobernados y descubrir tablas, columnas y reglas de negocio
- Responder preguntas de negocio con datos reales (KPIs, metricas, tendencias)
- Realizar analisis estadisticos (correlaciones, distribuciones, tests de hipotesis)
- Generar visualizaciones profesionales directamente en el chat
- Proponer terminos de negocio al diccionario de gobernanza

## Que puedes preguntarle

### Consultas rapidas
- "Cuantos clientes tenemos?"
- "Cual fue el total de ventas del ultimo trimestre?"
- "Que tablas hay en el dominio de facturacion?"

### Analisis conversacional
- "Analiza la tendencia de ventas por mes en el ultimo anio"
- "Hay correlacion entre el gasto en marketing y las ventas?"
- "Que productos tienen mas rotacion?"
- "Compara los ingresos por canal de venta"
- "Segmenta los clientes por comportamiento de compra"

### Exploracion
- "Que dominios de datos hay disponibles?"
- "Describe las tablas del dominio de clientes"
- "Que significa el campo 'lifetime_value'?"

## Skills disponibles

| Comando | Descripcion |
|---------|-------------|
| `/analyze` | Analisis de datos: descubrimiento de dominio, planificacion, queries, analisis estadistico y visualizaciones |
| `/explore-data` | Exploracion rapida de dominios, tablas, columnas y terminologia de negocio |
| `/propose-knowledge` | Proponer terminos de negocio descubiertos al diccionario de gobernanza |

## Conexiones necesarias

- **MCP de datos**: consultas SQL, exploracion de dominios, profiling de tablas y columnas

## Primeros pasos

Inicia el agente y pregunta: "Que dominios de datos hay disponibles?"
