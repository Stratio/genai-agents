---
name: build-semantic-layer
description: "Construir la capa semántica completa de un dominio técnico end-to-end en Stratio Governance, orquestando las cinco fases del pipeline (technical terms → ontology → business views → SQL mappings → semantic terms), con publicación opcional de vistas entre mappings y semantic terms. Requiere una data collection existente — usa create-data-collection primero si no existe. Usar cuando el usuario quiera construir, completar, regenerar o auditar la capa semántica completa de un dominio, en lugar de invocar una skill de fase concreta."
argument-hint: "[dominio técnico (opcional)]"
---

# Skill: Construir Capa Semántica (Pipeline Completo)

Orquesta las 5 fases del pipeline de construcción de la capa semántica de un dominio técnico existente. Diagnostica el estado actual, propone un plan de ejecución, ejecuta cada fase en secuencia y ofrece publicar las vistas tras completar los mappings.

**Importante**: Esta skill llama a las tools MCP directamente (inline). NO delega a otras skills — las skills no pueden invocar otras skills programáticamente. Las shared skills de cada fase existen para uso independiente por el usuario; el pipeline las replica de forma integrada.

Para referencia completa de tools y reglas, ver `guides/stratio-semantic-layer-tools.md`.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene nombre de dominio, buscar con `search_domains($ARGUMENTS, domain_type='technical')`.

- Si coincide con un resultado → usarlo y continuar con el paso 2.
- Si NO coincide → reintentar inmediatamente con `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` para forzar bypass de cache (la colección puede ser recién creada). Si ahora aparece → usarlo y continuar con el paso 2. Si sigue sin aparecer → la colección puede estar aún propagandose internamente. Informar al usuario: "El dominio no aparece aún. Puede tardar 1-2 minutos en propagarse. Reintentando en 60 segundos...". Esperar 60 segundos y volver a ejecutar `search_domains($ARGUMENTS, domain_type='technical', refresh=true)`. Si ahora aparece → continuar. Si no → informar al usuario y pedirle que reintente más tarde.
- Si no hay argumento → ejecutar `list_domains(domain_type='technical')` y presentar la lista de dominios existentes al usuario para que seleccione uno, siguiendo la convención de preguntas al usuario.

Si el usuario elige un dominio → continuar con el paso 2.

### 2. Diagnóstico completo

Ejecutar en paralelo:
- `list_domains(domain_type='technical')` → verificar si el dominio tiene descripción general
- `list_domain_tables(domain)` → tablas con/sin descripciones (= términos técnicos)
- `list_ontologies` → ontologías existentes (o `search_ontologies(texto)` si se busca una concreta)
- `list_technical_domain_concepts(domain)` → vistas, mappings, términos semánticos

> **OBLIGATORIO — sin atajos por inferencia.** Las cuatro llamadas anteriores son requeridas. `list_domain_tables` y `list_technical_domain_concepts` son **fuentes de verdad independientes** y reportan fases distintas:
> - **Términos técnicos** viven en `list_domain_tables(domain)` y se infieren del campo `description` de cada tabla.
> - **Vistas de negocio, SQL mappings y términos semánticos** viven en `list_technical_domain_concepts(domain)` (`has_sql_mapping`, `has_semantic_terms`, estado de la vista).
>
> Los términos técnicos pueden existir (o faltar) **independientemente** de que haya vistas de negocio. NUNCA inferir su estado a partir de `business_views = 0` ni de que ninguna otra fase esté vacía. Si el usuario pide "esquemáticamente", "rápido" o "qué falta", el **formato** de la respuesta puede ser compacto, pero el **alcance de la verificación es innegociable** — ejecutar las cuatro llamadas antes de responder.

Para cada ontología relevante: `get_ontology_info(name)`.

Presentar **dashboard de estado**:
```
## Estado de la Capa Semántica — [domain_name]
| Fase | Estado | Detalle |
|------|--------|---------|
| Descripción dominio | ✓ / ✗ | Tiene/no tiene descripción |
| Términos técnicos | Parcial (15/20) | 5 tablas sin describir |
| Ontología | ✓ Completa | "mi_ontologia" — 8 clases |
| Vistas de negocio | Parcial (6/8) | 2 clases sin vista |
| SQL Mappings | Parcial (5/6) | 1 vista sin mapping |
| Publicación | ✗ Draft | 0/6 vistas publicadas |
| Términos semánticos | ✗ Pendiente | 0/6 vistas |
```

> **Modo diagnóstico-solo (salida temprana).** Si la pregunta del usuario indica intención diagnóstica — palabras clave o variantes próximas tipo "qué falta", "qué queda", "esquemáticamente" / "de manera esquemática" / "esquemática", "estado del pipeline", "diagnostica", "estado de la capa semántica", "por dónde vamos con X" — Y NO incluye verbos de construcción ("construye", "crea", "genera", "regenera") sobre el mismo alcance, presenta el dashboard de arriba, añade un follow-up de una línea tipo "¿Sobre qué fase quieres actuar? Puedo cargar una skill para términos técnicos, ontología, vistas de negocio, SQL mappings o términos semánticos" y **DETENTE**. NO continuar con el paso 3 (enriquecimiento del glosario) ni con ningún paso posterior. Si el usuario pide después una fase concreta, carga directamente la skill correspondiente (`/create-technical-terms`, `/create-ontology`, …) pasando el dominio; si pide construir el pipeline entero, reentra en esta skill con `/build-semantic-layer [dominio]`. Trata el matching de palabras clave **semánticamente**, no como subcadena literal — "dime esquemáticamente qué queda" y "qué falta de manera esquemática" cuentan ambos.

### 3. Enriquecimiento con instrucciones del glosario (pre-carga para todo el pipeline)

Aplicar el Workflow de Enriquecimiento con Instrucciones del Glosario descrito en `guides/stratio-semantic-layer-tools.md` §11 **una sola vez**, cubriendo las cuatro fases del pipeline que aceptan `user_instructions`: technical terms, ontology, SQL mappings y semantic terms.

Al hacer la pregunta de cuatro opciones (§11.2), plantearla como "para las fases de este pipeline" y tratar la respuesta como política para todas; ofrecer override por fase solo si el usuario lo pide explícitamente. Combinar las instrucciones del glosario con cualquier fichero de referencia que el usuario quiera aportar (opción 3) y cualquier regla o definición de negocio en texto libre que quiera superponer.

El resultado es **texto enriquecido por fase** que esta skill mantiene en el contexto de planificación durante el resto de la ejecución. Cada invocación de fase en el paso 5 reutiliza el bloque correspondiente como `user_instructions` sin volver a hacer la pregunta de cuatro opciones. Las fases que el usuario decida saltar en el paso 4 simplemente no consumen su bloque — sin problema.

Si el usuario eligió la opción 4 (saltar), no se produce `user_instructions` para ninguna fase y el pipeline corre sin enriquecimiento.

### 4. Plan de ejecución

Basado en el diagnóstico, listar las fases que necesitan trabajo:
- Indicar que fases están completas (ofrecer saltar o forzar regeneracion)
- Indicar que fases están pendientes o parciales
- Advertir dependencias entre fases (ej: "Las vistas requieren ontología")

Pedir aprobación global del plan antes de ejecutar.

### 5. Ejecución secuencial

Ejecutar cada fase en orden estricto, llamando a las tools directamente:

**Fase 1 — Términos técnicos** (si necesario):
- `create_technical_terms(domain, table_names?, user_instructions?)` pasando como `user_instructions` el bloque de technical terms del enriquecimiento pre-cargado (omitir el parámetro si el usuario eligió saltar el enriquecimiento en el paso 3)
- Presentar resumen de la tool al usuario

**Fase 2 — Ontología** (si necesario):
- Planificación interactiva: preguntar al usuario sobre clases esenciales y nomenclaturas
- El bloque de ontology del enriquecimiento pre-cargado ya cubre ficheros de referencia, instrucciones del glosario y reglas en texto libre — alimentarlo en el contexto de planificación. Solo volver a preguntar si el usuario quiere añadir explícitamente algo nuevo para esta fase
- Explorar dominio: `list_domain_tables` + `get_tables_details` + `get_table_columns_details`
- Proponer plan de ontología en Markdown → revisar con usuario → iterar (max 3)
- `create_ontology(domain, name, ontology_plan)` o `update_ontology(domain, name, update_plan)`
- Verificar: `get_ontology_info(name)` — presentar estructura y ofrecer: "Si quieres eliminar alguna clase antes de continuar, puedo hacerlo (clases con vistas Published no se pueden borrar)." Si el usuario pide borrar → `delete_ontology_classes(ontology_name, class_names)` → informar de borradas/saltadas → volver a verificar

**Fase 3 — Vistas de negocio** (si necesario):
- `create_business_views(domain, ontology, class_names?)` con la ontología del paso anterior
- Presentar resumen de la tool al usuario
- Ofrecer: "Si alguna vista no te convence, puedo eliminarla antes de continuar con mappings (vistas Published no se pueden borrar)." Si el usuario pide borrar → `delete_business_views(domain, view_names)` → informar de borradas/saltadas

**Fase 4 — SQL Mappings** (si necesario; cubre vistas nuevas de Fase 3 y existentes sin mapping):
- `create_sql_mappings(domain, view_names?, user_instructions?)` pasando como `user_instructions` el bloque de mapping del enriquecimiento pre-cargado (omitir si se saltó en el paso 3)
- Presentar resumen de la tool al usuario
- La respuesta incluye `processed_views`: cada entrada lleva `sql_mapping` — la SQL del mapping recién generada. **Mantener esta lista en el contexto de orquestación**; el bloque opcional de validación pre-publicación de abajo la usa directamente (no hace falta volver a llamar a `list_technical_domain_concepts`)

**Validación opcional pre-publicación (mappings)**:
- Antes de preguntar por la publicación, ofrecer al usuario una validación con datos de muestra sobre los mappings recién creados: "¿Quieres que ejecute la SQL del mapping (LIMIT 5) de cada vista y te muestre los resultados antes de decidir sobre la publicación?"
- Usar la lista `processed_views` devuelta por la llamada a `create_sql_mappings` de la Fase 4 (cada entrada lleva la SQL recién generada en `sql_mapping`). Usar esa SQL tal cual, envolviéndola como `SELECT * FROM (<sql_mapping>) AS m LIMIT 5` para preservar la proyección original. No hace falta volver a llamar a `list_technical_domain_concepts` aquí.
- Si el usuario acepta, listar las vistas candidatas y **cap por defecto en 5 vistas**. Si `processed_views` tiene más, preguntar al usuario qué subconjunto validar.
- Para cada vista seleccionada: ejecutar `execute_sql` con la query envuelta. Lanzar todas las vistas seleccionadas **en paralelo** en la misma respuesta.
- Renderizar resultados como tablas Markdown siguiendo `guides/stratio-data-tools.md` §4 (cap por defecto de 10 filas en chat).
- **Sin improvisación**: si `sql_mapping` viene vacío para alguna vista dentro de `processed_views` (backend de gov no expone aún el campo, o el mapping no se persistió correctamente), NO improvisar un SELECT sobre las tablas fuente. Decirle al usuario: "No puedo validar la SQL de este mapping desde aquí porque el backend no la está exponiendo. Puedes validarla desde la UI de Governance, en la vista." Saltar esa vista y continuar con las demás.
- Si `execute_sql` no está disponible en este agente, no caer al fallback de `query_data` con lenguaje natural sobre las tablas fuente (no validaría el mapping). Informar al usuario y derivar a la UI de Governance.

**Publicación (opcional, entre Fase 4 y Fase 5)**:
- Las vistas de negocio y sus mappings están completos. Preguntar al usuario: "¿Quieres publicar las vistas ahora (Pending Publish) o continuar primero con los términos semánticos?"
- **Si publica**: Ejecutar `publish_business_views(domain)` → presentar resultado: vistas publicadas + fallidas (transicion no permitida) + no encontradas → continuar con Fase 5
- **Si no publica**: Pasar directamente a Fase 5. Recordar en el resumen final que las vistas siguen en Draft

**Fase 5 — Términos semánticos** (si necesario):
- Verificar que las vistas tienen mapping (pre-requisito)
- `create_semantic_terms(domain, view_names?, user_instructions?)` pasando como `user_instructions` el bloque de semantic terms del enriquecimiento pre-cargado (omitir si se saltó en el paso 3)
- Presentar resumen de la tool al usuario

**Tras cada fase**:
- Reportar progreso actualizado (mini-dashboard)
- Si falla: ofrecer opciones al usuario:
  - **Reintentar** con `user_instructions` mejoradas
  - **Saltar** esta fase (advertir dependencias: "Si saltas la ontología, no se pueden crear vistas")
  - **Abortar** el pipeline

### 6. Resumen final

Presentar dashboard actualizado con el estado final:
```
## Capa Semántica Completada — [domain_name]
| Fase | Estado | Acciones realizadas |
|------|--------|---------------------|
| Términos técnicos | ✓ | 20 tablas procesadas |
| Ontología | ✓ | "mi_ontologia" creada — 8 clases |
| Vistas de negocio | ✓ | 8 vistas creadas |
| SQL Mappings | ✓ | 8 mappings generados |
| Publicación | ✓ / ✗ | Pending Publish / Draft |
| Términos semánticos | ✓ | 8 vistas con términos |
```

Incluir:
- Acciones realizadas por fase
- Errores encontrados y como se resolvieron
- Sugerencias de siguientes pasos:
  - "Puedes crear business terms con `/manage-business-terms` para enriquecer el diccionario"
  - Si las vistas se publicaron durante el pipeline: "Las vistas están en estado Pending Publish, pendientes de ser publicadas al virtualizador de datos"
  - Si las vistas NO se publicaron: "Las vistas siguen en estado Draft. Puedes publicarlas pidiendolo directamente o desde la UI de Governance"
  - "Una vez publicada en el virtualizador, la capa semántica estará disponible como dominio `semantic_[nombre]`"

### 7. Validación opcional post-publicación (capa semántica)

Si las vistas se publicaron durante el pipeline (o ya estaban publicadas), ofrecer al usuario una verificación de la capa semántica en vivo:

- "El dominio semántico `semantic_[nombre]` ya está disponible. ¿Quieres que lance 1–3 preguntas de negocio sobre él para confirmar que las vistas y los términos responden como esperas?"
- **Latencias de propagación a tener en cuenta**:
  - **Tras `publish_business_views`**: las vistas suelen quedar consultables en ~60 segundos.
  - **Tras `create_semantic_terms`** (Fase 5): los términos semánticos suelen quedar consultables como parte de la capa en vivo en ~90 segundos — `query_data` puede no resolver aún una pregunta que dependa de un término semántico recién creado.
  - **Patrón**: si la primera llamada a `query_data` / `execute_sql` falla porque el dominio o el término no es visible aún, informar al usuario, esperar la ventana correspondiente (60s post-publish, 90s post-Fase-5) y reintentar una vez. Si sigue fallando, proponer continuar más tarde. Decirle explícitamente al usuario qué ventana de propagación se está respetando para que entienda la espera.
- Si el usuario acepta, pedirle 1–3 preguntas O proponérselas. **Patrón para preguntas propuestas** (determinístico, no libre): elegir la clase de la ontología con el mayor número de atributos mappeados y proponer: (a) `count(*)` de la vista correspondiente, (b) top-5 agrupando por un atributo categórico si existe, (c) min/max/avg sobre un atributo numérico si existe. Listar las propuestas como opciones numeradas antes de ejecutar.
- Resolver cada pregunta con `query_data` (preferido — usa la capa semántica gobernada con NL). Si el usuario quiere ver / ajustar la SQL generada antes de ejecutar, usar primero `generate_sql` y ofrecer `execute_sql` después.
- Renderizar resultados siguiendo `guides/stratio-data-tools.md` §4 (cap por defecto 10 filas).
- Si la validación arroja resultados inesperados (vacíos, tipos no coincidentes, términos semánticos no encontrados), reportarlo y sugerir siguientes pasos: `/create-semantic-terms` para refinar, o `/create-sql-mappings` para arreglar la SQL.
- Si el agente no tiene tools de datos (`query_data`, `execute_sql`, `generate_sql`), derivar al usuario a la UI de Governance / al agente de data-analytics y saltar este paso.
