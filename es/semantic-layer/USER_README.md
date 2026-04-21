# Semantic Layer Builder Agent

Agente especialista en construcción y mantenimiento de capas semánticas en Stratio Data Governance.

## Que es este agente

Semantic Layer Builder te guía en la creación, mantenimiento y publicación de los artefactos de gobernanza que componen la capa semántica de un dominio de datos. Trabaja con un pipeline de 5 fases — desde la descripción técnica de tablas hasta la generación de términos semánticos de negocio — y puede ejecutar cada fase de forma independiente o como un pipeline completo.

El agente no ejecuta queries de datos ni genera ficheros en disco. Su output es la interacción directa con las herramientas de gobernanza y resúmenes en chat.

## Capacidades

- Construir capas semánticas completas con un pipeline guiado de 5 fases
- Generar descripciones técnicas automáticas de tablas y columnas
- Crear y gestionar ontologías con planificación interactiva
- Crear vistas de negocio a partir de ontologías existentes
- Generar y actualizar SQL mappings para vistas de negocio
- Crear términos semánticos de negocio
- Gestionar business terms con relaciones a activos de datos
- Crear colecciones de datos (dominios técnicos) desde busquedas en el diccionario
- Diagnosticar el estado de la capa semántica de un dominio
- Leer ficheros locales (.owl, .ttl, CSV, documentos) para enriquecer la planificación

## Qué puedes preguntarle

### Pipeline completo
- "Construye la capa semántica del dominio clientes"
- "Quiero crear la capa semántica para el dominio de facturación desde cero"

### Fases individuales
- "Genera las descripciones técnicas de las tablas del dominio ventas"
- "Crea una ontología para el dominio de clientes"
- "Crea las vistas de negocio a partir de la ontología existente"
- "Actualiza los SQL mappings de las vistas del dominio"
- "Genera los términos semánticos para las vistas publicadas"

### Gestión de artefactos
- "Crea un business term para Customer Lifetime Value"
- "Crea una colección de datos con las tablas de facturación"
- "Publica las vistas de negocio del dominio Y"

### Exploración y diagnóstico
- "Cuál es el estado de la capa semántica del dominio X?"
- "Qué tablas hay sobre clientes en el diccionario de datos?"
- "Qué dominios de datos hay disponibles?"

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/build-semantic-layer` | Pipeline completo de 5 fases para construir la capa semántica de un dominio |
| `/create-technical-terms` | Crear descripciones técnicas automáticas de tablas y columnas |
| `/create-ontology` | Crear, ampliar o eliminar clases de ontología con planificación interactiva |
| `/create-business-views` | Crear, regenerar o eliminar vistas de negocio desde una ontología |
| `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas de negocio existentes |
| `/create-semantic-terms` | Generar términos semánticos de negocio para las vistas de un dominio |
| `/manage-business-terms` | Crear business terms con relaciones a activos de datos |
| `/create-data-collection` | Buscar tablas en el diccionario y crear una nueva colección de datos |

## Conexiones necesarias

- **MCP de gobernanza**: creación y gestión de artefactos semánticos (ontologías, vistas, términos, business terms)
- **MCP de datos**: exploración de dominios y diccionario de datos

## Primeros pasos

Inicia el agente y pregunta: "Cuál es el estado de la capa semántica del dominio X?"
