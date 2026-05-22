---
name: create-ontology
description: "Crear, ampliar o borrar clases de una ontología en Stratio Governance, con planificación interactiva a partir de ficheros de referencia (.owl/.ttl, CSVs, documentos de negocio) antes de crear. Usar cuando el usuario quiera modelar la ontología de un dominio, añadir clases a una ya existente, sembrar clases desde documentos de referencia, o eliminar clases obsoletas. Para generar las vistas de negocio a partir de la ontología, preferir create-business-views."
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
| `create_ontology(domain, name, ontology_plan, best_effort?)` | gov | Crear ontología nueva con plan en Markdown. Argumento opcional `best_effort` (bool, off por defecto): entregar el último resultado intentado con warnings si los supervisores siguen rechazando tras todos los reintentos + reconstrucciones del plan. Ver `guides/stratio-semantic-layer-tools.md` §2 y §7.2 |
| `update_ontology(domain, name, update_plan, best_effort?)` | gov | Añadir clases nuevas a ontología existente. Argumento opcional `best_effort` (bool, off por defecto): misma semántica que `create_ontology`. ADD-only — las clases añadidas en modo best-effort solo se pueden eliminar con `delete_ontology_classes` |
| `delete_ontology(ontology_name)` | gov | DESTRUCTIVO: borrar la ontología entera con todas sus clases (protegido por Published). Útil en el flujo de recuperación tras best-effort (ver workflow §4.b) o para deshacerse de ontologías obsoletas |
| `delete_ontology_classes(ontology_name, class_names)` | gov | DESTRUCTIVO: borrar clases específicas (protegido por Published). Preferido cuando solo unas pocas clases —añadidas en best-effort u otras— necesitan ser eliminadas sin tocar el resto de la ontología |

**Reglas clave**: `domain_name` inmutable. Ontologías son ADD+DELETE: `update_ontology` añade clases; `delete_ontology_classes` borra clases específicas; `delete_ontology` borra la ontología entera (protegido: clases con vistas Published dependientes se saltan; las ontologías publicadas no se pueden eliminar). No se pueden modificar clases existentes. Nomenclatura: sin espacios (→ guiones bajos), sin caracteres especiales. Construir el contexto de planificación mediante el Workflow de Enriquecimiento con Instrucciones del Glosario (`guides/stratio-semantic-layer-tools.md` §11) antes de proponer el plan de ontología. La entrega best-effort mediante el argumento opcional `best_effort` es **opt-in** y solo afecta a cómo se gestionan los rechazos de calidad durante la generación de clases/vistas; no anula los fallos previos a la generación (plan no alcanzable con las tablas disponibles, se exceden los topes de tablas/tamaño, servicios de governance no disponibles) — esos siguen provocando el fallo de la llamada.

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
- ¿Tiene una ontología existente para tomar como referencia? (si sí → `get_ontology_info` o leer fichero local)
- ¿Qué clases o entidades considera indispensables?
- ¿Aspectos importantes sobre formato y nomenclaturas?

**Enriquecimiento con instrucciones del glosario**:

Antes de proponer el plan, aplicar el Workflow de Enriquecimiento con Instrucciones del Glosario descrito en `guides/stratio-semantic-layer-tools.md` §11, acotado a **ontology** (al llamar a `get_glossary_instructions`, pedir solo la fase de ontology). Aquí es donde el usuario puede traerse las instrucciones GenAI de ontología desde el diccionario de datos, aportar un fichero externo (.owl/.ttl, documento de negocio, CSV) como su fuente, superponer comentarios libres, o saltar el enriquecimiento por completo.

Si el orquestador ya pre-cargó instrucciones enriquecidas para esta fase durante el flujo de `build-semantic-layer`, reutilizarlas — opcionalmente preguntar si el usuario quiere añadir algo específico para esta fase.

El texto enriquecido pasa a formar parte del contexto de planificación que alimenta el plan en Markdown propuesto más abajo. Cuando el MCP subyacente acepte `user_instructions` para `create_ontology` / `update_ontology`, ese mismo texto se pasará también a la llamada.

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

#### 4.a Invocación nominal

Según decisión del paso 2:
- **Nueva ontología**: `create_ontology(domain, name, ontology_plan)` con el plan aprobado en Markdown
- **Ampliar existente**: `update_ontology(domain, name, update_plan)` — solo clases nuevas
- **Borrar clases específicas**: Operación DESTRUCTIVA — confirmar con el usuario listando las clases a borrar y advirtiendo que las vistas de negocio dependientes se refrescarán. Ejecutar `delete_ontology_classes(ontology_name, class_names)`. Informar del resultado: clases borradas (`deleted`) y clases saltadas por tener vistas Published (`skipped_locked`)
- **Borrar la ontología entera**: Operación DESTRUCTIVA — confirmar con el usuario que la ontología nombrada y **todas sus clases** serán eliminadas. Ejecutar `delete_ontology(ontology_name)`. Informar de si el borrado tuvo éxito o si fue bloqueado porque la ontología está en un estado no-borrable

#### 4.b Flujo de recuperación si `create_ontology` / `update_ontology` devuelve error

**Distinción importante**: si la respuesta de fallo indica que la chain se detuvo **antes de generar ninguna clase** (formulaciones típicas: el plan no es alcanzable con las tablas disponibles, faltan tablas necesarias, la petición excede los límites de tablas/tamaño, no se pudo validar el plan), la ontología **no** se persistió — basta con volver a llamar a `create_ontology` con un plan ajustado. El flujo siguiente aplica **solo** cuando la chain produjo o produjo parcialmente clases y la validación de calidad las siguió rechazando.

En ese caso, presentar al usuario las seis opciones siguientes y dejar que elija. **Confirmar explícitamente con el usuario antes de cualquier llamada a `delete_ontology` (opciones A, D, E)** — la anotación destructive-hint del MCP es informativa, no enforcement.

| Opción | Pasos | Cuándo elegirla |
|---|---|---|
| **A — Limpia y reintenta con best-effort** | `delete_ontology(name)` → `create_ontology(name, plan, best_effort=True)` | El plan parece correcto; el usuario acepta una ontología subóptima con warnings en vez de más reintentos |
| **B — Completa lo que falta vía update con best-effort** | `update_ontology(name, update_plan_para_lo_que_falla, best_effort=True)` | La base se creó; faltan clases/vistas; el usuario acepta clases nuevas subóptimas |
| **C — Completa lo que falta vía update en modo estricto** | `update_ontology(name, update_plan_corregido)` (sin `best_effort`) | La base está bien; el usuario ajusta el plan de update para pasar la validación |
| **D — Limpia y reintenta con un plan corregido** | `delete_ontology(name)` → `create_ontology(name, plan_corregido)` (sin `best_effort`) | Problemas estructurales en el plan original; reseteo y reintento en modo estricto |
| **E — Solo limpia** | `delete_ontology(name)` (sin recrear) | El usuario quiere borrar el intento fallido y detenerse aquí |
| **F — Dejarlo como está y revisar/corregir manualmente en la UI de Governance** | (sin llamada a tool) | El usuario acepta la ontología parcial y la refinará manualmente |

Heurística de sugerencia (la decisión final siempre es del usuario):

- Solo unas clases concretas fallaron y el resto está sano → sugerir C (más barato, no destructivo).
- Problemas transversales o de estructura base → sugerir D.
- El plan parece bien pero la validación insistente impide terminar → sugerir A.

Tras ejecutar la opción elegida, volver al **paso 5 (Verificación)** para confirmar el estado resultante.

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
