---
name: create-business-views
description: Crear, regenerar o borrar vistas de negocio y SQL mappings en Stratio
  Governance a partir de una ontologia.
argument-hint: [dominio tecnico (opcional)]
---

# Skill: Crear Vistas de Negocio

Crea o regenera vistas de negocio y SQL mappings en Stratio Governance a partir de una ontologia existente. Fase 3 del pipeline de capa semantica.

## Tools MCP utilizadas

| Tool | Servidor | Proposito |
|------|----------|-----------|
| `stratio_list_technical_domains` | sql | Descubrir dominios tecnicos disponibles |
| `stratio_list_ontologies()` | gov | Listar ontologias existentes |
| `stratio_get_ontology_info(name)` | gov | Clases de la ontologia |
| `stratio_list_technical_domain_concepts(domain)` | gov | Vistas existentes con estado de mappings y terminos semanticos |
| `stratio_create_business_views(domain, ontology, class_names?, regenerate?)` | gov | Crear vistas + mappings. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| `stratio_delete_business_views(domain, view_names)` | gov | DESTRUCTIVO: borrar vistas especificas sin recrear (protegido por Published) |

**Reglas clave**: `domain_name` inmutable. Confirmacion obligatoria para `regenerate=true` y `delete`. `user_instructions` pendiente de implementar por el equipo de desarrollo — el agente ya lo contempla para cuando este disponible.

## Workflow

### 1. Determinar dominio y ontologia

**Dominio**: Si `$ARGUMENTS` contiene nombre, validar contra `stratio_list_technical_domains`. Si no, listar y preguntar al usuario siguiendo la convencion de preguntas al usuario.

**Ontologia**: Ejecutar `stratio_list_ontologies()`. Si hay varias, preguntar al usuario cual usar. Si solo hay una relevante para el dominio, confirmar.

### 2. Evaluar estado

Ejecutar en paralelo:
- `stratio_get_ontology_info(ontology)` → clases disponibles en la ontologia
- `stratio_list_technical_domain_concepts(domain)` → vistas ya creadas con su estado

Presentar resumen:
```
## Estado — [domain_name] + [ontologia]
| Clase | Vista | Mapping | Terminos semanticos |
|-------|-------|---------|---------------------|
| Clase1 | ✓ | ✓ | ✗ |
| Clase2 | ✗ | — | — |
| Clase3 | ✓ | ✗ | ✗ |
```

### 3. Seleccion de operacion

Preguntar al usuario con opciones:
1. **Crear vistas para clases sin vista** — idempotente: `stratio_create_business_views` salta las existentes
2. **Crear para clases especificas** — seleccion multiple de las clases sin vista
3. **Regenerar todas** — DESTRUCTIVO: borra y recrea vistas + mappings. Requiere confirmacion explicita con advertencia de que los terminos semanticos asociados tambien se pierden
4. **Regenerar clases especificas** — DESTRUCTIVO para las seleccionadas. Requiere confirmacion
5. **Borrar vistas especificas** — DESTRUCTIVO: elimina vistas seleccionadas sin recrearlas (diferente de regenerar). Seleccion multiple. Vistas con estado Published se saltan automaticamente. Requiere confirmacion

### 4. Ejecucion

Invocar `stratio_create_business_views` (con `regenerate=true` para opciones 3-4) o `stratio_delete_business_views` (opcion 5). Para `delete`: confirmar con el usuario listando las vistas a borrar. La tool devuelve `deleted` (borradas) y `skipped_published` (saltadas por Published) — presentar ambas listas al usuario.

Si hay errores, reintentar la entidad fallida (max 2 reintentos). Si persiste, documentar y continuar.

### 5. Resumen

Basado en la respuesta de la tool:
- Vistas creadas/regeneradas/borradas
- Mappings generados
- Errores si los hubo

Ofrecer proactivamente: "Si alguna vista no te convence, puedo eliminarla (las vistas Published no se pueden borrar)." No bloqueante — el usuario decide.

- Siguiente paso sugerido: "Puedes verificar o actualizar los mappings SQL con `/create-sql-mappings`, o generar terminos semanticos con `/create-semantic-terms`"
