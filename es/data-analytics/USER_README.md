# Data Analytics Agent

Agente de Business Intelligence y Business Analytics que convierte preguntas de negocio en análisis accionables con datos reales.

## Que es este agente

Data Analytics es un asistente de BI/BA completo que conecta con los datos gobernados de tu organización para realizar análisis avanzados. Puede descubrir dominios de datos, ejecutar consultas, realizar análisis estadísticos, generar visualizaciones profesionales y entregar los resultados en múltiples formatos: informes PDF, documentos Word, presentaciones PowerPoint o dashboards web interactivos.

El agente mantiene memoria entre sesiones, recordando tus preferencias de análisis, patrones de datos conocidos y heurísticas aprendidas.

## Capacidades

- Explorar dominios de datos gobernados y descubrir tablas, columnas y reglas de negocio
- Responder preguntas de negocio con datos reales (KPIs, métricas, tendencias)
- Realizar análisis estadísticos avanzados (correlaciones, distribuciones, tests de hipótesis)
- Segmentación y clustering automático de datos (RFM, KMeans, DBSCAN)
- Generar visualizaciones profesionales (gráficas, charts, dashboards)
- Crear informes en múltiples formatos: PDF, DOCX, PowerPoint, web interactiva
- Recordar preferencias y análisis previos entre sesiones (memoria persistente)
- Proponer términos de negocio al diccionario de gobernanza

## Qué puedes preguntarle

### Consultas rápidas
- "Cuántos clientes tenemos?"
- "Cuál fue el total de ventas del último trimestre?"
- "Qué tablas hay en el dominio de facturación?"

### Análisis avanzado
- "Analiza la evolución de ventas por región en los últimos 12 meses"
- "Qué factores influyen más en la rotación de clientes?"
- "Compara el rendimiento de las tiendas del norte vs sur"
- "Segmenta los clientes por comportamiento de compra"
- "Hay anomalías en los datos de facturación del último mes?"

### Informes
- "Genera un informe PDF con el análisis de rentabilidad"
- "Crea un dashboard web interactivo con los KPIs de ventas"
- "Prepara una presentación PowerPoint con los resultados del trimestre"
- "Genera un informe Word con el análisis de cohortes"

### Exploración
- "Qué dominios de datos hay disponibles?"
- "Describe las tablas del dominio de clientes"
- "Qué significa el campo 'churn_score' en la tabla de clientes?"

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/analyze` | Análisis completo: descubrimiento de dominio, planificación, queries, análisis estadístico, visualizaciones e informes |
| `/report` | Generación de informes profesionales en PDF, DOCX, web interactiva o PowerPoint |
| `/explore-data` | Exploración rápida de dominios, tablas, columnas y terminología de negocio |
| `/update-memory` | Actualizar la memoria persistente con preferencias y patrones aprendidos |
| `/propose-knowledge` | Proponer términos de negocio descubiertos al diccionario de gobernanza |

## Conexiones necesarias

- **MCP de datos**: consultas SQL, exploración de dominios, profiling de tablas y columnas

## Primeros pasos

Inicia el agente y pregunta: "Qué dominios de datos hay disponibles?"
