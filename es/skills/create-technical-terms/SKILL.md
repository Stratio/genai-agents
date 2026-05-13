---
name: create-technical-terms
description: "Crear o regenerar technical terms — descripciones de tablas y columnas — en Stratio Governance para un dominio técnico completo, y sembrar la descripción de la colección cuando falte. Usar cuando el usuario quiera documentar tablas y columnas, generar descripciones en masa para un nuevo dominio, refrescarlas tras cambios de esquema, o recuperar technical terms que falten."
argument-hint: "[dominio técnico (opcional)]"
---

# Skill: Crear Términos Técnicos

Crea descripciones técnicas de tablas y columnas de un dominio en Stratio Governance. Fase 1 del pipeline de capa semántica.

## Tools MCP utilizadas

| Tool | Servidor | Propósito |
|------|----------|-----------|
| `search_domains(search_text, domain_type='technical')` | sql | **Preferir**. Buscar dominios técnicos por texto libre. Resultados por relevancia |
| `list_domains(domain_type='technical', refresh?)` | sql | Listar todos los dominios técnicos (incluye descripción si existe). `refresh=true` para bypass de cache |
| `list_domain_tables(domain)` | sql | Listar tablas con sus descripciones (indica si ya tienen términos técnicos) |
| `create_technical_terms(domain, table_names?, user_instructions?, regenerate?)` | gov | Crear términos técnicos. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |

**Reglas clave**: `domain_name` inmutable (valor exacto de `list_domains` o `search_domains`). Confirmación obligatoria para `regenerate=true`. Construir `user_instructions` mediante el Workflow de Enriquecimiento con Instrucciones del Glosario (`guides/stratio-semantic-layer-tools.md` §11) antes de invocar.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene un nombre de dominio, buscar con `search_domains($ARGUMENTS, domain_type='technical')`. Si coincide con un resultado, continuar. Si no coincide, reintentar con `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` por si es una colección recién creada. Si ahora coincide, continuar. Si sigue sin coincidir o no hay argumento, listar dominios con `list_domains(domain_type='technical')` y preguntar al usuario siguiendo la convención de preguntas al usuario.

### 2. Evaluar estado

Ejecutar `list_domain_tables(domain)` para evaluar el estado actual:
- Tablas con descripción → ya tienen términos técnicos generados
- Tablas sin descripción → pendientes de generar
- Si el dominio tiene descripción (visible en `list_domains(domain_type='technical')`) → la descripción general ya existe

Presentar resumen al usuario:
```
## Estado — [domain_name]
- Tablas totales: N
- Con términos técnicos: X
- Pendientes: Y
- Descripción del dominio: Si/No
```

### 3. Selección de alcance

Preguntar al usuario con opciones:
1. **Crear para todas las tablas** — idempotente: `create_technical_terms` salta tablas que ya tienen descripción
2. **Crear para tablas específicas** — selección múltiple de las tablas pendientes
3. **Regenerar todas** — DESTRUCTIVO: borra y recrea. Requiere confirmación explícita
4. **Regenerar tablas específicas** — DESTRUCTIVO para las seleccionadas. Requiere confirmación explícita

### 4. Enriquecimiento con instrucciones del glosario

Antes de invocar la tool MCP, aplicar el Workflow de Enriquecimiento con Instrucciones del Glosario descrito en `guides/stratio-semantic-layer-tools.md` §11, acotado a **technical terms** (al llamar a `get_glossary_instructions`, pedir solo la fase de technical terms).

Si el orquestador ya pre-cargó instrucciones enriquecidas para esta fase durante el flujo de `build-semantic-layer`, reutilizarlas en lugar de volver a preguntar — opcionalmente preguntar al usuario si quiere añadir algo específico para esta fase encima de lo que ya se cargó.

El texto enriquecido se usa como argumento `user_instructions` en la llamada MCP del paso siguiente. Si el usuario eligió la opción 4 (saltar), se omite `user_instructions`.

### 5. Ejecución

Invocar `create_technical_terms`. Para regenerar: pasar `regenerate=true` (DESTRUCTIVO). La tool devuelve un resumen de lo procesado — presentar ese resumen al usuario directamente. No llamar a tools adicionales post-creación para no llenar contexto.

**Nota sobre descripción de dominio**: `create_technical_terms` genera automáticamente la descripción del dominio/colección si no tiene. No es necesario llamar a `create_collection_description` como paso separado.

### 6. Resumen

Basado en la respuesta de la tool, presentar:
- Tablas procesadas
- Errores si los hubo (reintentar entidades fallidas con `user_instructions` mejoradas, max 2 reintentos)
- Siguientes pasos sugeridos:
  - "Puedes crear una ontología con `/create-ontology`"
  - "Si necesitas corregir, añadir o eliminar claves foráneas virtuales concretas sin regenerar los términos técnicos, usa `/refine-foreign-keys`"
