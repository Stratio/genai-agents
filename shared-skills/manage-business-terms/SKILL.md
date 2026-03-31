---
name: manage-business-terms
description: Crear Business Terms en el diccionario de Stratio Governance con relaciones
  a activos de datos. Planificacion guiada — nombre, descripcion, tipo y relaciones.
argument-hint: [dominio (opcional)]
---

# Skill: Gestionar Business Terms

Crea Business Terms en el diccionario de Stratio Governance con relaciones a activos de datos. Incluye planificacion guiada para definir nombre, descripcion, tipo y activos relacionados.

## Tools MCP utilizadas

| Tool | Servidor | Proposito |
|------|----------|-----------|
| `search_domains(search_text, domain_type?, refresh?)` | sql | **Preferir**. Buscar dominios por texto libre (acepta tecnicos y semanticos). Resultados por relevancia |
| `list_domains(domain_type?, refresh?)` | sql | Listar dominios disponibles (acepta tecnicos y semanticos). `refresh=true` para bypass de cache |
| `list_domain_tables(domain)` | sql | Descubrir tablas de un dominio para relaciones |
| `get_table_columns_details(domain, table)` | sql | Descubrir columnas para relaciones a nivel columna |
| `list_business_asset_types()` | gov | Tipos de activos disponibles para business terms |
| `create_business_term(domain, name, description, type, related_assets)` | gov | Crear business term en el diccionario |

**Reglas clave**: `domain_name` inmutable. Business terms aceptan tanto dominios tecnicos como semanticos (`semantic_*`). Los activos relacionados siguen una jerarquia de granularidad.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene nombre de dominio, buscar con `search_domains($ARGUMENTS)` (acepta tanto dominios tecnicos como semanticos). Si no coincide, reintentar con `search_domains($ARGUMENTS, refresh=true)` por si es un dominio recien creado o publicado. Si ahora coincide, continuar. Si no coincide o no hay argumento, listar dominios con `list_domains()` y preguntar al usuario siguiendo la convencion de preguntas al usuario.

### 2. Planificacion guiada

Para cada business term, planificar estos campos:

**Nombre del termino**: Proponer basado en el contexto o pedir al usuario.

**Descripcion**: Texto en Markdown con la definicion completa del termino. Proponer una descripcion basada en el contexto del dominio, o pedir al usuario que la proporcione.

**Tipo de activo**: Ejecutar `list_business_asset_types()` y presentar tipos disponibles al usuario para seleccion.

**Activos relacionados** — Explicar la jerarquia al usuario:
- Formato: `collection.table.column`, `collection.table`, o `collection`
- **Regla de granularidad**:
  - Si el termino aplica a **columnas especificas** → relacionar con las columnas (no anadir tabla ni coleccion redundantemente)
  - Si aplica a **tablas especificas** → relacionar con las tablas (no anadir coleccion)
  - Si aplica a **mas de 2 tablas** del mismo dominio → relacionar con la coleccion directamente
- El usuario decide la granularidad final — presentar la recomendacion pero respetar su criterio

Para descubrir activos disponibles:
- `list_domain_tables(domain)` → tablas del dominio
- `get_table_columns_details(domain, table)` → columnas de tablas especificas

**Agrupacion**: El usuario puede querer agrupar varios conceptos en un solo business term o crear terminos separados. Preguntar si aplica — esta es una decision del usuario.

### 3. Aprobacion

Mostrar el termino completo antes de crear:
```
## Business Term: [nombre]
- **Tipo**: [tipo seleccionado]
- **Descripcion**: [descripcion en Markdown]
- **Activos relacionados**:
  - collection.table.column1
  - collection.table.column2
```

Permitir al usuario editar cualquier campo antes de confirmar.

### 4. Ejecucion

Invocar `create_business_term(domain, name, description, type, related_assets)` con los datos aprobados.

Si hay error, analizar la causa y ofrecer reintentar con ajustes (max 2 reintentos por termino).

### 5. Modo batch

Si el usuario quiere crear multiples business terms:
1. Planificar todos los terminos en una lista
2. Presentar lista completa para aprobacion
3. Crear secuencialmente
4. Presentar resumen final:
   - Terminos creados con exito
   - Errores si los hubo
   - Nota: "Los business terms se crean en estado Draft. Seran revisados en la UI de Governance"
