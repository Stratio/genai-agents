---
name: create-semantic-terms
description: "Generar o regenerar semantic terms para las vistas de negocio de un dominio en Stratio Governance. Usar cuando el usuario quiera refrescar los semantic terms de las vistas de un dominio tras cambios en la ontología o las vistas, o poblarlos masivamente para un nuevo dominio. Para business terms en el diccionario, preferir manage-business-terms; para crear las vistas en sí, preferir create-business-views."
argument-hint: "[dominio técnico (opcional)]"
---

# Skill: Crear Términos Semánticos

Genera o regenera términos semánticos de negocio en el glosario de Stratio Governance para las vistas de negocio de un dominio. Fase 5 del pipeline de capa semántica.

## Tools MCP utilizadas

| Tool | Servidor | Propósito |
|------|----------|-----------|
| `search_domains(search_text, domain_type='technical')` | sql | **Preferir**. Buscar dominios técnicos por texto libre. Resultados por relevancia |
| `list_domains(domain_type='technical', refresh?)` | sql | Listar todos los dominios técnicos. `refresh=true` para bypass de cache |
| `list_technical_domain_concepts(domain)` | gov | Listar vistas con estado de gobernanza, términos semánticos y mappings |
| `create_semantic_terms(domain, view_names?, user_instructions?, regenerate?)` | gov | Crear términos semánticos. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |

**Reglas clave**: `domain_name` inmutable. Confirmación obligatoria para `regenerate=true`. Construir `user_instructions` mediante el Workflow de Enriquecimiento con Instrucciones del Glosario (`guides/stratio-semantic-layer-tools.md` §11) antes de invocar. Pre-requisito: las vistas deben tener SQL mapping antes de generar términos semánticos.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene nombre de dominio, buscar con `search_domains($ARGUMENTS, domain_type='technical')`. Si no coincide, reintentar con `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` por si es una colección recién creada. Si ahora coincide, continuar. Si no coincide o no hay argumento, listar con `list_domains(domain_type='technical')` y preguntar al usuario siguiendo la convención de preguntas al usuario.

### 2. Evaluar estado

Ejecutar `list_technical_domain_concepts(domain)` para obtener el listado de vistas con su estado de gobernanza, mappings y términos semánticos.

Presentar resumen:
```
## Términos Semánticos — [domain_name]
| Vista | Estado | Mapping | Términos semánticos |
|-------|--------|---------|---------------------|
| Vista1 | Draft | ✓ | ✓ |
| Vista2 | Pending Publish | ✓ | ✗ |
| Vista3 | Draft | ✗ | — |
```

### 3. Verificar pre-requisito

Las vistas necesitan SQL mapping para poder generar términos semánticos. Si hay vistas sin mapping:
- Advertir al usuario: "Las siguientes vistas no tienen mapping SQL: [lista]. No se pueden generar términos semánticos para ellas."
- Sugerir: "Usa `/create-sql-mappings` o `/create-business-views` para generar los mappings primero"
- Continuar solo con las vistas que tienen mapping

### 4. Selección de alcance

Preguntar al usuario con opciones (solo vistas con mapping):
1. **Crear para vistas sin términos** — idempotente
2. **Vistas específicas** — selección múltiple
3. **Regenerar todas** — DESTRUCTIVO: borra términos existentes y recrea. Requiere confirmación explícita
4. **Regenerar vistas específicas** — DESTRUCTIVO para las seleccionadas. Requiere confirmación

### 5. Enriquecimiento con instrucciones del glosario

Antes de invocar la tool MCP, aplicar el Workflow de Enriquecimiento con Instrucciones del Glosario descrito en `guides/stratio-semantic-layer-tools.md` §11, acotado a **semantic terms** (al llamar a `get_glossary_instructions`, pedir solo la fase de semantic terms). Aquí es donde el usuario puede traerse las instrucciones GenAI de semantic terms desde el diccionario de datos, aportar un fichero externo (glosario de negocio, documentación funcional, guía de estilo terminológico) como su fuente, superponer definiciones en texto libre, o saltar el enriquecimiento por completo.

Si el orquestador ya pre-cargó instrucciones enriquecidas para esta fase durante el flujo de `build-semantic-layer`, reutilizarlas — opcionalmente preguntar al usuario si quiere añadir algo específico para esta fase encima de lo que ya se cargó.

El texto enriquecido se usa como argumento `user_instructions` en la llamada MCP del paso siguiente. Si el usuario eligió la opción 4 (saltar), se omite `user_instructions`.

### 6. Ejecución

Invocar `create_semantic_terms`. Para regenerar: pasar `regenerate=true` (DESTRUCTIVO). La tool devuelve un resumen de lo procesado — presentar al usuario directamente.

Si hay errores, reintentar la vista fallida con `user_instructions` mejoradas (max 2 reintentos). Si persiste, documentar y continuar.

### 7. Resumen

Basado en la respuesta de la tool:
- Términos creados/regenerados
- Errores si los hubo
- Siguiente paso sugerido: "La capa semántica está lista para revisión. Si las vistas aún están en estado Draft, puedes enviarlas a Pending Publish pidiendo publicarlas directamente. Puedes crear business terms con `/manage-business-terms` para enriquecer el diccionario"
