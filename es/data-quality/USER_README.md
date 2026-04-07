# Data Quality Agent

Agente experto en gobernanza y calidad del dato que evalúa la cobertura de calidad, identifica gaps y crea reglas de calidad.

## Que es este agente

Data Quality es un asistente especializado en calidad del dato que trabaja sobre tus datos gobernados. Puede evaluar la cobertura de calidad de un dominio, colección o tabla, identificar que dimensiones de calidad faltan, proponer reglas de calidad razonadas basadas en el contexto semántico y los datos reales, y crear esas reglas con tu aprobación. También genera informes de cobertura en múltiples formatos.

El agente evalúa la calidad en 11 dimensiones (completitud, unicidad, validez, consistencia, frescura, precisión, integridad referencial, disponibilidad, nivel de detalle, razonabilidad y trazabilidad) y siempre requiere tu aprobación antes de crear o modificar reglas.

## Capacidades

- Evaluar cobertura de calidad por dominio, colección, tabla o columna
- Identificar gaps: dimensiones de calidad no cubiertas, tablas o columnas sin cobertura
- Proponer reglas de calidad razonadas basadas en contexto semántico y datos reales
- Crear reglas de calidad con aprobación humana obligatoria (human-in-the-loop)
- Planificar la ejecución automática de reglas de calidad (scheduling)
- Generar informes de cobertura en chat, PDF, DOCX o Markdown
- Diagnosticar problemas de calidad con profiling de datos reales

## Qué puedes preguntarle

### Evaluación de cobertura
- "Cuál es la cobertura de calidad del dominio clientes?"
- "Qué tablas del dominio ventas no tienen reglas de calidad?"
- "Evalua la calidad de la columna email en la tabla clientes"
- "Qué dimensiones de calidad faltan en la tabla facturación?"

### Creación de reglas
- "Crea reglas de calidad para cubrir los gaps del dominio X"
- "Completa la cobertura de calidad de la tabla facturación"
- "Crea una regla que verifique que el campo email tiene formato válido"
- "Necesito reglas de unicidad para las claves primarias del dominio Y"

### Informes
- "Genera un informe PDF de cobertura de calidad del dominio ventas"
- "Escribe un informe en Markdown con el estado de calidad"
- "Dame un resumen de cobertura de todo el dominio"

### Planificación
- "Planifica la ejecución automática de las reglas del dominio clientes"
- "Crea una planificación diaria para las reglas de calidad"

### Consultas directas
- "Qué dimensiones de calidad existen?"
- "Qué reglas de calidad tiene la tabla X?"
- "Qué dominios de datos hay disponibles?"

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/assess-quality` | Evaluar cobertura de calidad por dominio o tabla: dimensiones cubiertas, gaps y prioridades |
| `/create-quality-rules` | Diseñar y crear reglas de calidad para cubrir gaps, con aprobación humana obligatoria |
| `/create-quality-planification` | Crear planificaciones de ejecución automática de reglas de calidad |
| `/quality-report` | Generar informe formal de cobertura en PDF, DOCX o Markdown |

## Conexiones necesarias

- **MCP de gobernanza**: dimensiones de calidad, creación y gestión de reglas, planificaciones
- **MCP de datos**: exploración de dominios, profiling de datos, ejecución SQL

## Primeros pasos

Inicia el agente y pregunta: "Cuál es la cobertura de calidad del dominio X?"
