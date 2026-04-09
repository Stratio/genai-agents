---
name: create-ontology
description: "Crear, ampliar o borrar clases de una ontología en Stratio Governance. Incluye planificación interactiva con el usuario (dominio, ficheros de referencia, clases, nomenclaturas) antes de crear."
argument-hint: "[dominio técnico (opcional)]"
---

# Skill: Crear, Ampliar o Borrar Clases de Ontología

Crea, amplia o borra clases de una ontología en Stratio Governance mediante planificación interactiva con el usuario. Fase 2 del pipeline de capa semántica.

## Tools MCP utilizadas

| Tool | Servidor | Propósito |
|------|----------|-----------|
| `search_domains(search_text, domain_type='technical')` | sql | **Preferir**. Buscar dominios técnicos por texto libre. Resultados por relevancia |
| `list_domains(domain_type='technical', refresh?)` | sql | Listar todos los dominios técnicos. `refresh=true` para bypass de cache |
| `list_domain_tables(domain)` | sql | Conocer tablas del dominio |
| `get_tables_details(domain, tables)` | sql | Detalle de tablas: reglas de negocio, contexto |
| `get_table_columns_details(domain, table)` | sql | Columnas de una tabla (para planificar data properties) |
| `search_domain_knowledge(question, domain)` | sql | Buscar conocimiento existente |
| `search_ontologies(search_text)` | gov | Buscar ontologías por texto libre. Resultados por relevancia |
| `list_ontologies()` | gov | Listar todas las ontologías existentes |
| `get_ontology_info(name)` | gov | Estructura de clases, data properties y relaciones |
| `create_ontology(domain, name, ontology_plan)` | gov | Crear ontología nueva con plan en Markdown |
| `update_ontology(domain, name, update_plan)` | gov | Añadir clases nuevas a ontología existente |
| `delete_ontology_classes(ontology_name, class_names)` | gov | DESTRUCTIVO: borrar clases específicas (protegido por Published) |

**Reglas clave**: `domain_name` inmutable. Ontologías son ADD+DELETE: `update` añade clases, `delete_ontology_classes` borra clases (protegido: clases con vistas Published dependientes se saltan). No se pueden modificar clases existentes. Nomenclatura: sin espacios (→ guiones bajos), sin caracteres especiales. Ofrecer `user_instructions` antes de invocar.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene un nombre de dominio, buscar con `search_domains($ARGUMENTS, domain_type='technical')`. Si no coincide, reintentar con `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` por si es una colección recién creada. Si ahora coincide, continuar. Si sigue sin coincidir o no hay argumento, listar dominios con `list_domains(domain_type='technical')` y preguntar al usuario siguiendo la convención de preguntas al usuario.

### 2. Evaluar ontologías existentes

Ejecutar en paralelo:
- `search_ontologies(dominio_o_contexto)` o `list_ontologies()` → ontologías existentes. Preferir `search_ontologies` si el usuario menciona una ontología concreta; usar `list_ontologies()` si se necesita el listado completo
- `list_domain_tables(domain)` → tablas disponibles para la ontología

Si hay ontologías, mostrar al usuario:
- "No hay ontología → crearemos una nueva"
- "Ya existe [nombre] con N clases → podemos ampliar, borrar clases o crear una nueva"

Si aplica, ejecutar `get_ontology_info(name)` para mostrar estructura existente.

### 3. Planificación interactiva

Este es el nucleo de la skill. Preguntar al usuario agrupando para minimizar interacciones:

**Bloque de preguntas** (una sola interacción):
- ¿Tiene ficheros adicionales con información relevante? (ontologías .owl/.ttl, documentos de negocio, CSVs). Si proporciona rutas → **leer los ficheros** para extraer contexto
- ¿Tiene ontologías existentes como referencia? (si si → `get_ontology_info` o leer fichero local)
- ¿Que clases o entidades considera indispensables?
- ¿Aspectos importantes sobre formato y nomenclaturas?
- ¿Instrucciones adicionales para la IA que generará la ontología?

**Exploración del dominio** (en paralelo con la interacción si es posible):
- `list_domain_tables(domain)` + `get_tables_details(domain, tables)` → entender tablas y su contexto
- `get_table_columns_details(domain, table)` para tablas clave → datos disponibles para data properties
- `search_domain_knowledge(question, domain)` → terminología existente

**Proponer plan**:
1. Proponer nombre de ontología (sin espacios → guiones bajos, sin caracteres especiales)
2. Proponer **plan en Markdown** con:
   - Clases propuestas con descripción
   - Data properties por clase
   - Relaciones entre clases
   - Tablas fuente de cada clase
3. Presentar plan al usuario para revisión
4. Iterar hasta aprobación (max 3 iteraciones de refinamiento)

### 4. Ejecución

Según decisión del paso 2:
- **Nueva ontología**: `create_ontology(domain, name, ontology_plan)` con el plan aprobado en Markdown
- **Ampliar existente**: `update_ontology(domain, name, update_plan)` — solo clases nuevas
- **Borrar clases**: Operación DESTRUCTIVA — confirmar con el usuario listando las clases a borrar y advirtiendo que las vistas de negocio dependientes se refrescaran. Ejecutar `delete_ontology_classes(ontology_name, class_names)`. Informar del resultado: clases borradas (`deleted`) y clases saltadas por tener vistas Published (`skipped_locked`)

### 5. Verificación

Ejecutar `get_ontology_info(name)` para confirmar la estructura creada. Presentar al usuario:
- Clases generadas con sus data properties
- Relaciones establecidas
- Diferencias respecto al plan (si las hay)

Ofrecer proactivamente: "Si tras revisarla quieres eliminar alguna clase, puedo hacerlo (las clases con vistas Published no se pueden borrar)." No bloqueante — el usuario decide si continuar o borrar algo.

### 6. Resumen

- Ontología creada/ampliada con nombre y número de clases
- Clases generadas vs planificadas
- Advertencias o problemas encontrados
- Siguiente paso sugerido: "Puedes crear las vistas de negocio con `/create-business-views`"
