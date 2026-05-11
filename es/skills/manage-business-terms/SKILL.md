---
name: manage-business-terms
description: "Crear business terms en el diccionario de Stratio Governance, de forma individual o en batch, con relaciones a activos de datos, mediante planificación guiada (nombre, descripción, tipo, relaciones). Usar cuando el usuario quiera añadir, enlazar o documentar business terms (KPIs, conceptos, acrónimos) en el diccionario, o conectar un término existente con tablas y columnas concretas. Para semantic terms masivos de vistas, preferir create-semantic-terms."
argument-hint: "[dominio (opcional)]"
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

## Selección de dominio — DEFAULT FUERTE: semántico

> *Alcance: esta regla de selección de dominio es específica de `create_business_term` y del workflow de esta skill. NO se generaliza a otras tools de gobernanza — `create_technical_terms`, `create_ontology`, `create_business_views`, `create_sql_mappings`, `create_semantic_terms` y `publish_business_views` siguen usando el dominio técnico.*

`create_business_term` es una operación **post-publicación**: se ejecuta después de construir y publicar la capa semántica, no forma parte del pipeline de construcción. **Default: preferir el dominio semántico / business (`semantic_<x>`)**. Los business terms describen conceptos de negocio; pertenecen bajo "Semantic Knowledge". Si existe `semantic_<x>`, úsalo como `domain` — no preguntes al usuario. El dominio técnico es la **excepción**, no el default.

**Cuándo elegir el dominio técnico** (edge cases legítimos y plenamente soportados — proceder sin oponerse):

- El término describe un *artefacto del modelo físico* sin representación en la capa semántica: una columna concreta, un tipo de dato, una regla de carga, una restricción operacional que sólo tiene sentido para un ingeniero de datos.
- El dominio técnico **no tiene capa semántica publicada** (`semantic_<x>` no existe) y el usuario quiere documentar el término igualmente.
- El usuario **pide explícitamente** vincular el término al dominio técnico (p. ej. "documenta esto en la capa raw"). La intención del usuario sobreescribe el default; confirma brevemente en una línea si `semantic_<x>` también existe.

**Coherencia de prefijo**: cada entrada de `related_assets` debe empezar por el **mismo** valor que `domain` — la chain rechaza prefijos mezclados. Si `domain="semantic_finance"`, todos los activos relacionados deben empezar por `semantic_finance.`.

**Inmutabilidad de `domain_name`**: el valor pasado a la tool debe ser **exactamente** el devuelto por `list_domains` / `search_domains` — sin traducir, parafrasear ni reformatear.

**Ejemplos**:
- *Semántico (default)* — KPI "Customer Lifetime Value" sobre una capa semántica publicada: `domain="semantic_finance"`, `related_assets=["semantic_finance.card.clv"]`. Sin pregunta al usuario.
- *Técnico — sin capa semántica publicada* — columna `tx_id` en `raw_finance` sin `semantic_raw_finance`: `domain="raw_finance"`, `related_assets=["raw_finance.transactions.tx_id"]`. Informa al usuario antes de proceder.
- *Técnico — petición explícita del usuario* — el usuario dice "documenta esto en la capa raw" aunque exista `semantic_raw_finance`: `domain="raw_finance"`, `related_assets=["raw_finance.transactions.tx_id"]`. Confirma la intención en una línea.

## Workflow

### 1. Determinar dominio

Buscar con `search_domains($ARGUMENTS)` (sin filtro `domain_type` — devuelve técnicos y semánticos). Si no coincide, reintentar con `refresh=true` por si es un dominio recién creado o publicado. Si sigue sin coincidir (o `$ARGUMENTS` está vacío), listar con `list_domains()` y preguntar al usuario siguiendo la convención de preguntas al usuario.

Aplicar la regla de Selección de dominio de arriba: **si existe `semantic_<x>`, fijar `domain="semantic_<x>"`** (default — no preguntar). Si sólo existe `<x>` y el término es un concepto de negocio, informar al usuario que el dominio aún no ha publicado capa semántica y preguntar si proceder bajo el dominio técnico o abortar. Sea cual sea el `domain` elegido, todos los `related_assets` deben usar el mismo prefijo.

### 2. Planificación guiada

Para cada business term, planificar estos campos:

**Nombre del término**: Proponer basado en el contexto o pedir al usuario.

**Descripción**: Texto en Markdown con la definición completa del término. Proponer una descripción basada en el contexto del dominio, o pedir al usuario que la proporcione.

**Tipo de activo**: Ejecutar `list_business_asset_types()` y presentar tipos disponibles al usuario para selección.

**Activos relacionados** — Explicar la jerarquia al usuario:
- Formato: `collection.table.column`, `collection.table`, o `collection`. El prefijo `collection.` debe coincidir con el `domain` elegido arriba (en la práctica, con el prefijo `semantic_` salvo que aplique la excepción del dominio técnico).
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
