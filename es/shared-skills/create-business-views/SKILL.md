---
name: create-business-views
description: Crear, regenerar, borrar o publicar vistas de negocio y SQL mappings en
  Stratio Governance a partir de una ontologia.
argument-hint: [dominio tecnico (opcional)]
---

# Skill: Crear Vistas de Negocio

Crea, regenera o borra vistas de negocio y SQL mappings en Stratio Governance a partir de una ontologia existente. Ofrece publicar las vistas tras crearlas o regenerarlas. Fase 3 del pipeline de capa semantica.

## Tools MCP utilizadas

| Tool | Servidor | Proposito |
|------|----------|-----------|
| `search_domains(search_text, domain_type='technical')` | sql | **Preferir**. Buscar dominios tecnicos por texto libre. Resultados por relevancia |
| `list_domains(domain_type='technical', refresh?)` | sql | Listar todos los dominios tecnicos. `refresh=true` para bypass de cache |
| `search_ontologies(search_text)` | gov | Buscar ontologias por texto libre. Resultados por relevancia |
| `list_ontologies()` | gov | Listar todas las ontologias existentes |
| `get_ontology_info(name)` | gov | Clases de la ontologia |
| `list_technical_domain_concepts(domain)` | gov | Vistas existentes con estado de gobernanza, mappings y terminos semanticos |
| `create_business_views(domain, ontology, class_names?, regenerate?)` | gov | Crear vistas + mappings. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| `delete_business_views(domain, view_names)` | gov | DESTRUCTIVO: borrar vistas especificas sin recrear (protegido por Published) |
| `publish_business_views(domain, view_names?)` | gov | Publicar vistas (Draft → Pending Publish). Sin `view_names`, publica todas |

**Reglas clave**: `domain_name` inmutable. Confirmacion obligatoria para `regenerate=true` y `delete`. `user_instructions` pendiente de implementar por el equipo de desarrollo — el agente ya lo contempla para cuando este disponible.

## Workflow

### 1. Determinar dominio y ontologia

**Dominio**: Si `$ARGUMENTS` contiene nombre, buscar con `search_domains($ARGUMENTS, domain_type='technical')`. Si no coincide, reintentar con `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` por si es una coleccion recien creada. Si ahora coincide, continuar. Si no coincide o no hay argumento, listar con `list_domains(domain_type='technical')` y preguntar al usuario siguiendo la convencion de preguntas al usuario.

**Ontologia**: Si el usuario o el contexto mencionan una ontologia concreta, buscar con `search_ontologies(pista)`. Si no, ejecutar `list_ontologies()` para ver todas. Si hay varias, preguntar al usuario cual usar. Si solo hay una relevante para el dominio, confirmar.

### 2. Evaluar estado

Ejecutar en paralelo:
- `get_ontology_info(ontology)` → clases disponibles en la ontologia
- `list_technical_domain_concepts(domain)` → vistas ya creadas con su estado

Presentar resumen:
```
## Estado — [domain_name] + [ontologia]
| Clase | Vista | Estado | Mapping | Terminos semanticos |
|-------|-------|--------|---------|---------------------|
| Clase1 | ✓ | Draft | ✓ | ✗ |
| Clase2 | ✗ | — | — | — |
| Clase3 | ✓ | Pending Publish | ✗ | ✗ |
```

### 3. Seleccion de operacion

Preguntar al usuario con opciones:
1. **Crear vistas para clases sin vista** — idempotente: `create_business_views` salta las existentes
2. **Crear para clases especificas** — seleccion multiple de las clases sin vista
3. **Regenerar todas** — DESTRUCTIVO: borra y recrea vistas + mappings. Requiere confirmacion explicita con advertencia de que los terminos semanticos asociados tambien se pierden
4. **Regenerar clases especificas** — DESTRUCTIVO para las seleccionadas. Requiere confirmacion
5. **Borrar vistas especificas** — DESTRUCTIVO: elimina vistas seleccionadas sin recrearlas (diferente de regenerar). Seleccion multiple. Vistas con estado Published se saltan automaticamente. Requiere confirmacion

### 4. Ejecucion

Invocar `create_business_views` (con `regenerate=true` para opciones 3-4) o `delete_business_views` (opcion 5). Para `delete`: confirmar con el usuario listando las vistas a borrar. La tool devuelve `deleted` (borradas) y `skipped_published` (saltadas por Published) — presentar ambas listas al usuario.

Si hay errores, reintentar la entidad fallida (max 2 reintentos). Si persiste, documentar y continuar.

### 5. Resumen

Basado en la respuesta de la tool:
- Vistas creadas/regeneradas/borradas
- Mappings generados
- Errores si los hubo

Ofrecer proactivamente: "Si alguna vista no te convence, puedo eliminarla (las vistas Published no se pueden borrar)." No bloqueante — el usuario decide.

### 6. Publicacion (opcional)

Si se crearon o regeneraron vistas (no aplica a borrado), ofrecer publicacion:
- "¿Quieres publicar las vistas creadas? Esto cambiara su estado a Pending Publish, listas para ser publicadas al virtualizador de datos."
- Si el usuario acepta → ejecutar `publish_business_views(domain, view_names)` con las vistas creadas → presentar resultado: vistas publicadas + fallidas (transicion no permitida) + no encontradas
- Si el usuario rechaza → continuar con la sugerencia de siguiente paso
- No bloqueante: el usuario decide

Siguiente paso sugerido: "Puedes verificar o actualizar los mappings SQL con `/create-sql-mappings`, o generar terminos semanticos con `/create-semantic-terms`. Si no has publicado ahora, puedes hacerlo mas tarde"
