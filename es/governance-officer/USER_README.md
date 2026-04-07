# Agente Governance Officer

Agente experto en gobierno que combina la construccion de capas semanticas y la gestion de calidad del dato en un unico asistente.

## Que hace este agente

Governance Officer es un asistente integral que gestiona ambos lados del gobierno del dato: construir capas semanticas y gestionar la calidad del dato. Puede construir ontologias, business views, SQL mappings y terminos semanticos para tus dominios de datos, y tambien evaluar la cobertura de calidad, identificar gaps, crear reglas de calidad y generar informes de cobertura.

El agente trabaja con Stratio Data Governance via herramientas MCP, orquestando el ciclo de vida completo de los artefactos de gobierno con tu aprobacion en cada paso critico.

## Capacidades

### Capa semantica
- Construir y mantener capas semanticas completas (ontologias, vistas, mappings, terminos)
- Publicar business views para revision
- Explorar dominios tecnicos y capas semanticas publicadas
- Planificacion interactiva de ontologias con lectura de ficheros locales
- Crear data collections (dominios tecnicos) a partir de busquedas en el diccionario de datos
- Gestionar business terms en el diccionario de gobierno

### Calidad del dato
- Evaluar la cobertura de calidad por dominio, coleccion, tabla o columna
- Identificar gaps: dimensiones de calidad no cubiertas, tablas o columnas sin cobertura
- Proponer reglas de calidad razonadas basadas en contexto semantico y datos reales
- Crear reglas de calidad con aprobacion humana obligatoria (human-in-the-loop)
- Programar la ejecucion automatica de reglas de calidad
- Generar informes de cobertura en chat, PDF, DOCX o Markdown

## Que puedes preguntar

### Capa semantica
- "Construye la capa semantica del dominio X"
- "Genera descripciones tecnicas para el dominio Y"
- "Crea una ontologia para el dominio de clientes"
- "Crea business views y publicalas"
- "Genera terminos semanticos para las vistas"
- "Crea un business term para CLV"
- "Crea una nueva data collection con tablas de X"

### Calidad del dato
- "Cual es la cobertura de calidad del dominio de clientes?"
- "Crea reglas de calidad para cubrir los gaps del dominio X"
- "Crea una regla que verifique que el campo email tiene formato valido"
- "Genera un informe de cobertura en PDF para el dominio de ventas"
- "Programa la ejecucion automatica de las reglas del dominio de clientes"

### Flujos combinados
- "Construye la capa semantica del dominio X y luego evalua su calidad"
- "Que artefactos de gobierno existen para el dominio Y?"

## Skills disponibles

| Comando | Descripcion |
|---------|-------------|
| `/build-semantic-layer` | Pipeline completo de capa semantica: terminos, ontologia, vistas, mappings, terminos semanticos |
| `/generate-technical-terms` | Generar descripciones tecnicas para tablas y columnas |
| `/create-ontology` | Crear, extender o eliminar clases de ontologia con planificacion interactiva |
| `/create-business-views` | Crear, regenerar o eliminar business views |
| `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas existentes |
| `/create-semantic-terms` | Generar terminos semanticos de negocio para vistas |
| `/manage-business-terms` | Crear business terms en el diccionario de gobierno |
| `/create-data-collection` | Buscar tablas en el diccionario y crear nuevas data collections |
| `/assess-quality` | Evaluar la cobertura de calidad por dominio o tabla |
| `/create-quality-rules` | Disenar y crear reglas de calidad con aprobacion humana obligatoria |
| `/create-quality-planification` | Crear planificaciones de ejecucion automatica para reglas de calidad |
| `/quality-report` | Generar un informe formal de cobertura en PDF, DOCX o Markdown |

## Conexiones necesarias

- **MCP de Gobierno**: gestion de capa semantica, dimensiones de calidad, creacion de reglas
- **MCP de Datos**: exploracion de dominios, profiling de datos, ejecucion SQL

## Como empezar

Inicia el agente y pregunta: "Construye la capa semantica del dominio X" o "Cual es la cobertura de calidad del dominio Y?"
