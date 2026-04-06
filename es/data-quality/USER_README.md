# Data Quality Agent

Agente experto en gobernanza y calidad del dato que evalua la cobertura de calidad, identifica gaps y crea reglas de calidad.

## Que es este agente

Data Quality es un asistente especializado en calidad del dato que trabaja sobre tus datos gobernados. Puede evaluar la cobertura de calidad de un dominio, coleccion o tabla, identificar que dimensiones de calidad faltan, proponer reglas de calidad razonadas basadas en el contexto semantico y los datos reales, y crear esas reglas con tu aprobacion. Tambien genera informes de cobertura en multiples formatos.

El agente evalua la calidad en 11 dimensiones (completitud, unicidad, validez, consistencia, frescura, precision, integridad referencial, disponibilidad, nivel de detalle, razonabilidad y trazabilidad) y siempre requiere tu aprobacion antes de crear o modificar reglas.

## Capacidades

- Evaluar cobertura de calidad por dominio, coleccion, tabla o columna
- Identificar gaps: dimensiones de calidad no cubiertas, tablas o columnas sin cobertura
- Proponer reglas de calidad razonadas basadas en contexto semantico y datos reales
- Crear reglas de calidad con aprobacion humana obligatoria (human-in-the-loop)
- Planificar la ejecucion automatica de reglas de calidad (scheduling)
- Generar informes de cobertura en chat, PDF, DOCX o Markdown
- Diagnosticar problemas de calidad con profiling de datos reales

## Que puedes preguntarle

### Evaluacion de cobertura
- "Cual es la cobertura de calidad del dominio clientes?"
- "Que tablas del dominio ventas no tienen reglas de calidad?"
- "Evalua la calidad de la columna email en la tabla clientes"
- "Que dimensiones de calidad faltan en la tabla facturacion?"

### Creacion de reglas
- "Crea reglas de calidad para cubrir los gaps del dominio X"
- "Completa la cobertura de calidad de la tabla facturacion"
- "Crea una regla que verifique que el campo email tiene formato valido"
- "Necesito reglas de unicidad para las claves primarias del dominio Y"

### Informes
- "Genera un informe PDF de cobertura de calidad del dominio ventas"
- "Escribe un informe en Markdown con el estado de calidad"
- "Dame un resumen de cobertura de todo el dominio"

### Planificacion
- "Planifica la ejecucion automatica de las reglas del dominio clientes"
- "Crea una planificacion diaria para las reglas de calidad"

### Consultas directas
- "Que dimensiones de calidad existen?"
- "Que reglas de calidad tiene la tabla X?"
- "Que dominios de datos hay disponibles?"

## Skills disponibles

| Comando | Descripcion |
|---------|-------------|
| `/assess-quality` | Evaluar cobertura de calidad por dominio o tabla: dimensiones cubiertas, gaps y prioridades |
| `/create-quality-rules` | Disenar y crear reglas de calidad para cubrir gaps, con aprobacion humana obligatoria |
| `/create-quality-planification` | Crear planificaciones de ejecucion automatica de reglas de calidad |
| `/quality-report` | Generar informe formal de cobertura en PDF, DOCX o Markdown |

## Conexiones necesarias

- **MCP de gobernanza**: dimensiones de calidad, creacion y gestion de reglas, planificaciones
- **MCP de datos**: exploracion de dominios, profiling de datos, ejecucion SQL

## Primeros pasos

Inicia el agente y pregunta: "Cual es la cobertura de calidad del dominio X?"
