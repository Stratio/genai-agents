---
name: create-business-views
description: "Crear, regenerar, borrar o publicar vistas de negocio y sus SQL mappings en Stratio Governance a partir de una ontología existente. Usar cuando el usuario quiera generar vistas de negocio desde la ontología, reconstruirlas tras cambios en la ontología, eliminar vistas obsoletas o publicar vistas pendientes. Para ajustes de SQL sin recrear la vista, preferir create-sql-mappings."
argument-hint: "[dominio técnico (opcional)]"
---

# Skill: Crear Vistas de Negocio

Crea, regenera o borra vistas de negocio y SQL mappings en Stratio Governance a partir de una ontología existente. Ofrece publicar las vistas tras crearlas o regenerarlas. Fase 3 del pipeline de capa semántica.

## Tools MCP utilizadas

| Tool | Servidor | Propósito |
|------|----------|-----------|
| `search_domains(search_text, domain_type='technical')` | sql | **Preferir**. Buscar dominios técnicos por texto libre. Resultados por relevancia |
| `list_domains(domain_type='technical', refresh?)` | sql | Listar todos los dominios técnicos. `refresh=true` para bypass de cache |
| `search_ontologies(search_text)` | gov | Buscar ontologías por texto libre. Resultados por relevancia |
| `list_ontologies()` | gov | Listar todas las ontologías existentes |
| `get_ontology_info(name)` | gov | Clases de la ontología |
| `list_technical_domain_concepts(domain)` | gov | Vistas existentes con estado de gobernanza, mappings y términos semánticos |
| `create_business_views(domain, ontology, class_names?, regenerate?)` | gov | Crear vistas + mappings. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| `delete_business_views(domain, view_names)` | gov | DESTRUCTIVO: borrar vistas específicas sin recrear (protegido por Published) |
| `publish_business_views(domain, view_names?)` | gov | Publicar vistas (Draft → Pending Publish). Sin `view_names`, publica todas |

**Reglas clave**: `domain_name` inmutable. Confirmación obligatoria para `regenerate=true` y `delete`. `user_instructions` pendiente de implementar por el equipo de desarrollo — el agente ya lo contempla para cuando esté disponible.

## Workflow

### 1. Determinar dominio y ontología

**Dominio**: Si `$ARGUMENTS` contiene nombre, buscar con `search_domains($ARGUMENTS, domain_type='technical')`. Si no coincide, reintentar con `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` por si es una colección recién creada. Si ahora coincide, continuar. Si no coincide o no hay argumento, listar con `list_domains(domain_type='technical')` y preguntar al usuario siguiendo la convención de preguntas al usuario.

**Ontología**: Si el usuario o el contexto mencionan una ontología concreta, buscar con `search_ontologies(pista)`. Si no, ejecutar `list_ontologies()` para ver todas. Si hay varias, preguntar al usuario cual usar. Si solo hay una relevante para el dominio, confirmar.

### 2. Evaluar estado

Ejecutar en paralelo:
- `get_ontology_info(ontology)` → clases disponibles en la ontología
- `list_technical_domain_concepts(domain)` → vistas ya creadas con su estado

Presentar resumen:
```
## Estado — [domain_name] + [ontología]
| Clase | Vista | Estado | Mapping | Términos semánticos |
|-------|-------|--------|---------|---------------------|
| Clase1 | ✓ | Draft | ✓ | ✗ |
| Clase2 | ✗ | — | — | — |
| Clase3 | ✓ | Pending Publish | ✗ | ✗ |
```

### 3. Selección de operación

Preguntar al usuario con opciones:
1. **Crear vistas para clases sin vista** — idempotente: `create_business_views` salta las existentes
2. **Crear para clases específicas** — selección múltiple de las clases sin vista
3. **Regenerar todas** — DESTRUCTIVO: borra y recrea vistas + mappings. Requiere confirmación explícita con advertencia de que los términos semánticos asociados también se pierden
4. **Regenerar clases específicas** — DESTRUCTIVO para las seleccionadas. Requiere confirmación
5. **Borrar vistas específicas** — DESTRUCTIVO: elimina vistas seleccionadas sin recrearlas (diferente de regenerar). Selección múltiple. Vistas con estado Published se saltan automáticamente. Requiere confirmación

### 4. Ejecución

Invocar `create_business_views` (con `regenerate=true` para opciones 3-4) o `delete_business_views` (opción 5). Para `delete`: confirmar con el usuario listando las vistas a borrar. La tool devuelve `deleted` (borradas) y `skipped_published` (saltadas por Published) — presentar ambas listas al usuario.

Si hay errores, reintentar la entidad fallida (max 2 reintentos). Si persiste, documentar y continuar.

### 5. Resumen

Basado en la respuesta de la tool:
- Vistas creadas/regeneradas/borradas
- Mappings generados
- Errores si los hubo

Ofrecer proactivamente: "Si alguna vista no te convence, puedo eliminarla (las vistas Published no se pueden borrar)." No bloqueante — el usuario decide.

### 6. Publicación (opcional)

Si se crearon o regeneraron vistas (no aplica a borrado), ofrecer publicación:
- "¿Quieres publicar las vistas creadas? Esto cambiara su estado a Pending Publish, listas para ser publicadas al virtualizador de datos."
- Si el usuario acepta → ejecutar `publish_business_views(domain, view_names)` con las vistas creadas → presentar resultado: vistas publicadas + fallidas (transicion no permitida) + no encontradas
- Si el usuario rechaza → continuar con la sugerencia de siguiente paso
- No bloqueante: el usuario decide

Siguiente paso sugerido: "Puedes verificar o actualizar los mappings SQL con `/create-sql-mappings`, o generar términos semánticos con `/create-semantic-terms`. Si no has publicado ahora, puedes hacerlo más tarde"
