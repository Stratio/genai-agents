# Data Analytics Agent

Agente de Business Intelligence y Business Analytics que convierte preguntas de negocio en analisis accionables con datos reales.

## Que es este agente

Data Analytics es un asistente de BI/BA completo que conecta con los datos gobernados de tu organizacion para realizar analisis avanzados. Puede descubrir dominios de datos, ejecutar consultas, realizar analisis estadisticos, generar visualizaciones profesionales y entregar los resultados en multiples formatos: informes PDF, documentos Word, presentaciones PowerPoint o dashboards web interactivos.

El agente mantiene memoria entre sesiones, recordando tus preferencias de analisis, patrones de datos conocidos y heuristicas aprendidas.

## Capacidades

- Explorar dominios de datos gobernados y descubrir tablas, columnas y reglas de negocio
- Responder preguntas de negocio con datos reales (KPIs, metricas, tendencias)
- Realizar analisis estadisticos avanzados (correlaciones, distribuciones, tests de hipotesis)
- Segmentacion y clustering automatico de datos (RFM, KMeans, DBSCAN)
- Generar visualizaciones profesionales (graficas, charts, dashboards)
- Crear informes en multiples formatos: PDF, DOCX, PowerPoint, web interactiva
- Recordar preferencias y analisis previos entre sesiones (memoria persistente)
- Proponer terminos de negocio al diccionario de gobernanza

## Que puedes preguntarle

### Consultas rapidas
- "Cuantos clientes tenemos?"
- "Cual fue el total de ventas del ultimo trimestre?"
- "Que tablas hay en el dominio de facturacion?"

### Analisis avanzado
- "Analiza la evolucion de ventas por region en los ultimos 12 meses"
- "Que factores influyen mas en la rotacion de clientes?"
- "Compara el rendimiento de las tiendas del norte vs sur"
- "Segmenta los clientes por comportamiento de compra"
- "Hay anomalias en los datos de facturacion del ultimo mes?"

### Informes
- "Genera un informe PDF con el analisis de rentabilidad"
- "Crea un dashboard web interactivo con los KPIs de ventas"
- "Prepara una presentacion PowerPoint con los resultados del trimestre"
- "Genera un informe Word con el analisis de cohortes"

### Exploracion
- "Que dominios de datos hay disponibles?"
- "Describe las tablas del dominio de clientes"
- "Que significa el campo 'churn_score' en la tabla de clientes?"

## Skills disponibles

| Comando | Descripcion |
|---------|-------------|
| `/analyze` | Analisis completo: descubrimiento de dominio, planificacion, queries, analisis estadistico, visualizaciones e informes |
| `/report` | Generacion de informes profesionales en PDF, DOCX, web interactiva o PowerPoint |
| `/explore-data` | Exploracion rapida de dominios, tablas, columnas y terminologia de negocio |
| `/update-memory` | Actualizar la memoria persistente con preferencias y patrones aprendidos |
| `/propose-knowledge` | Proponer terminos de negocio descubiertos al diccionario de gobernanza |

## Conexiones necesarias

- **MCP de datos**: consultas SQL, exploracion de dominios, profiling de tablas y columnas

## Primeros pasos

Inicia el agente y pregunta: "Que dominios de datos hay disponibles?"
