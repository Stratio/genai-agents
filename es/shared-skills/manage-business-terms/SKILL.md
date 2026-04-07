---
name: manage-business-terms
description: Crear Business Terms en el diccionario de Stratio Governance con relaciones
  a activos de datos. Planificación guiada — nombre, descripción, tipo y relaciones.
argument-hint: [dominio (opcional)]
---

# Skill: Gestionar Business Terms

Crea Business Terms en el diccionario de Stratio Governance con relaciones a activos de datos. Incluye planificación guiada para definir nombre, descripción, tipo y activos relacionados.

## Tools MCP utilizadas

| Tool | Servidor | Propósito |
|------|----------|-----------|
| `search_domains(search_text, domain_type?, refresh?)` | sql | **Preferir**. Buscar dominios por texto libre (acepta técnicos y semánticos). Resultados por relevancia |
| `list_domains(domain_type?, refresh?)` | sql | Listar dominios disponibles (acepta técnicos y semánticos). `refresh=true` para bypass de cache |
| `list_domain_tables(domain)` | sql | Descubrir tablas de un dominio para relaciones |
| `get_table_columns_details(domain, table)` | sql | Descubrir columnas para relaciones a nivel columna |
| `list_business_asset_types()` | gov | Tipos de activos disponibles para business terms |
| `create_business_term(domain, name, description, type, related_assets)` | gov | Crear business term en el diccionario |

**Reglas clave**: `domain_name` inmutable. Business terms aceptan tanto dominios técnicos como semánticos (`semantic_*`). Los activos relacionados siguen una jerarquia de granularidad.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene nombre de dominio, buscar con `search_domains($ARGUMENTS)` (acepta tanto dominios técnicos como semánticos). Si no coincide, reintentar con `search_domains($ARGUMENTS, refresh=true)` por si es un dominio recién creado o publicado. Si ahora coincide, continuar. Si no coincide o no hay argumento, listar dominios con `list_domains()` y preguntar al usuario siguiendo la convención de preguntas al usuario.

### 2. Planificación guiada

Para cada business term, planificar estos campos:

**Nombre del término**: Proponer basado en el contexto o pedir al usuario.

**Descripción**: Texto en Markdown con la definición completa del término. Proponer una descripción basada en el contexto del dominio, o pedir al usuario que la proporcione.

**Tipo de activo**: Ejecutar `list_business_asset_types()` y presentar tipos disponibles al usuario para selección.

**Activos relacionados** — Explicar la jerarquia al usuario:
- Formato: `collection.table.column`, `collection.table`, o `collection`
- **Regla de granularidad**:
  - Si el término aplica a **columnas específicas** → relacionar con las columnas (no añadir tabla ni colección redundantemente)
  - Si aplica a **tablas específicas** → relacionar con las tablas (no añadir colección)
  - Si aplica a **más de 2 tablas** del mismo dominio → relacionar con la colección directamente
- El usuario decide la granularidad final — presentar la recomendación pero respetar su criterio

Para descubrir activos disponibles:
- `list_domain_tables(domain)` → tablas del dominio
- `get_table_columns_details(domain, table)` → columnas de tablas específicas

**Agrupación**: El usuario puede querer agrupar varios conceptos en un solo business term o crear términos separados. Preguntar si aplica — esta es una decisión del usuario.

### 3. Aprobación

Mostrar el término completo antes de crear:
```
## Business Term: [nombre]
- **Tipo**: [tipo seleccionado]
- **Descripción**: [descripción en Markdown]
- **Activos relacionados**:
  - collection.table.column1
  - collection.table.column2
```

Permitir al usuario editar cualquier campo antes de confirmar.

### 4. Ejecución

Invocar `create_business_term(domain, name, description, type, related_assets)` con los datos aprobados.

Si hay error, analizar la causa y ofrecer reintentar con ajustes (max 2 reintentos por término).

### 5. Modo batch

Si el usuario quiere crear múltiples business terms:
1. Planificar todos los términos en una lista
2. Presentar lista completa para aprobación
3. Crear secuencialmente
4. Presentar resumen final:
   - Términos creados con éxito
   - Errores si los hubo
   - Nota: "Los business terms se crean en estado Draft. Serán revisados en la UI de Governance"
