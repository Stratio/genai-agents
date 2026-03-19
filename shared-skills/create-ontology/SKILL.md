---
name: create-ontology
description: Crear, ampliar o borrar clases de una ontologia en Stratio Governance.
  Incluye planificacion interactiva con el usuario (dominio, ficheros de referencia,
  clases, nomenclaturas) antes de crear.
argument-hint: [dominio tecnico (opcional)]
---

# Skill: Crear, Ampliar o Borrar Clases de Ontologia

Crea, amplia o borra clases de una ontologia en Stratio Governance mediante planificacion interactiva con el usuario. Fase 2 del pipeline de capa semantica.

## Tools MCP utilizadas

| Tool | Servidor | Proposito |
|------|----------|-----------|
| `stratio_list_technical_domains` | sql | Descubrir dominios tecnicos disponibles |
| `stratio_list_domain_tables(domain)` | sql | Conocer tablas del dominio |
| `stratio_get_tables_details(domain, tables)` | sql | Detalle de tablas: reglas de negocio, contexto |
| `stratio_get_table_columns_details(domain, table)` | sql | Columnas de una tabla (para planificar data properties) |
| `stratio_search_domain_knowledge(question, domain)` | sql | Buscar conocimiento existente |
| `stratio_list_ontologies()` | gov | Listar ontologias existentes |
| `stratio_get_ontology_info(name)` | gov | Estructura de clases, data properties y relaciones |
| `stratio_create_ontology(domain, name, ontology_plan)` | gov | Crear ontologia nueva con plan en Markdown |
| `stratio_update_ontology(domain, name, update_plan)` | gov | Anadir clases nuevas a ontologia existente |
| `stratio_delete_ontology_classes(ontology_name, class_names)` | gov | DESTRUCTIVO: borrar clases especificas (protegido por Published) |

**Reglas clave**: `domain_name` inmutable. Ontologias son ADD+DELETE: `update` anade clases, `delete_ontology_classes` borra clases (protegido: clases con vistas Published dependientes se saltan). No se pueden modificar clases existentes. Nomenclatura: sin espacios (→ guiones bajos), sin caracteres especiales. Ofrecer `user_instructions` antes de invocar.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene un nombre de dominio, validar contra `stratio_list_technical_domains`. Si no coincide o no hay argumento, listar dominios y preguntar al usuario siguiendo la convencion de preguntas al usuario.

### 2. Evaluar ontologias existentes

Ejecutar en paralelo:
- `stratio_list_ontologies()` → listar ontologias
- `stratio_list_domain_tables(domain)` → tablas disponibles para la ontologia

Si hay ontologias, mostrar al usuario:
- "No hay ontologia → crearemos una nueva"
- "Ya existe [nombre] con N clases → podemos ampliar, borrar clases o crear una nueva"

Si aplica, ejecutar `stratio_get_ontology_info(name)` para mostrar estructura existente.

### 3. Planificacion interactiva

Este es el nucleo de la skill. Preguntar al usuario agrupando para minimizar interacciones:

**Bloque de preguntas** (una sola interaccion):
- ¿Tiene ficheros adicionales con informacion relevante? (ontologias .owl/.ttl, documentos de negocio, CSVs). Si proporciona rutas → **leer los ficheros** para extraer contexto
- ¿Tiene ontologias existentes como referencia? (si si → `stratio_get_ontology_info` o leer fichero local)
- ¿Que clases o entidades considera indispensables?
- ¿Aspectos importantes sobre formato y nomenclaturas?
- ¿Instrucciones adicionales para la IA que generara la ontologia?

**Exploracion del dominio** (en paralelo con la interaccion si es posible):
- `stratio_list_domain_tables(domain)` + `stratio_get_tables_details(domain, tables)` → entender tablas y su contexto
- `stratio_get_table_columns_details(domain, table)` para tablas clave → datos disponibles para data properties
- `stratio_search_domain_knowledge(question, domain)` → terminologia existente

**Proponer plan**:
1. Proponer nombre de ontologia (sin espacios → guiones bajos, sin caracteres especiales)
2. Proponer **plan en Markdown** con:
   - Clases propuestas con descripcion
   - Data properties por clase
   - Relaciones entre clases
   - Tablas fuente de cada clase
3. Presentar plan al usuario para revision
4. Iterar hasta aprobacion (max 3 iteraciones de refinamiento)

### 4. Ejecucion

Segun decision del paso 2:
- **Nueva ontologia**: `stratio_create_ontology(domain, name, ontology_plan)` con el plan aprobado en Markdown
- **Ampliar existente**: `stratio_update_ontology(domain, name, update_plan)` — solo clases nuevas
- **Borrar clases**: Operacion DESTRUCTIVA — confirmar con el usuario listando las clases a borrar y advirtiendo que las vistas de negocio dependientes se refrescaran. Ejecutar `stratio_delete_ontology_classes(ontology_name, class_names)`. Informar del resultado: clases borradas (`deleted`) y clases saltadas por tener vistas Published (`skipped_locked`)

### 5. Verificacion

Ejecutar `stratio_get_ontology_info(name)` para confirmar la estructura creada. Presentar al usuario:
- Clases generadas con sus data properties
- Relaciones establecidas
- Diferencias respecto al plan (si las hay)

Ofrecer proactivamente: "Si tras revisarla quieres eliminar alguna clase, puedo hacerlo (las clases con vistas Published no se pueden borrar)." No bloqueante — el usuario decide si continuar o borrar algo.

### 6. Resumen

- Ontologia creada/ampliada con nombre y numero de clases
- Clases generadas vs planificadas
- Advertencias o problemas encontrados
- Siguiente paso sugerido: "Puedes crear las vistas de negocio con `/create-business-views`"
