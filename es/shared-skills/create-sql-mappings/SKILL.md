---
name: create-sql-mappings
description: Crear o actualizar SQL mappings para vistas de negocio existentes en Stratio
  Governance. Para corregir, mejorar o crear mappings sin recrear vistas.
argument-hint: [dominio técnico (opcional)]
---

# Skill: Crear SQL Mappings

Crea o actualiza SQL mappings para vistas de negocio existentes en Stratio Governance. Fase 4 del pipeline de capa semántica. Útil para corregir o mejorar mappings sin necesidad de recrear las vistas.

## Tools MCP utilizadas

| Tool | Servidor | Propósito |
|------|----------|-----------|
| `search_domains(search_text, domain_type='technical')` | sql | **Preferir**. Buscar dominios técnicos por texto libre. Resultados por relevancia |
| `list_domains(domain_type='technical', refresh?)` | sql | Listar todos los dominios técnicos. `refresh=true` para bypass de cache |
| `list_technical_domain_concepts(domain)` | gov | Listar vistas con estado de gobernanza y mapping |
| `create_sql_mappings(domain, view_names?, user_instructions?)` | gov | Crear o actualizar mappings SQL de vistas existentes |
| `publish_business_views(domain, view_names?)` | gov | Publicar vistas (Draft → Pending Publish). Sin `view_names`, publica todas |

**Reglas clave**: `domain_name` inmutable. Ofrecer `user_instructions` antes de invocar. `create_sql_mappings` sobrescribe mappings existentes (no es destructivo a nivel de vista, solo reemplaza el mapping SQL).

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene nombre de dominio, buscar con `search_domains($ARGUMENTS, domain_type='technical')`. Si no coincide, reintentar con `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` por si es una colección recién creada. Si ahora coincide, continuar. Si no coincide o no hay argumento, listar con `list_domains(domain_type='technical')` y preguntar al usuario siguiendo la convención de preguntas al usuario.

### 2. Evaluar estado

Ejecutar `list_technical_domain_concepts(domain)` para obtener el listado de vistas con su estado de gobernanza y mapping.

Presentar resumen:
```
## Mappings SQL — [domain_name]
| Vista | Estado | Mapping |
|-------|--------|---------|
| Vista1 | Draft | ✓ |
| Vista2 | Draft | ✗ |
| Vista3 | Pending Publish | ✓ |
```

### 3. Selección de vistas

Preguntar al usuario con opciones:
1. **Todas las vistas sin mapping** — seguro, solo crea donde falta
2. **Vistas específicas** — selección múltiple (puede incluir vistas con mapping existente para actualizarlo)
3. **Actualizar mappings existentes** — sobrescribe el mapping SQL, no borra la vista ni sus términos semánticos

### 4. user_instructions

Ofrecer al usuario la oportunidad de aportar contexto adicional:
- **Ficheros locales**: Si el usuario tiene documentación técnica, diagramas ER, especificaciones de integracion o scripts SQL de referencia → **leerlos** y extraer información relevante para incluirla como contexto
- **Reglas de mapping**: Relaciones entre tablas, tipo de JOINs preferidos, filtros de exclusion, transformaciones de datos
- Ejemplos: "Usa LEFT JOIN para preservar registros sin correspondencia", "Tabla principal para los JOINs: accounts", "Excluir registros con estado='DELETED'", "Usar COALESCE para campos nullable", "Fechas en formato epoch milliseconds"

No sugerir opciones que la tool controla internamente (idioma, formato de salida). Si el usuario no aporta instrucciones, continuar sin el parámetro. No es bloqueante.

### 5. Ejecución

Invocar `create_sql_mappings(domain, view_names?, user_instructions?)`. La tool devuelve un resumen de lo procesado — presentar al usuario directamente.

Si hay errores, reintentar la vista fallida con `user_instructions` mejoradas (max 2 reintentos). Si persiste, documentar y continuar.

### 6. Resumen

Basado en la respuesta de la tool:
- Mappings creados/actualizados
- Errores si los hubo

### 7. Publicación (opcional)

Tras crear o actualizar mappings, ofrecer publicación de las vistas procesadas que esten en estado Draft (verificar con `list_technical_domain_concepts`; las vistas ya en Pending Publish o Published no aplican):
- "Las vistas con mapping actualizado están listas para publicar. ¿Quieres publicarlas? Esto cambiara su estado a Pending Publish, listas para ser publicadas al virtualizador de datos."
- Si el usuario acepta → ejecutar `publish_business_views(domain, view_names)` con las vistas en Draft procesadas → presentar resultado: vistas publicadas + fallidas (transicion no permitida) + no encontradas
- Si el usuario rechaza → continuar con la sugerencia de siguiente paso
- No bloqueante: el usuario decide

Siguiente paso sugerido: "Puedes generar los términos semánticos con `/create-semantic-terms`. Si no has publicado ahora, puedes hacerlo más tarde"
