# Semantic Layer Builder Agent

Agente especialista en construcción y mantenimiento de capas semánticas en Stratio Data Governance — el pipeline completo desde descripciones técnicas de tablas hasta términos semánticos de negocio, con planificación interactiva y capacidad para ingerir tus propios documentos de especificación.

## Qué es este agente

Semantic Layer Builder te guía en la creación, mantenimiento y publicación de los artefactos de gobernanza que componen la capa semántica de un dominio de datos. Trabaja con un pipeline de 5 fases — desde la descripción técnica de tablas hasta la generación de términos semánticos de negocio — y puede ejecutar cada fase de forma independiente o como un pipeline completo.

El agente también puede ingerir contexto local para enriquecer la planificación: especificaciones Word con glosarios y reglas de negocio, decks PowerPoint con walkthroughs de arquitectura, catálogos CSV y ficheros de ontología (`.owl`, `.ttl`).

No ejecuta queries de datos ni genera ficheros en disco — su output es la interacción directa con las herramientas de gobernanza y resúmenes en chat.

## Capacidades

- Construir capas semánticas completas con un pipeline guiado de 5 fases
- Generar descripciones técnicas automáticas de tablas y columnas
- Crear y gestionar ontologías con planificación interactiva
- Crear business views a partir de ontologías existentes
- Generar y actualizar SQL mappings para business views
- Crear términos semánticos de negocio
- Gestionar business terms con relaciones a activos de datos
- Crear data collections (dominios técnicos) desde búsquedas en el diccionario
- Diagnosticar el estado de la capa semántica de un dominio
- Ingerir documentos locales de especificación para enriquecer la planificación: ficheros Word (`.docx`/`.doc`), decks PowerPoint (`.pptx`/`.ppt`), catálogos CSV y ficheros de ontología (`.owl`, `.ttl`)

## Qué puedes preguntarle

### Pipeline completo
- "Construye la capa semántica del dominio clientes"
- "Quiero crear la capa semántica para el dominio de facturación desde cero"

### Fases individuales
- "Genera las descripciones técnicas de las tablas del dominio ventas"
- "Crea una ontología para el dominio de clientes"
- "Crea las business views a partir de la ontología existente"
- "Actualiza los SQL mappings de las vistas del dominio"
- "Genera los términos semánticos para las vistas publicadas"

### Gestión de artefactos
- "Crea un business term para Customer Lifetime Value"
- "Crea una data collection con las tablas de facturación"
- "Publica las business views del dominio Y"

### Ingesta de especificaciones locales
- "Ingiere este DOCX de política y propón business terms a partir del glosario"
- "Lee este deck de arquitectura y arranca la ontología a partir de él"
- "Usa este CSV como semilla para los technical terms"

### Exploración y diagnóstico
- "¿Cuál es el estado de la capa semántica del dominio X?"
- "¿Qué tablas hay sobre clientes en el diccionario de datos?"
- "¿Qué dominios de datos hay disponibles?"

## Skills disponibles

### Pipeline de capa semántica
| Comando | Descripción |
|---------|-------------|
| `/build-semantic-layer` | Pipeline completo de 5 fases para construir la capa semántica de un dominio |
| `/create-technical-terms` | Crear descripciones técnicas automáticas de tablas y columnas |
| `/create-ontology` | Crear, ampliar o eliminar clases de ontología con planificación interactiva |
| `/create-business-views` | Crear, regenerar o eliminar business views desde una ontología |
| `/create-sql-mappings` | Crear o actualizar SQL mappings para business views existentes |
| `/create-semantic-terms` | Generar términos semánticos de negocio para las vistas de un dominio |
| `/manage-business-terms` | Crear business terms con relaciones a activos de datos |
| `/create-data-collection` | Buscar tablas en el diccionario y crear una nueva data collection |

### Ingesta de ficheros locales
| Comando | Descripción |
|---------|-------------|
| `/docx-reader` | Leer documentos Word (`.docx` y `.doc` legacy) — especificaciones, glosarios, reglas de negocio |
| `/pptx-reader` | Leer decks PowerPoint (`.pptx` y `.ppt` legacy) — walkthroughs de arquitectura, decks de especificación |

### Referencia de herramientas MCP
| Comando | Descripción |
|---------|-------------|
| `/stratio-semantic-layer` | Referencia para las herramientas MCP de capa semántica: patrones, buenas prácticas, guía tool-by-tool |

## Conexiones necesarias

- **MCP de gobernanza**: creación y gestión de artefactos semánticos (ontologías, vistas, términos, business terms)
- **MCP de datos**: exploración de dominios y diccionario de datos

## Primeros pasos

Inicia el agente y pregunta: "¿Cuál es el estado de la capa semántica del dominio X?"
