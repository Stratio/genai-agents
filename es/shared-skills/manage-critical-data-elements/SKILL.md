---
name: manage-critical-data-elements
description: "Consultar o definir Elementos de Dato Críticos (CDEs) para un dominio gobernado. Flujo A: ver CDEs actuales. Flujo B: taggear tablas/columnas como críticas — manualmente, por recomendación del agente, o combinado. Pausa de aprobación obligatoria antes de cualquier operación de tagueado."
argument-hint: "[dominio]"
---

# Skill: Gestión de Elementos de Dato Críticos

Workflow para consultar y definir Elementos de Dato Críticos (CDEs) en un dominio gobernado. Los CDEs son los assets de dato — tablas o columnas específicas — considerados más importantes para el negocio. Reciben tratamiento de calidad prioritario: los assessments se focalizan en ellos primero, y los gaps en assets CDE se elevan a un nivel de prioridad superior.

## PAUSA DE APROBACION CRITICA

**NUNCA llamar `set_critical_data_elements` sin confirmación explícita del usuario.**

**Las respuestas HTTP 409 durante el tagueado significan que el asset ya estaba tagueado como CDE.** Esto NO es un error — contar estos como "ya tagueado" y NO tratarlos como fallos en los resultados ni en el resumen.

---

## 1. Determinación de Scope

### 1.1 Validar el dominio

Si `$ARGUMENTS` proporciona un nombre de dominio, buscar con `search_domains($ARGUMENTS)`. Si no se encuentra, reintentar con `search_domains($ARGUMENTS, refresh=true)`. Si sigue sin encontrarse, o si no se proporcionó argumento, listar dominios con `list_domains()` y preguntar al usuario con opciones siguiendo la convención de preguntas al usuario.

**Regla CRITICA**: el `collection_name` usado en todas las llamadas MCP debe ser **exactamente** el valor devuelto por `search_domains` o `list_domains`. NUNCA traducirlo, interpretarlo, parafrasearlo ni inferirlo.

### 1.2 Determinar flujo

Si la petición del usuario ya deja clara la intención, proceder directamente:
- "Muéstrame los CDEs" / "¿Cuáles son los elementos de dato críticos de [dominio]?" → **Flujo A**
- "Recomienda CDEs" / "Define los CDEs" (sin asset concreto mencionado) → **Flujo B** (preguntar método en B.2)
- "Taggea [tabla/columna concreta] como crítica" / "Marca [tabla/columna] como CDE" (el usuario nombra assets exactos) → **Flujo B, saltar B.2, ir directamente a B1** con esos assets pre-cargados. NO preguntar al usuario que elija un método — ya especificó qué taggear.

Si no está claro, preguntar al usuario con opciones siguiendo la convención de preguntas al usuario:
1. **Ver CDEs actuales** — consultar qué está actualmente marcado como crítico en este dominio
2. **Definir/actualizar CDEs** — taggear tablas o columnas como Elementos de Dato Críticos

---

## Flujo A: Ver CDEs Actuales

### A.1 Obtener y presentar los CDEs actuales

Llamar a `get_critical_data_elements(collection_name=domain_name)`.

Presentar los resultados con estructura clara:

```markdown
## Elementos de Dato Críticos — [domain_name]

### Tablas completamente críticas (todas las columnas son CDEs)
| Tabla |
|-------|
| account |
| district |

### Tablas con columnas CDE específicas
| Tabla | Columnas CDE |
|-------|-------------|
| card | card_id, disp_id |
| transaction | account_id, bank, date, trans_id |
```

Si tanto `critical_tables` como `columns_by_table` están vacíos o ausentes: "No hay Elementos de Dato Críticos definidos actualmente para este dominio."

### A.2 Opcional: comprobación rápida de cobertura de calidad

Tras presentar los CDEs, ofrecer al usuario una comprobación rápida de la cobertura de calidad sobre los assets CDE. Si acepta:

1. Llamar a `get_tables_quality_details(domain_name, [todas las tablas CDE])` — tablas de `critical_tables` más tablas con entradas en `columns_by_table`
2. Presentar una tabla resumen:

```markdown
| Tabla | Tipo CDE | Reglas definidas | Estado |
|-------|----------|-----------------|--------|
| account | Tabla completa | 4 | OK |
| card | Columnas específicas | 1 | Warning |
| transaction | Columnas específicas | 0 | Sin reglas |
```

3. Si alguna tabla CDE no tiene reglas definidas: destacarlo como gap de calidad a abordar.

### A.3 Pregunta de continuación

Preguntar al usuario con opciones siguiendo la convención de preguntas al usuario:
- **Definir o actualizar CDEs para este dominio** (continuar con el Flujo B)
- **Evaluar la cobertura de calidad focalizada en los CDEs** (cargar `assess-quality`)
- **Finalizar**

---

## Flujo B: Definir/Actualizar CDEs

### B.1 Obtener baseline en paralelo

Antes de recomendar o recopilar input del usuario, obtener el estado actual:

```
Paralelo:
  A. list_domain_tables(domain_name)
  B. get_critical_data_elements(collection_name=domain_name)   ← baseline: CDEs actuales
```

### B.2 Determinar método de definición

Preguntar al usuario con opciones siguiendo la convención de preguntas al usuario:
1. **Especificación manual** — Indicaré directamente qué tablas/columnas taggear como CDEs
2. **Recomendación del agente** — Analiza la semántica del dominio y el perfil de datos, luego recomienda CDEs para mi confirmación
3. **Combinado** — El agente recomienda y yo ajusto antes de confirmar

---

### Flujo B1: Especificación Manual

Presentar la lista de tablas disponibles del dominio (de `list_domain_tables`) para ayudar al usuario a elegir. Si el usuario quiere inspeccionar las columnas de una tabla concreta, llamar a `get_table_columns_details(domain_name, tabla)` bajo petición.

Recopilar del usuario:
- Qué **tablas completas** taggear como críticas (todas las columnas de esas tablas pasan a ser CDEs)
- Qué **columnas específicas** de qué tablas taggear como CDEs

Validar que todas las tablas y columnas mencionadas existen en el dominio antes de continuar. Comparar los assets especificados por el usuario con el baseline de B.1:
- Assets que **no** están en el baseline → incluir en el payload de tagueado (verdaderamente nuevos)
- Assets que ya están en el baseline → **excluir** del payload; anotarlos como "Ya tagueados" en el plan

**Regla del payload**: el payload de tagueado debe contener ÚNICAMENTE los assets que no están en el baseline. Si el usuario solicitó N assets pero todos N ya están tagueados, el payload está vacío — omitir la llamada a la API por completo y presentar el resultado como "todos los assets solicitados ya estaban marcados como CDEs".

Continuar en la **Pausa de Aprobación B.4**.

---

### Flujo B2: Recomendación del Agente

#### B2.1 Recopilar información en paralelo

```
Paralelo:
  A. get_tables_details(domain_name, [todas_las_tablas])
  B. get_table_columns_details(domain_name, tabla)             [por cada tabla — en paralelo]
  C. get_tables_quality_details(domain_name, [todas_las_tablas])  ← reglas existentes como señal
```

Luego perfilar los datos por tabla:
```
Por cada tabla (en paralelo):
  generate_sql("obtener todos los campos de la tabla [tabla] sin filtros", domain_name)
  → profile_data(query=[sql])
```

#### B2.2 Criterios de recomendación

**A nivel de tabla (taggear tabla entera como CDE):**
- Entidades maestras o de referencia (cuentas, clientes, productos, ubicaciones, categorías)
- Tablas descritas en el dominio como fundamentales o centrales para los procesos de negocio
- Tablas con muchas relaciones de clave foránea apuntando hacia ellas desde otras tablas
- Tablas mencionadas explícitamente en reglas de negocio documentadas como fuentes de verdad

**A nivel de columna (taggear columnas específicas dentro de una tabla):**
- Claves primarias e identificadores de negocio — completeness + uniqueness son críticos por definición
- Claves foráneas obligatorias que garantizan la integridad referencial del dominio
- Columnas definidas en el glosario del dominio con términos de negocio o definiciones formales
- Columnas de métricas financieras u operacionales core (importes, conteos, tasas centrales para reporting)
- Columnas de fecha que determinan la frescura del dato, cumplimiento de SLAs o ventanas de reporting regulatorio
- Columnas de estado o estado de proceso que controlan flujos de aprobación o negocio
- Columnas ya cubiertas por múltiples reglas de calidad — la inversión previa indica importancia

**Señales EDA que refuerzan una recomendación:**
- Nulos existentes en una columna que debería ser no-nula → evidencia inmediata de riesgo
- Duplicados en un candidato a clave primaria → problema crítico de integridad
- Columnas con varias reglas de calidad ya definidas → alguien ya las consideró críticas

#### B2.3 Presentar la recomendación

```markdown
## Elementos de Dato Críticos Recomendados — [domain_name]

**Base**: análisis semántico de la descripción del dominio, contexto de tablas, definiciones
de columnas, terminología del dominio, resultados EDA y reglas de calidad existentes.

### Tablas completamente críticas recomendadas (todas las columnas pasan a ser CDEs)

| Tabla | Motivo |
|-------|--------|
| account | Entidad maestra — todas las columnas son identificadores, saldos o campos críticos de proceso |
| district | Tabla de referencia — proporciona datos maestros geográficos usados en 3+ tablas |

### Tablas con columnas CDE específicas recomendadas

| Tabla | Columnas recomendadas | Motivo |
|-------|----------------------|--------|
| card | card_id, disp_id | Clave primaria + FK obligatoria — identificadores core de integridad |
| transaction | account_id, trans_id, date, amount | FK, ID de negocio, fecha de frescura, métrica financiera core |

### Tablas no recomendadas como CDEs

| Tabla | Motivo |
|-------|--------|
| order | Tabla operacional secundaria; no se identifica rol de maestro/referencia |
```

Informar al usuario de que puede aceptar, modificar o rechazar elementos individuales antes de confirmar.

---

### Flujo B3: Combinado

Ejecutar primero el **Flujo B2** (recomendación del agente) y luego permitir al usuario:
- Añadir tablas o columnas no incluidas en la recomendación
- Eliminar tablas o columnas de la recomendación
- Promover un CDE a nivel de columna a un CDE de tabla completa (o degradarlo)
- Aceptar la recomendación tal cual

Recopilar la lista final acordada y continuar con la pausa de aprobación.

---

### B.4 PAUSA: Presentar Plan y Esperar Aprobación

Antes de llamar a `set_critical_data_elements`, presentar el plan completo de tagueado:

- **Assets a taggear como críticos** = solo los assets que NO están en el baseline (operaciones de tagueado verdaderamente nuevas).
- **Ya tagueados** = assets de la especificación del usuario que ya estaban en el baseline — se muestran por transparencia, pero se excluyen de la llamada a la API.

```markdown
## Plan de Tagueado de CDEs — [domain_name]

**Dominio**: [collection_name]
**Origen**: [Especificación manual | Recomendación del agente | Combinado]

### Assets a taggear como críticos (nuevos — no presentes en el baseline)

**Tablas completamente críticas** (todas las columnas pasarán a ser CDEs):
- account
- district
- loan

**Tablas con columnas CDE específicas**:
| Tabla | Columnas a taggear |
|-------|-------------------|
| card | card_id, disp_id |
| transaction | account_id, bank, date, trans_id |

**Ya tagueados** (del baseline actual — se contarán como retenidos, no como errores):
- [lista o "Ninguno"]

---

¿Procedo con el tagueado de estos assets como Elementos de Dato Críticos?
```

**Señales válidas de aprobación**: "sí", "procede", "adelante", "ok", "aprobado", "confirmado", "hazlo", o equivalentes en el idioma del usuario.

**Señales de rechazo o modificación**: "no", "cancela", "quita X", "añade Y", "cambia". Si el usuario modifica: actualizar el plan, presentarlo de nuevo y esperar confirmación.

### B.5 Ejecución

Solo tras aprobación explícita, llamar a `set_critical_data_elements` con **únicamente los assets que son nuevos** (no presentes en el baseline de B.1).

**CRÍTICO — el payload debe contener ÚNICAMENTE assets nuevos:**
- Cruzar el payload con el baseline obtenido en B.1 (resultado de `get_critical_data_elements`).
- Eliminar del payload CUALQUIER asset (tabla o columna) que ya aparezca en el baseline.
- NO incluir CDEs ya tagueados. La API es aditiva, no reemplaza todo: re-enviar un CDE existente provoca un error 409 y nunca es necesario.
- Si la especificación del usuario coincide con solo 1 asset nuevo, el payload contiene exactamente 1 asset. Si coincide con 0 assets nuevos, omitir la llamada a la API por completo.

```json
{
  "collection_name": "domain_name",
  "critical_tables": ["account", "district", "loan"],
  "columns_by_table": {
    "card": ["card_id", "disp_id"],
    "transaction": ["account_id", "bank", "date", "trans_id"]
  }
}
```

### B.6 Presentar resultados

Parsear la respuesta y presentar una tabla de resultados:

```markdown
## Resultado del Tagueado de CDEs — [domain_name]

| Asset | Resultado |
|-------|-----------|
| account (tabla completa) | Tagueado correctamente |
| district (tabla completa) | Ya estaba tagueado — sin cambios |
| card.card_id | Tagueado correctamente |
| card.disp_id | Tagueado correctamente |
| transaction.account_id | Ya estaba tagueado — sin cambios |
| transaction.bank | Tagueado correctamente |

**Resumen**:
- Tagueados correctamente: N
- Ya estaban tagueados (retenidos): M
- Fallidos: X
```

- HTTP 409 → mostrar como "Ya estaba tagueado — sin cambios" y contabilizar como **retenido**, no como fallo
- Otros errores → mostrar como "Fallido" con una breve nota del motivo bajo la tabla

---

## 7. Pregunta de Continuación

Preguntar al usuario con opciones siguiendo la convención de preguntas al usuario:
- **Evaluar la cobertura de calidad focalizada en los CDEs** (cargar `assess-quality`)
- **Ver la lista actualizada de CDEs de este dominio**
- **Definir CDEs para otro dominio**
- **Finalizar**
