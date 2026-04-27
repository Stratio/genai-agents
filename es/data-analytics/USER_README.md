# Data Analytics Agent

Agente analista senior de BI/BA que convierte preguntas de negocio en análisis accionables con datos reales de dominios gobernados, y entrega el resultado en el formato que necesites — desde un informe PDF hasta un workbook Excel, desde un dashboard interactivo hasta una infografía de una página.

## Qué es este agente

Data Analytics es un asistente de BI/BA completo que conecta con los datos gobernados de tu organización para realizar análisis avanzados. Puede descubrir dominios de datos, ejecutar consultas, realizar análisis estadísticos, generar visualizaciones profesionales y entregar los resultados en **siete formatos analíticos**: informes PDF, documentos Word, presentaciones PowerPoint, workbooks Excel, dashboards web interactivos, informes web / artículos web y pósters/infografías de una página.

También puede ingerir contexto local (contratos PDF, briefs Word, decks PowerPoint, hojas Excel), aplicar identidad visual consistente mediante un catálogo centralizado de temas, y mantener memoria entre sesiones — recordando tus preferencias de análisis, patrones conocidos y heurísticas aprendidas.

## Capacidades

- Explorar dominios de datos gobernados y descubrir tablas, columnas y reglas de negocio
- Responder preguntas de negocio con datos reales (KPIs, métricas, tendencias)
- Realizar análisis estadísticos avanzados (correlaciones, distribuciones, tests de hipótesis)
- Segmentación y clustering automático de datos (RFM, KMeans, DBSCAN)
- Generar visualizaciones profesionales (gráficas, charts, dashboards)
- **Informes analíticos** en siete formatos (PDF, DOCX, PowerPoint, Excel, dashboard web interactivo, informe web / artículo web, póster/infografía) — generados cuando pides un análisis con un entregable
- **Entregables visuales ligeros** sin ejecutar un análisis — pósters e infografías rápidas, dashboards interactivos standalone, PDFs simples con pocos KPIs, documentos Word y Excel ad-hoc
- **Leer documentos existentes** — PDFs, Word (`.docx`/`.doc`), PowerPoint (`.pptx`/`.ppt`) y Excel (`.xlsx`/`.xls`) — para extraer texto, tablas, diapositivas, valores de celda y metadatos
- **Evaluar la cobertura de calidad del dato** y generar informes de calidad en 9 formatos (Chat, PDF, DOCX, PPTX, Dashboard web, Informe web / Artículo web, Póster/Infografía, XLSX, Markdown) — solo lectura, no crea ni programa reglas
- Aplicar identidad visual consistente (colores, tipografía, paletas de gráficos) a cada entregable mediante el catálogo centralizado de temas (10 temas curados, extensible por cliente)
- Recordar preferencias y análisis previos entre sesiones (memoria persistente)
- Proponer términos de negocio al diccionario de gobernanza

## Formatos de salida

Cuando pides un entregable, elige el formato que encaje con la audiencia:

| Formato | Ideal para |
|---|---|
| **PDF** | Informes formales multi-página con narrativa en prosa |
| **DOCX** | Documentos Word editables para revisión e iteración |
| **PPTX** | Decks ejecutivos, briefings a comités de dirección |
| **XLSX** | Workbooks analíticos (cover/KPI + parámetros + detalle + apéndice), matrices pivot, exports tabulares, modelos cuantitativos |
| **Dashboard web** | HTML interactivo con KPI cards, filtros y tablas ordenables |
| **Informe web / Artículo web** | Página HTML editorial autocontenida con secciones narrativas, callouts KPI inline y gráficos incrustados |
| **Póster / Infografía** | Resumen visual de una página para comunicación o exposición |

Cada formato visual aplica el tema que elijas al inicio (o el tema corporativo por defecto).

## Qué puedes preguntarle

### Consultas rápidas
- "¿Cuántos clientes tenemos?"
- "¿Cuál fue el total de ventas del último trimestre?"
- "¿Qué tablas hay en el dominio de facturación?"

### Análisis avanzado
- "Analiza la evolución de ventas por región en los últimos 12 meses"
- "¿Qué factores influyen más en la rotación de clientes?"
- "Compara el rendimiento de las tiendas del norte vs sur"
- "Segmenta los clientes por comportamiento de compra"
- "¿Hay anomalías en los datos de facturación del último mes?"

### Informes analíticos (análisis + entregable)
- "Genera un informe PDF con el análisis de rentabilidad"
- "Crea un dashboard web interactivo con los KPIs de ventas y la narrativa del deep-dive"
- "Prepara una presentación PowerPoint con los resultados del trimestre y los hallazgos clave"
- "Genera un informe Word con el análisis de cohortes"
- "Produce un workbook Excel analítico con cover de KPIs y hojas de detalle con pivots para el último trimestre"
- "Usa el tema luxury-refined para el informe ejecutivo"

### Visuales ligeros (sin análisis, solo el artefacto)
- "Hazme un póster con los 3 KPIs principales del último trimestre" *(canvas-craft)*
- "Construye una infografía de marketing con los números del lanzamiento" *(canvas-craft)*
- "Dame un PDF de una página con estas 3 cifras de ventas" *(pdf-writer)*
- "Dashboard interactivo standalone para el equipo de operaciones, sin narrativa" *(web-craft)*
- "Reempaqueta el output del análisis de ayer como un PDF en otro estilo" *(pdf-writer)*
- "Exporta esta lista de cifras como una tabla Excel con fórmulas" *(xlsx-writer)*

### Reempaquetar una exploración o consulta rápida
Tras explorar un dominio, una evaluación de calidad o una consulta MCP rápida, puedes pedir empaquetar lo que has visto — sin reanalizar:
- Tras `/explore-data` del dominio ventas → "Ahora dame esto en un PDF" *(pdf-writer)*
- Tras listar las tablas de un dominio → "Hazme un póster de una página con esta lista" *(canvas-craft)*
- Tras `/assess-quality` → "Pásalo a un dashboard standalone" *(web-craft)*
- Tras cualquier resultado SQL → "Vuélcalo como workbook Excel" *(xlsx-writer)*

(Si añades un verbo analítico — "ahora analiza esto y dame un PDF" — el agente ejecuta el análisis completo en lugar de solo empaquetar.)

### Lectura de documentos existentes
- "Lee este PDF y extrae las tablas"
- "¿Qué dice este PDF de contrato sobre las condiciones de renovación?"
- "Lee este Excel y extrae la tabla de ingresos"
- "Extrae los bullets de este deck PowerPoint"
- "Lee este informe Word y resume la sección de KPIs"

### Exploración
- "¿Qué dominios de datos hay disponibles?"
- "Describe las tablas del dominio de clientes"
- "¿Qué significa el campo 'churn_score' en la tabla de clientes?"

### Cobertura de calidad
- "Evalúa la cobertura de calidad del dominio ventas"
- "¿Qué reglas de calidad tiene la tabla clientes?"
- "Genera un PDF de calidad del dominio logística"
- "Construye un dashboard web de calidad para el dominio facturación"
- "Exporta la cobertura de calidad del dominio X como un workbook Excel"

> Nota: este agente evalúa e informa. Para crear reglas o programar ejecuciones, usa los agentes Data Quality o Governance Officer.

## Skills disponibles

### Análisis, exploración y memoria
| Comando | Descripción |
|---------|-------------|
| `/analyze` | Análisis completo: descubrimiento de dominio, planificación, queries, análisis estadístico, visualizaciones y entregables multi-formato (PDF, DOCX, PPTX, XLSX, web interactiva, póster) |
| `/explore-data` | Exploración rápida de dominios, tablas, columnas y terminología de negocio |
| `/update-memory` | Actualizar la memoria persistente con preferencias y patrones aprendidos |
| `/propose-knowledge` | Proponer términos de negocio descubiertos al diccionario de gobernanza |

### Cobertura de calidad (solo lectura)
| Comando | Descripción |
|---------|-------------|
| `/assess-quality` | Evaluación de cobertura de calidad (dimensiones, reglas existentes, gaps) |
| `/quality-report` | Generar un informe formal de cobertura de calidad en Chat, PDF, DOCX, PPTX, Dashboard web, Informe web / Artículo web, Póster/Infografía, XLSX o Markdown |

### Lectores de contenido
| Comando | Descripción |
|---------|-------------|
| `/pdf-reader` | Extraer texto, tablas, imágenes, formularios y adjuntos de ficheros PDF |
| `/docx-reader` | Extraer contenido de documentos Word (`.docx` y `.doc` legacy) |
| `/pptx-reader` | Extraer diapositivas, notas y assets embebidos de decks PowerPoint |
| `/xlsx-reader` | Leer valores de celda, tablas, fórmulas y metadatos de workbooks Excel |

### Escritores de contenido
| Comando | Descripción |
|---------|-------------|
| `/pdf-writer` | PDFs multi-página o dominados por prosa (informes ligeros con ≤3 KPIs, facturas, cartas, newsletters, certificados). También combinar/dividir/rotar, marca de agua, cifrar, rellenar formularios |
| `/docx-writer` | Autorar y manipular documentos Word (combinar, dividir, find-replace, conversión de `.doc`) |
| `/pptx-writer` | Autorar y manipular decks PowerPoint fuera del pipeline analítico (combinar, dividir, reordenar, find-replace) |
| `/xlsx-writer` | Autorar workbooks Excel analíticos y ad-hoc (cover/KPI + detalle, matrices pivot, exports tabulares), convertir `.xls` a `.xlsx` |

### Visuales y branding
| Comando | Descripción |
|---------|-------------|
| `/canvas-craft` | Visuales de una sola página dominados por composición: pósters, infografías, portadas, one-pagers de marketing (PDF o PNG) |
| `/web-craft` | HTML interactivo standalone: dashboards sin narrativa analítica, componentes UI, landing pages |
| `/brand-kit` | Catálogo centralizado de temas: 10 temas curados (corporate-formal, luxury-refined, editorial-serious, technical-minimal y más), extensible con temas propios del cliente |

## Conexiones necesarias

- **MCP de datos** (`stratio_data`): consultas SQL, exploración de dominios, profiling de tablas y columnas — configurado vía `MCP_SQL_URL` / `MCP_SQL_API_KEY`
- **MCP de gobernanza** (`stratio_gov`, solo lectura): dimensiones de calidad y metadata de reglas para la evaluación de cobertura — configurado vía `MCP_GOV_URL` / `MCP_GOV_API_KEY`

## Primeros pasos

Inicia el agente y pregunta: "¿Qué dominios de datos hay disponibles?"
