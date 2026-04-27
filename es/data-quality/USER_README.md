# Data Quality Agent

Agente experto en gobernanza y calidad del dato que evalúa la cobertura de calidad, identifica gaps, crea reglas de calidad y entrega informes de cobertura en ocho formatos diferentes.

## Qué es este agente

Data Quality es un asistente especializado en calidad del dato que trabaja sobre tus datos gobernados. Puede evaluar la cobertura de calidad de un dominio, colección o tabla, identificar qué dimensiones de calidad faltan, proponer reglas razonadas basadas en el contexto semántico y el profiling real, y crearlas con tu aprobación. También genera informes de cobertura en múltiples formatos — desde un resumen rápido en chat hasta un workbook Excel multi-hoja, un dashboard web interactivo o una infografía imprimible.

El agente evalúa la calidad en 11 dimensiones (completitud, unicidad, validez, consistencia, frescura, precisión, integridad referencial, disponibilidad, nivel de detalle, razonabilidad y trazabilidad) y siempre requiere tu aprobación antes de crear o modificar reglas. También puede ingerir contexto local (workbooks de specs de reglas en Excel, policy briefs en Word, decks de referencia en PowerPoint, PDFs de regulación) y aplicar branding visual consistente a cada entregable.

## Capacidades

- Evaluar cobertura de calidad por dominio, colección, tabla o columna
- Identificar gaps: dimensiones de calidad no cubiertas, tablas o columnas sin cobertura
- Proponer reglas de calidad razonadas basadas en contexto semántico y profiling real
- Crear reglas de calidad con aprobación humana obligatoria (human-in-the-loop)
- Planificar la ejecución automática de reglas de calidad
- Generar informes de cobertura en 8 formatos (ver [Formatos de salida](#formatos-de-salida))
- Leer y extraer contenido de ficheros PDF, Word, PowerPoint y Excel (políticas, specs de reglas, catálogos de referencia)
- Autorar compliance briefs, decks ejecutivos, workbooks de specs de reglas y visuales standalone (pósters, dashboards)
- Aplicar identidad visual consistente a cada informe mediante el catálogo centralizado de temas (10 temas curados, extensible por cliente)
- Diagnosticar problemas de calidad con profiling de datos reales

## Formatos de salida

Para `/quality-report` puedes elegir cualquiera de:

| Formato | Ideal para |
|---|---|
| **Chat** | Revisión rápida dentro de la conversación, sin fichero |
| **PDF** | Informe formal con narrativa en prosa, firma de compliance |
| **DOCX** | Documento Word editable para equipos de auditoría y policy briefs |
| **PPTX** | Deck de resumen ejecutivo, briefing a comité de dirección |
| **Dashboard web** | HTML interactivo con KPI cards, filtros, tablas ordenables |
| **Informe web / Artículo web** | Página HTML editorial autocontenida con secciones narrativas, callouts KPI inline y gráficos incrustados |
| **Póster / Infografía** | Resumen visual de una página con cobertura por dominio |
| **XLSX** | Workbook multi-hoja de cobertura con conditional formatting para auditoría y compliance |
| **Markdown** | Formato de texto ligero para sistemas de documentación y wikis |

Cada formato visual aplica el tema que elijas al inicio (o el tema corporativo por defecto).

## Qué puedes preguntarle

### Evaluación de cobertura
- "¿Cuál es la cobertura de calidad del dominio clientes?"
- "¿Qué tablas del dominio ventas no tienen reglas de calidad?"
- "Evalúa la calidad de la columna email en la tabla clientes"
- "¿Qué dimensiones de calidad faltan en la tabla facturación?"

### Creación de reglas
- "Crea reglas de calidad para cubrir los gaps del dominio X"
- "Completa la cobertura de calidad de la tabla facturación"
- "Crea una regla que verifique que el campo email tiene formato válido"
- "Necesito reglas de unicidad para las claves primarias del dominio Y"

### Informes (generación de ficheros)
- "Genera un informe PDF de cobertura de calidad del dominio ventas"
- "Crea un resumen ejecutivo PowerPoint de los hallazgos de calidad"
- "Construye un dashboard web interactivo de calidad"
- "Genera una infografía de una página con la cobertura por dominio"
- "Exporta el catálogo de reglas como un workbook Excel con conditional formatting"
- "Usa el tema forensic-audit para este informe de compliance"
- "Escribe un resumen Markdown con el estado de calidad"

### Lectura de contexto local
- "Lee este workbook Excel de specs de reglas y crea las reglas que define"
- "Extrae los requisitos de compliance de este DOCX de política"
- "Lee el catálogo de términos en este PDF para arrancar la revisión de reglas"

### Planificación
- "Planifica la ejecución automática de las reglas del dominio clientes"
- "Crea una planificación diaria para las reglas de calidad"

### Consultas directas
- "¿Qué dimensiones de calidad existen?"
- "¿Qué reglas de calidad tiene la tabla X?"
- "¿Qué dominios de datos hay disponibles?"

## Skills disponibles

### Evaluación, diseño e informes de calidad
| Comando | Descripción |
|---------|-------------|
| `/assess-quality` | Evaluar cobertura de calidad por dominio o tabla: dimensiones cubiertas, gaps y prioridades |
| `/create-quality-rules` | Diseñar y crear reglas de calidad para cubrir gaps, con aprobación humana obligatoria |
| `/create-quality-schedule` | Crear planificaciones de ejecución automática de reglas de calidad |
| `/quality-report` | Generar informe formal de cobertura en Chat, PDF, DOCX, PPTX, Dashboard web, Informe web / Artículo web, Póster/Infografía, XLSX o Markdown |

### Lectores de contenido
| Comando | Descripción |
|---------|-------------|
| `/pdf-reader` | Extraer texto, tablas, imágenes, formularios y adjuntos de ficheros PDF |
| `/docx-reader` | Extraer contenido de documentos Word (`.docx` y `.doc` legacy) |
| `/pptx-reader` | Extraer diapositivas, notas y assets embebidos de decks PowerPoint |
| `/xlsx-reader` | Leer valores de celda, tablas, fórmulas y metadatos de workbooks Excel (specs de reglas, catálogos de términos) |

### Escritores de contenido
| Comando | Descripción |
|---------|-------------|
| `/pdf-writer` | Crear PDFs personalizados, combinar/dividir, marca de agua, cifrar, rellenar formularios |
| `/docx-writer` | Autorar y manipular documentos Word (combinar, dividir, find-replace, conversión de `.doc`) |
| `/pptx-writer` | Autorar y manipular decks PowerPoint para resúmenes ejecutivos y training de reglas |
| `/xlsx-writer` | Autorar workbooks Excel multi-hoja (cobertura, plantillas de specs de reglas, catálogos de términos), convertir `.xls` a `.xlsx` |

### Visuales y branding
| Comando | Descripción |
|---------|-------------|
| `/web-craft` | HTML interactivo standalone: dashboards, landing pages, componentes UI |
| `/canvas-craft` | Visuales de una página dominados por composición: pósters, infografías, portadas |
| `/brand-kit` | Catálogo centralizado de temas: 10 temas curados (corporate-formal, forensic-audit, luxury-refined, editorial-serious y más), extensible con temas propios del cliente |

## Conexiones necesarias

- **MCP de gobernanza**: dimensiones de calidad, creación y gestión de reglas, planificaciones
- **MCP de datos**: exploración de dominios, profiling de datos, ejecución SQL

## Primeros pasos

Inicia el agente y pregunta: "¿Cuál es la cobertura de calidad del dominio X?"
