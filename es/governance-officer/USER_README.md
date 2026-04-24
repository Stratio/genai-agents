# Agente Governance Officer

Agente experto en gobierno que combina la construcción de capas semánticas y la gestión de calidad del dato en un único asistente — el ciclo completo de gobierno del dato bajo un mismo techo.

## Qué hace este agente

Governance Officer es un asistente integral para ambas caras del gobierno del dato: construir **capas semánticas** y gestionar **calidad del dato**. Puede construir ontologías, business views, SQL mappings y términos semánticos para tus dominios, y también evaluar la cobertura de calidad, identificar gaps, crear reglas de calidad, programar su ejecución y generar informes de cobertura en ocho formatos diferentes — desde decks ejecutivos hasta dashboards interactivos.

El agente trabaja con Stratio Data Governance vía herramientas MCP, orquestando el ciclo de vida completo de los artefactos de gobierno con tu aprobación en cada paso crítico. También puede ingerir ficheros locales (especificaciones Word, walkthroughs PowerPoint, catálogos Excel, PDFs) para enriquecer la planificación, y aplicar identidad visual consistente a cada entregable mediante el catálogo centralizado de temas.

## Capacidades

### Capa semántica
- Construir y mantener capas semánticas completas (ontologías, business views, SQL mappings, términos)
- Publicar business views para revisión
- Explorar dominios técnicos y capas semánticas publicadas
- Planificación interactiva de ontologías con lectura de ficheros locales (incluidas especificaciones `.docx` y decks `.pptx`)
- Crear data collections (dominios técnicos) a partir de búsquedas en el diccionario de datos
- Gestionar business terms en el diccionario de gobierno

### Calidad del dato
- Evaluar la cobertura de calidad por dominio, colección, tabla o columna
- Identificar gaps: dimensiones de calidad no cubiertas, tablas o columnas sin cobertura
- Proponer reglas de calidad razonadas basadas en contexto semántico y profiling real
- Crear reglas de calidad con aprobación humana obligatoria (human-in-the-loop)
- Programar la ejecución automática de reglas de calidad
- Generar informes de cobertura en 8 formatos (ver [Formatos de salida](#formatos-de-salida))

### Manejo de contenido y branding
- Leer y extraer contenido de ficheros PDF, Word, PowerPoint y Excel
- Autorar y manipular documentos PDF, Word, PowerPoint y Excel para compliance briefs, decks de políticas, walkthroughs de ontología, catálogos de términos y workbooks de especificación de reglas
- Aplicar identidad visual consistente (colores, tipografía, paletas de gráficos) a cada entregable visual mediante el catálogo centralizado de temas (10 temas curados, extensible por cliente)

## Formatos de salida

Para informes de cobertura de calidad y otros entregables multi-formato, puedes elegir entre:

| Formato | Ideal para |
|---|---|
| **Chat** | Revisión rápida dentro de la conversación, sin generar fichero |
| **PDF** | Documentos formales con narrativa en prosa, informes ejecutivos o de compliance |
| **DOCX** | Documentos Word editables para policy briefs e informes de compliance |
| **PPTX** | Decks de resumen ejecutivo, briefings a comités de dirección, walkthroughs de ontología |
| **Dashboard web** | HTML interactivo con KPI cards, filtros y tablas ordenables |
| **Póster / Infografía** | Resumen visual de una página para comunicación o exposición |
| **XLSX** | Workbook multi-hoja de cobertura, export de ontología, catálogo de términos, matriz de compliance con conditional formatting |
| **Markdown** | Formato de texto ligero para sistemas de documentación y wikis |

Cada formato visual aplica el tema que elijas al inicio del entregable (o el tema corporativo por defecto).

## Qué puedes preguntar

### Capa semántica
- "Construye la capa semántica del dominio X"
- "Genera descripciones técnicas para el dominio Y"
- "Crea una ontología para el dominio de clientes"
- "Crea business views y publícalas"
- "Genera términos semánticos para las vistas"
- "Crea un business term para CLV"
- "Crea una nueva data collection con tablas de X"
- "Ingiere este DOCX de política y propón business terms a partir del glosario"
- "Lee este deck de arquitectura y arranca la ontología a partir de él"

### Calidad del dato
- "¿Cuál es la cobertura de calidad del dominio de clientes?"
- "Crea reglas de calidad para cubrir los gaps del dominio X"
- "Crea una regla que verifique que el campo email tiene formato válido"
- "Programa la ejecución automática de las reglas del dominio de clientes"

### Informes y entregables
- "Genera un informe PDF de cobertura del dominio de ventas"
- "Crea un resumen ejecutivo PowerPoint de los hallazgos de calidad"
- "Construye un dashboard web interactivo de calidad para el equipo de operaciones"
- "Genera una infografía de una página con la cobertura por dominio"
- "Exporta el catálogo de reglas como un workbook Excel con conditional formatting"
- "Usa el tema forensic-audit para el informe de compliance"

### Flujos combinados
- "Construye la capa semántica del dominio X y después evalúa su calidad"
- "¿Qué artefactos de gobierno existen para el dominio Y?"
- "Construye la ontología de clientes y después genera un deck PowerPoint de briefing de compliance"
- "Evalúa la calidad y produce un workbook Excel con branding corporativo para el equipo de auditoría"

## Skills disponibles

### Capa semántica
| Comando | Descripción |
|---------|-------------|
| `/build-semantic-layer` | Pipeline completo de capa semántica: términos, ontología, vistas, mappings, términos semánticos |
| `/create-technical-terms` | Crear descripciones técnicas para tablas y columnas |
| `/create-ontology` | Crear, ampliar o eliminar clases de ontología con planificación interactiva |
| `/create-business-views` | Crear, regenerar o eliminar business views |
| `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas existentes |
| `/create-semantic-terms` | Generar términos semánticos de negocio para las vistas |
| `/manage-business-terms` | Crear business terms en el diccionario de gobierno |
| `/create-data-collection` | Buscar tablas en el diccionario y crear nuevas data collections |
| `/stratio-semantic-layer` | Referencia para las herramientas MCP de capa semántica (patrones, buenas prácticas) |

### Calidad del dato
| Comando | Descripción |
|---------|-------------|
| `/assess-quality` | Evaluar cobertura de calidad por dominio o tabla: dimensiones cubiertas, gaps y prioridades |
| `/create-quality-rules` | Diseñar y crear reglas de calidad con aprobación humana obligatoria |
| `/create-quality-schedule` | Crear planificaciones de ejecución automática de reglas de calidad |
| `/quality-report` | Generar informe formal de cobertura en Chat, PDF, DOCX, PPTX, Dashboard web, Póster/Infografía, XLSX o Markdown |

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
| `/pdf-writer` | Crear PDFs personalizados, combinar/dividir, marca de agua, cifrar, rellenar formularios |
| `/docx-writer` | Autorar y manipular documentos Word (combinar, dividir, find-replace, conversión de `.doc`) |
| `/pptx-writer` | Autorar y manipular decks PowerPoint (combinar, dividir, reordenar, find-replace) |
| `/xlsx-writer` | Autorar workbooks Excel multi-hoja (cobertura, catálogos de términos, specs de reglas), convertir `.xls` a `.xlsx` |

### Visuales y branding
| Comando | Descripción |
|---------|-------------|
| `/web-craft` | HTML interactivo standalone: dashboards, landing pages, componentes UI |
| `/canvas-craft` | Visuales de una página dominados por composición: pósters, infografías, portadas |
| `/brand-kit` | Catálogo centralizado de temas: 10 temas curados (corporate-formal, forensic-audit, luxury-refined, editorial-serious y más), extensible con temas propios del cliente |

## Conexiones necesarias

- **MCP de Gobierno**: gestión de capa semántica, dimensiones de calidad, creación y planificación de reglas
- **MCP de Datos**: exploración de dominios, profiling de datos, ejecución SQL

## Cómo empezar

Inicia el agente y pregunta: "Construye la capa semántica del dominio X" o "¿Cuál es la cobertura de calidad del dominio Y?"
