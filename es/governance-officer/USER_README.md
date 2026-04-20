# Agente Governance Officer

Agente experto en gobierno que combina la construcción de capas semánticas y la gestión de calidad del dato en un único asistente.

## Que hace este agente

Governance Officer es un asistente integral que gestiona ambos lados del gobierno del dato: construir capas semánticas y gestionar la calidad del dato. Puede construir ontologías, business views, SQL mappings y términos semánticos para tus dominios de datos, y también evaluar la cobertura de calidad, identificar gaps, crear reglas de calidad y generar informes de cobertura.

El agente trabaja con Stratio Data Governance vía herramientas MCP, orquestando el ciclo de vida completo de los artefactos de gobierno con tu aprobación en cada paso crítico.

## Capacidades

### Capa semántica
- Construir y mantener capas semánticas completas (ontologías, vistas, mappings, términos)
- Publicar business views para revisión
- Explorar dominios técnicos y capas semánticas publicadas
- Planificación interactiva de ontologías con lectura de ficheros locales
- Crear data collections (dominios técnicos) a partir de busquedas en el diccionario de datos
- Gestionar business terms en el diccionario de gobierno

### Calidad del dato
- Evaluar la cobertura de calidad por dominio, colección, tabla o columna
- Identificar gaps: dimensiones de calidad no cubiertas, tablas o columnas sin cobertura
- Proponer reglas de calidad razonadas basadas en contexto semántico y datos reales
- Crear reglas de calidad con aprobación humana obligatoria (human-in-the-loop)
- Programar la ejecución automática de reglas de calidad
- Generar informes de cobertura en chat, PDF, DOCX o Markdown

## Qué puedes preguntar

### Capa semántica
- "Construye la capa semántica del dominio X"
- "Genera descripciones técnicas para el dominio Y"
- "Crea una ontología para el dominio de clientes"
- "Crea business views y publicalas"
- "Genera términos semánticos para las vistas"
- "Crea un business term para CLV"
- "Crea una nueva data collection con tablas de X"

### Calidad del dato
- "Cuál es la cobertura de calidad del dominio de clientes?"
- "Crea reglas de calidad para cubrir los gaps del dominio X"
- "Crea una regla que verifique que el campo email tiene formato válido"
- "Genera un informe de cobertura en PDF para el dominio de ventas"
- "Programa la ejecución automática de las reglas del dominio de clientes"

### Flujos combinados
- "Construye la capa semántica del dominio X y luego evalúa su calidad"
- "Qué artefactos de gobierno existen para el dominio Y?"

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/build-semantic-layer` | Pipeline completo de capa semántica: términos, ontología, vistas, mappings, términos semánticos |
| `/generate-technical-terms` | Generar descripciones técnicas para tablas y columnas |
| `/create-ontology` | Crear, extender o eliminar clases de ontología con planificación interactiva |
| `/create-business-views` | Crear, regenerar o eliminar business views |
| `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas existentes |
| `/create-semantic-terms` | Generar términos semánticos de negocio para vistas |
| `/manage-business-terms` | Crear business terms en el diccionario de gobierno |
| `/create-data-collection` | Buscar tablas en el diccionario y crear nuevas data collections |
| `/assess-quality` | Evaluar la cobertura de calidad por dominio o tabla |
| `/create-quality-rules` | Diseñar y crear reglas de calidad con aprobación humana obligatoria |
| `/create-quality-planification` | Crear planificaciones de ejecución automática para reglas de calidad |
| `/quality-report` | Generar un informe formal de cobertura en PDF, DOCX o Markdown |
| `/pdf-reader` | Leer y extraer contenido de archivos PDF (texto, tablas, imágenes, formularios) |
| `/pdf-writer` | Crear documentos PDF personalizados, combinar/dividir PDFs, añadir marcas de agua, cifrar, rellenar formularios |

## Conexiones necesarias

- **MCP de Gobierno**: gestión de capa semántica, dimensiones de calidad, creación de reglas
- **MCP de Datos**: exploración de dominios, profiling de datos, ejecución SQL

## Como empezar

Inicia el agente y pregunta: "Construye la capa semántica del dominio X" o "Cuál es la cobertura de calidad del dominio Y?"
