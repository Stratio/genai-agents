# Semantic Layer Builder Agent

Agente especialista en construccion y mantenimiento de capas semanticas en Stratio Data Governance.

## Que es este agente

Semantic Layer Builder te guia en la creacion, mantenimiento y publicacion de los artefactos de gobernanza que componen la capa semantica de un dominio de datos. Trabaja con un pipeline de 5 fases — desde la descripcion tecnica de tablas hasta la generacion de terminos semanticos de negocio — y puede ejecutar cada fase de forma independiente o como un pipeline completo.

El agente no ejecuta queries de datos ni genera ficheros en disco. Su output es la interaccion directa con las herramientas de gobernanza y resumenes en chat.

## Capacidades

- Construir capas semanticas completas con un pipeline guiado de 5 fases
- Generar descripciones tecnicas automaticas de tablas y columnas
- Crear y gestionar ontologias con planificacion interactiva
- Crear vistas de negocio a partir de ontologias existentes
- Generar y actualizar SQL mappings para vistas de negocio
- Crear terminos semanticos de negocio
- Gestionar business terms con relaciones a activos de datos
- Crear colecciones de datos (dominios tecnicos) desde busquedas en el diccionario
- Diagnosticar el estado de la capa semantica de un dominio
- Leer ficheros locales (.owl, .ttl, CSV, documentos) para enriquecer la planificacion

## Que puedes preguntarle

### Pipeline completo
- "Construye la capa semantica del dominio clientes"
- "Quiero crear la capa semantica para el dominio de facturacion desde cero"

### Fases individuales
- "Genera las descripciones tecnicas de las tablas del dominio ventas"
- "Crea una ontologia para el dominio de clientes"
- "Crea las vistas de negocio a partir de la ontologia existente"
- "Actualiza los SQL mappings de las vistas del dominio"
- "Genera los terminos semanticos para las vistas publicadas"

### Gestion de artefactos
- "Crea un business term para Customer Lifetime Value"
- "Crea una coleccion de datos con las tablas de facturacion"
- "Publica las vistas de negocio del dominio Y"

### Exploracion y diagnostico
- "Cual es el estado de la capa semantica del dominio X?"
- "Que tablas hay sobre clientes en el diccionario de datos?"
- "Que dominios de datos hay disponibles?"

## Skills disponibles

| Comando | Descripcion |
|---------|-------------|
| `/build-semantic-layer` | Pipeline completo de 5 fases para construir la capa semantica de un dominio |
| `/generate-technical-terms` | Generar descripciones tecnicas automaticas de tablas y columnas |
| `/create-ontology` | Crear, ampliar o eliminar clases de ontologia con planificacion interactiva |
| `/create-business-views` | Crear, regenerar o eliminar vistas de negocio desde una ontologia |
| `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas de negocio existentes |
| `/create-semantic-terms` | Generar terminos semanticos de negocio para las vistas de un dominio |
| `/manage-business-terms` | Crear business terms con relaciones a activos de datos |
| `/create-data-collection` | Buscar tablas en el diccionario y crear una nueva coleccion de datos |

## Conexiones necesarias

- **MCP de gobernanza**: creacion y gestion de artefactos semanticos (ontologias, vistas, terminos, business terms)
- **MCP de datos**: exploracion de dominios y diccionario de datos

## Primeros pasos

Inicia el agente y pregunta: "Cual es el estado de la capa semantica del dominio X?"
