---
name: create-sql-mappings
description: "Crear o actualizar los SQL mappings de vistas de negocio existentes en Stratio Governance, sin recrear las vistas, y opcionalmente publicarlas después. Usar cuando el usuario quiera corregir un mapping, arreglar el SQL de una vista, añadir columnas que falten, o recuperarse de una creación parcial de mappings. Para regeneración end-to-end de vistas + mappings, preferir create-business-views."
argument-hint: "[dominio técnico (opcional)]"
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

**Reglas clave**: `domain_name` inmutable. Construir `user_instructions` mediante el Workflow de Enriquecimiento con Instrucciones del Glosario (`skills-guides/stratio-semantic-layer-tools.md` §11) antes de invocar. `create_sql_mappings` sobrescribe mappings existentes (no es destructivo a nivel de vista, solo reemplaza el mapping SQL).

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

### 4. Enriquecimiento con instrucciones del glosario

Antes de invocar la tool MCP, aplicar el Workflow de Enriquecimiento con Instrucciones del Glosario descrito en `skills-guides/stratio-semantic-layer-tools.md` §11, acotado a **SQL mappings** (al llamar a `get_glossary_instructions`, pedir solo la fase de mapping). Aquí es donde el usuario puede traerse las instrucciones GenAI de mapping desde el diccionario de datos, aportar un fichero externo (documentación técnica, diagramas ER, especificaciones de integración, scripts SQL de referencia) como su fuente, superponer reglas de mapping en texto libre, o saltar el enriquecimiento por completo.

Si el orquestador ya pre-cargó instrucciones enriquecidas para esta fase durante el flujo de `build-semantic-layer`, reutilizarlas — opcionalmente preguntar al usuario si quiere añadir algo específico para esta fase encima de lo que ya se cargó.

El texto enriquecido se usa como argumento `user_instructions` en la llamada MCP del paso siguiente. Si el usuario eligió la opción 4 (saltar), se omite `user_instructions`.

### 5. Ejecución

Invocar `create_sql_mappings(domain, view_names?, user_instructions?)`. La tool devuelve un resumen de lo procesado — presentar al usuario directamente.

Si hay errores, reintentar la vista fallida con `user_instructions` mejoradas (max 2 reintentos). Si persiste, documentar y continuar.

### 6. Resumen

Basado en la respuesta de la tool:
- Mappings creados/actualizados
- Errores si los hubo

### 6.5 Validación opcional pre-publicación (datos de muestra)

Tras crear o actualizar los mappings y antes de ofrecer la publicación, ofrecer al usuario una verificación con datos de muestra:

- "¿Quieres que ejecute la SQL del mapping (LIMIT 5) de cada vista procesada y te muestre los resultados antes de decidir sobre la publicación?"
- La respuesta de `create_sql_mappings` de §5 ya incluye `processed_views`: una lista de `BusinessViewSummary` de las vistas recién procesadas, cada una con la SQL recién generada en `sql_mapping`. Usar esa SQL tal cual, envolviéndola como `SELECT * FROM (<sql_mapping>) AS m LIMIT 5` para preservar la proyección original. **No hace falta** volver a llamar a `list_technical_domain_concepts` aquí.
- Restringir la validación a las vistas presentes en `processed_views` (las realmente procesadas en §5). **Cap por defecto en 5 vistas**; si en §5 se procesaron más, preguntar al usuario qué subconjunto validar.
- Para cada vista seleccionada: ejecutar `execute_sql` con la query envuelta. Lanzar todas las vistas seleccionadas **en paralelo** en la misma respuesta.
- Renderizar resultados como tablas Markdown siguiendo `skills-guides/stratio-data-tools.md` §4 (cap por defecto de 10 filas en chat).
- **Sin improvisación**: si `sql_mapping` viene vacío para alguna vista dentro de `processed_views` (backend de gov no expone aún el campo, o el mapping recién creado no se persistió correctamente), NO improvisar un SELECT sobre las tablas fuente. Decirle al usuario: "No puedo validar la SQL de este mapping desde aquí porque el backend no la está exponiendo. Puedes validarla desde la UI de Governance, en la vista." Saltar esa vista y continuar con las demás.
- Si `execute_sql` no está disponible en este agente, no caer al fallback de `query_data` con lenguaje natural sobre las tablas fuente (no validaría el mapping). Informar al usuario y derivar a la UI de Governance.
- Este paso es no-bloqueante: independientemente del resultado de la validación, continuar con §7 Publicación.

### 7. Publicación (opcional)

Tras crear o actualizar mappings, ofrecer publicación de las vistas procesadas que esten en estado Draft (verificar con `list_technical_domain_concepts`; las vistas ya en Pending Publish o Published no aplican):
- "Las vistas con mapping actualizado están listas para publicar. ¿Quieres publicarlas? Esto cambiara su estado a Pending Publish, listas para ser publicadas al virtualizador de datos."
- Si el usuario acepta → ejecutar `publish_business_views(domain, view_names)` con las vistas en Draft procesadas → presentar resultado: vistas publicadas + fallidas (transicion no permitida) + no encontradas
- Si el usuario rechaza → continuar con la sugerencia de siguiente paso
- No bloqueante: el usuario decide

Siguiente paso sugerido: "Puedes generar los términos semánticos con `/create-semantic-terms`. Si no has publicado ahora, puedes hacerlo más tarde"
