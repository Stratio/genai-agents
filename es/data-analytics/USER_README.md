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
- **Informes analíticos** en múltiples formatos (PDF, DOCX, PowerPoint, web interactiva) — generados cuando pides un análisis con un entregable
- **Entregables visuales ligeros** sin ejecutar un análisis — pósters e infografías rápidas, dashboards interactivos standalone, PDFs simples con pocos KPIs
- **Leer PDFs existentes** para extraer texto, tablas y datos de formulario
- **Evaluar la cobertura de calidad del dato** y generar informes de calidad (Chat / PDF / DOCX / Markdown) — solo lectura, no crea ni programa reglas
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

### Informes analíticos (análisis + entregable)
- "Genera un informe PDF con el análisis de rentabilidad"
- "Crea un dashboard web interactivo con los KPIs de ventas y la narrativa del deep-dive"
- "Prepara una presentación PowerPoint con los resultados del trimestre y los hallazgos clave"
- "Genera un informe Word con el análisis de cohortes"

### Visuales ligeros (sin análisis, solo el artefacto)
- "Hazme un póster con los 3 KPIs principales del último trimestre" *(canvas-craft)*
- "Construye una infografía de marketing con los números del lanzamiento" *(canvas-craft)*
- "Dame un PDF de una página con estas 3 cifras de ventas" *(pdf-writer)*
- "Dashboard interactivo standalone para el equipo de operaciones, sin narrativa" *(web-craft)*
- "Reempaqueta el output del análisis de ayer como un PDF en otro estilo" *(pdf-writer)*

### Reempaquetar una exploración o consulta rápida
Tras explorar un dominio, una evaluación de calidad o una consulta MCP rápida, puedes pedir empaquetar lo que has visto — sin reanalizar:
- Tras `/explore-data` del dominio ventas → "Ahora dame esto en un PDF" *(pdf-writer)*
- Tras listar las tablas de un dominio → "Hazme un póster de una página con esta lista" *(canvas-craft)*
- Tras `/assess-quality` → "Pásalo a un dashboard standalone" *(web-craft)*

(Si añades un verbo analítico — "ahora analiza esto y dame un PDF" — el agente ejecuta el análisis completo en lugar de solo empaquetar.)

### Lectura de PDFs
- "Lee este PDF y extrae las tablas"
- "¿Qué dice este PDF de contrato sobre las condiciones de renovación?"

### Exploración
- "Qué dominios de datos hay disponibles?"
- "Describe las tablas del dominio de clientes"
- "Qué significa el campo 'churn_score' en la tabla de clientes?"

### Cobertura de calidad
- "Evalúa la cobertura de calidad del dominio ventas"
- "¿Qué reglas de calidad tiene la tabla clientes?"
- "Genera un PDF de calidad del dominio logística"
- "¿Qué dimensiones no están cubiertas en la tabla facturación?"

> Nota: este agente evalúa e informa. Para crear reglas o programar ejecuciones, usa los agentes Data Quality o Governance Officer.

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/analyze` | Análisis completo: descubrimiento de dominio, planificación, queries, análisis estadístico, visualizaciones y entregables multi-formato (PDF, DOCX, web interactiva, PowerPoint — generados internamente) |
| `/explore-data` | Exploración rápida de dominios, tablas, columnas y terminología de negocio |
| `/assess-quality` | Evaluación de cobertura de calidad (dimensiones, reglas existentes, gaps) |
| `/quality-report` | Generar un informe formal de cobertura de calidad (Chat / PDF / DOCX / Markdown) |
| `/update-memory` | Actualizar la memoria persistente con preferencias y patrones aprendidos |
| `/propose-knowledge` | Proponer términos de negocio descubiertos al diccionario de gobernanza |
| `/pdf-reader` | Leer y extraer contenido de archivos PDF (texto, tablas, imágenes, formularios, adjuntos) |
| `/pdf-writer` | PDFs multi-página o dominados por prosa (informes ligeros con ≤3 KPIs, facturas, cartas, newsletters, certificados). También combinar/dividir/rotar, marca de agua, cifrar, rellenar formularios |
| `/canvas-craft` | Visuales de una sola página dominados por composición: pósters, infografías, portadas, one-pagers de marketing (PDF o PNG) |
| `/web-craft` | HTML interactivo standalone: dashboards sin narrativa analítica, componentes UI, landing pages |

## Conexiones necesarias

- **MCP de datos** (`stratio_data`): consultas SQL, exploración de dominios, profiling de tablas y columnas — configurado vía `MCP_SQL_URL` / `MCP_SQL_API_KEY`
- **MCP de gobernanza** (`stratio_gov`, solo lectura): dimensiones de calidad y metadata de reglas para la evaluación de cobertura — configurado vía `MCP_GOV_URL` / `MCP_GOV_API_KEY`

## Primeros pasos

Inicia el agente y pregunta: "Qué dominios de datos hay disponibles?"
