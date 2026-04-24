---
name: build-semantic-layer
description: "Construir la capa semántica completa de un dominio técnico end-to-end en Stratio Governance, orquestando las cinco fases del pipeline (technical terms → ontology → business views → SQL mappings → semantic terms), con publicación opcional de vistas entre mappings y semantic terms. Requiere una data collection existente — usa create-data-collection primero si no existe. Usar cuando el usuario quiera construir, completar, regenerar o auditar la capa semántica completa de un dominio, en lugar de invocar una skill de fase concreta."
argument-hint: "[dominio técnico (opcional)]"
---

# Skill: Construir Capa Semántica (Pipeline Completo)

Orquesta las 5 fases del pipeline de construcción de la capa semántica de un dominio técnico existente. Diagnostica el estado actual, propone un plan de ejecución, ejecuta cada fase en secuencia y ofrece publicar las vistas tras completar los mappings.

**Importante**: Esta skill llama a las tools MCP directamente (inline). NO delega a otras skills — las skills no pueden invocar otras skills programáticamente. Las shared skills de cada fase existen para uso independiente por el usuario; el pipeline las replica de forma integrada.

Para referencia completa de tools y reglas, ver `skills-guides/stratio-semantic-layer-tools.md`.

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

### 3. Contexto general

Pedir al usuario contexto global que aplique a todas las fases:
- "¿Tienes ficheros de referencia (documentación, glosarios, especificaciones) que deba leer para entender mejor el dominio? ¿Hay definiciones de negocio, reglas o conceptos clave que quieras que se reflejen en la capa semántica? Si no, responde 'Continuar'."
- Si el usuario proporciona rutas a ficheros → **leerlos** y extraer información relevante como contexto global
- El contexto extraido se pasara como `user_instructions` en cada fase que lo soporte
- Solo preguntar de nuevo en fases específicas si el usuario necesita instrucciones diferentes

### 4. Plan de ejecución

Basado en el diagnóstico, listar las fases que necesitan trabajo:
- Indicar que fases están completas (ofrecer saltar o forzar regeneracion)
- Indicar que fases están pendientes o parciales
- Advertir dependencias entre fases (ej: "Las vistas requieren ontología")

Pedir aprobación global del plan antes de ejecutar.

### 5. Ejecución secuencial

Ejecutar cada fase en orden estricto, llamando a las tools directamente:

**Fase 1 — Términos técnicos** (si necesario):
- `create_technical_terms(domain, table_names?, user_instructions?)` con las instrucciones globales
- Presentar resumen de la tool al usuario

**Fase 2 — Ontología** (si necesario):
- Planificación interactiva: preguntar al usuario sobre clases, ficheros de referencia (ontologías .owl/.ttl, documentos de negocio, CSVs), nomenclaturas
- Si el usuario proporciona rutas a ficheros locales → **leerlos** para extraer contexto y enriquecer el plan
- Explorar dominio: `list_domain_tables` + `get_tables_details` + `get_table_columns_details`
- Proponer plan de ontología en Markdown → revisar con usuario → iterar (max 3)
- `create_ontology(domain, name, ontology_plan)` o `update_ontology(domain, name, update_plan)`
- Verificar: `get_ontology_info(name)` — presentar estructura y ofrecer: "Si quieres eliminar alguna clase antes de continuar, puedo hacerlo (clases con vistas Published no se pueden borrar)." Si el usuario pide borrar → `delete_ontology_classes(ontology_name, class_names)` → informar de borradas/saltadas → volver a verificar

**Fase 3 — Vistas de negocio** (si necesario):
- `create_business_views(domain, ontology, class_names?)` con la ontología del paso anterior
- Presentar resumen de la tool al usuario
- Ofrecer: "Si alguna vista no te convence, puedo eliminarla antes de continuar con mappings (vistas Published no se pueden borrar)." Si el usuario pide borrar → `delete_business_views(domain, view_names)` → informar de borradas/saltadas

**Fase 4 — SQL Mappings** (si necesario; cubre vistas nuevas de Fase 3 y existentes sin mapping):
- `create_sql_mappings(domain, view_names?, user_instructions?)` con las instrucciones globales
- Presentar resumen de la tool al usuario

**Publicación (opcional, entre Fase 4 y Fase 5)**:
- Las vistas de negocio y sus mappings están completos. Preguntar al usuario: "¿Quieres publicar las vistas ahora (Pending Publish) o continuar primero con los términos semánticos?"
- **Si publica**: Ejecutar `publish_business_views(domain)` → presentar resultado: vistas publicadas + fallidas (transicion no permitida) + no encontradas → continuar con Fase 5
- **Si no publica**: Pasar directamente a Fase 5. Recordar en el resumen final que las vistas siguen en Draft

**Fase 5 — Términos semánticos** (si necesario):
- Verificar que las vistas tienen mapping (pre-requisito)
- `create_semantic_terms(domain, view_names?, user_instructions?)` con las instrucciones globales
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
