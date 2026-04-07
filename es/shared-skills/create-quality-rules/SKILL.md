---
name: create-quality-rules
description: "Diseñar y crear reglas de calidad. Flujo A (gaps): cubrir gaps identificados en una evaluación de cobertura previa. Flujo B (regla concreta): crear una regla específica descrita por el usuario sin evaluación previa. Ambos flujos requieren confirmación humana obligatoria antes de ejecutar."
argument-hint: "[dominio] [tabla (opcional)]"
---

# Skill: Creación de Reglas de Calidad

Workflow para diseñar, proponer y crear reglas de calidad con aprobación humana. Esta skill tiene un prerequisito obligatorio y una pausa de aprobación crítica.

## PREREQUISITO

Esta skill tiene dos flujos de entrada con prerequisitos distintos:

**Flujo A — Gaps (requiere evaluación de cobertura previa):**
El usuario quiere cubrir gaps de cobertura (ej: "crea reglas para el dominio X", "completa la cobertura de la tabla Y"). Este flujo requiere que ya se haya evaluado la cobertura de calidad del scope indicado: inventario de reglas existentes (de `get_tables_quality_details`), gaps identificados y resultados del EDA con `profile_data`. Si estos datos no están disponibles en el contexto de la conversación:
1. Indicar al usuario que primero es necesario evaluar la cobertura
2. Detenerse para que se realice la evaluación antes de continuar

**Flujo B — Regla concreta (NO requiere evaluación previa):**
El usuario describe una regla específica que quiere crear (ej: "crea una regla que verifique que todo cliente en tabla A existe en tabla B", "quiero una regla de validity que compruebe que el importe es positivo en transactions"). En este caso, NO es necesaria una evaluación de cobertura previa — ir directamente a la sección "Flujo B: Regla Concreta" más adelante.

## PAUSA DE APROBACION CRITICA

**NUNCA llamar `create_quality_rule` sin que el usuario haya confirmado explícitamente el plan.**

Esta pausa es el paso más importante de toda la skill. Si hay dudas sobre si el usuario ha aprobado, preguntar de nuevo. No interpretar silencio ni respuestas ambiguas como aprobación.

**La pregunta de scheduling está integrada en la sección 4 (aprobación).** No es un paso separado — se presenta junto con la petición de confirmación para que sea imposible omitirla.

**Cada invocación de esta skill es independiente.** Una aprobación dada anteriormente en la misma conversación NO es válida para un nuevo lote de reglas. Aunque el usuario ya haya aprobado un plan anterior, siempre se debe seguir el paso 4 de nuevo desde cero.

---

## 1. Determinar Tablas con Gaps

A partir del resultado de la evaluación de cobertura, recuperar el inventario de reglas existentes obtenido vía `get_tables_quality_details`. Este inventario es la fuente de verdad: **solo diseñar reglas para dimensiones/columnas que NO estén ya cubiertas por una regla existente**.

Identificar:
- Qué tablas tienen gaps de cobertura (dimensiones esperadas no cubiertas por ninguna regla existente)
- Que dimensiones faltan en cada tabla (considerando tanto las estándar como las específicas del dominio)
- Cuales son los gaps prioritarios basándose en el EDA previo de `profile_data`

**Sobre dimensiones**: las definiciones del dominio (obtenidas en la evaluación de cobertura vía `get_quality_rule_dimensions`) prevalecen siempre sobre las estándar. Ver sección 2 de `skills-guides/quality-exploration.md`.

Si el usuario ha especificado un subset ("solo la tabla account"), respetar esa restricción.

Si hay reglas existentes en estado KO o WARNING: mencionarlas como acción prioritaria antes de crear nuevas. Preguntar si quiere resolver primero esas o continuar con los gaps.

## 2. Diseño de Reglas (a partir del análisis completo de la evaluación de cobertura)

La evaluación de cobertura ya ha producido dos fuentes de información que se usan aquí directamente — no repetir ninguna llamada MCP salvo que el scope haya cambiado:

**Fuente 1 — Análisis semántico** (de `get_tables_details` + `get_table_columns_details`):
El análisis semántico de la evaluación de cobertura determinó *por qué* cada columna necesita cada dimensión: rol de la columna (clave, métrica, estado, FK…), obligatoriedad según negocio, restricciones documentadas en la gobernanza. Ese razonamiento es la justificación de cada regla. Recuperarlo y usarlo como base para la descripción y el diseño del SQL.

**Nota para dominios técnicos**: Si el dominio es técnico, las descripciones de negocio pueden ser limitadas o inexistentes. En ese caso, dar mayor peso al EDA y razonar por nombres/tipos de columnas (convenciones como `*_id`, `*_date`, `*_amount`). Validar con el usuario las asunciones sobre semántica antes de diseñar reglas de `validity` (rangos, enumerados).

**Fuente 2 — EDA** (de `profile_data`):
El perfilado estadístico sirve para parametrizar y priorizar, no para decidir si una regla existe o no:

| Tipo de gap | Señales en EDA | Implicación para el SQL |
|-------------|---------------|------------------------|
| Completeness | `nulls > 0` | Confirma el problema; el % actual orienta la urgencia |
| Uniqueness | `distinct_count < count` | Hay duplicados reales; informar al usuario antes de crear la regla |
| Validity (rango) | `min`, `max` | Orientan el rango — los umbrales finales deben basarse en lógica de negocio, no en los valores actuales |
| Validity (enumerado) | `top_values` | Usar como base para el `IN (...)`, confirmando con el usuario si la lista es exhaustiva |
| Consistency | Columnas relacionadas | Puede requerir cruzar datos; diseñar el SQL con cuidado |

**Atención**: Si el EDA muestra 100% de nulos o valores completamente inválidos, informar al usuario antes de crear la regla — pero no descartarla si la semántica la justifica.

## 3. Diseño de Reglas

Para cada gap identificado, diseñar la regla de calidad correspondiente.

### 3.1 Estructura de una regla

Cada regla tiene los siguientes campos:
- `rule_name`: nombre descriptivo en kebab-case. Convención: `dq-[tabla]-[dimension]-[columna-o-descripcion]`
- `primary_table`: tabla principal a la que pertenece la regla
- `table_names`: lista de tablas referenciadas en los SQLs (incluir primary_table siempre)
- `description`: descripción en lenguaje natural de forma concisa y en términos claros de negocio (sin jerga técnica) que comprueba esta regla, describiendo el resultado esperado. **Reglas obligatorias**: (1) NO incluir información de planificación ni scheduling (frecuencia, horarios, cron). (2) NO usar nombres técnicos de columnas (como `card_id`, `district_id`); en su lugar, usar la definición semántica/de negocio del campo obtenida de `get_table_columns_details`. (3) NO mencionar la dimensión de la regla (completeness, uniqueness, validity, etc.) — la dimensión ya es un campo separado. Ejemplo correcto: "Validates that every account record has a non-null district identifier, ensuring all accounts are assigned to a district". Ejemplo incorrecto: "Completeness check: Checks that district_id is never null. Scheduled daily at 09:00"
- `query`: SQL que cuenta los registros que PASAN el check (numerador)
- `query_reference`: SQL que cuenta el total de registros (denominador)
- `dimension`: completeness / uniqueness / validity / consistency
- `collection_name`: el domain_name del dominio
- `measurement_type`: (opcional) cómo se mide el resultado de calidad. Valores posibles:
  - `percentage` (por defecto): compara query vs query_reference como porcentaje
  - `count`: usa el conteo absoluto de registros de la query
- `threshold_mode`: (opcional) como se definen los umbrales de evaluación. Valores posibles:
  - `exact` (por defecto): valor exacto con operadores `=` y `!=`
  - `range`: rangos con operadores como `>`, `<=`
- `exact_threshold`: (opcional, solo para `threshold_mode=exact`) objeto con:
  - `value`: valor de comparación (ej: `"100"`, `"0"`)
  - `equal_status`: estado cuando resultado = value (`OK`, `KO`, o `WARNING`)
  - `not_equal_status`: estado cuando resultado != value (`OK`, `KO`, o `WARNING`)
  - Default: `{value: "100", equal_status: "OK", not_equal_status: "KO"}`
- `threshold_breakpoints`: (opcional, solo para `threshold_mode=range`) lista ordenada ascendente de puntos de corte. Cada entrada tiene:
  - `value`: limite superior del intervalo (ej: `"50"`, `"80"`)
  - `status`: estado para ese intervalo (`OK`, `KO`, o `WARNING`)
  - La **última entrada** NO lleva `value` (rango abierto hacia arriba); solo `status`
  - Mínimo 2 entradas, al menos una `OK` y una `KO`. Ver sección 3.4
- `cron_expression`: (opcional) expresión Quartz cron para ejecución automática. Si no se indica, la regla no se planifica
- `cron_timezone`: (opcional) timezone del cron; si hay cron y no se específica, usar `Europe/Madrid`
- `cron_start_datetime`: (opcional) ISO 8601 con la primera ejecución programada; si no se indica, la planificación empieza inmediatamente tras la creación

### 3.2 Patrones SQL por dimensión

**Completeness** — columna no nula:
```sql
query:     SELECT COUNT(*) FROM ${tabla} WHERE columna IS NOT NULL
reference: SELECT COUNT(*) FROM ${tabla}
```

**Uniqueness** — sin duplicados en una columna:
```sql
query:     SELECT COUNT(*) FROM (SELECT DISTINCT columna FROM ${tabla})
reference: SELECT COUNT(*) FROM ${tabla}
```

**Uniqueness** — clave compuesta:
```sql
query:     SELECT COUNT(*) FROM (SELECT DISTINCT col1, col2 FROM ${tabla})
reference: SELECT COUNT(*) FROM ${tabla}
```

**Validity (rango numérico)**:
```sql
-- importe no negativo
query:     SELECT COUNT(*) FROM ${tabla} WHERE importe >= 0
reference: SELECT COUNT(*) FROM ${tabla}

-- edad en rango logico
query:     SELECT COUNT(*) FROM ${tabla} WHERE edad BETWEEN 0 AND 150
reference: SELECT COUNT(*) FROM ${tabla}
```

**Validity (enumerado)**:
```sql
query:     SELECT COUNT(*) FROM ${tabla} WHERE estado IN ('ACTIVO', 'INACTIVO', 'PENDIENTE')
reference: SELECT COUNT(*) FROM ${tabla}
```

**Validity (fecha)**:
```sql
-- fecha no futura
query:     SELECT COUNT(*) FROM ${tabla} WHERE fecha_alta <= CURRENT_DATE
reference: SELECT COUNT(*) FROM ${tabla}

-- fecha en rango logico
query:     SELECT COUNT(*) FROM ${tabla} WHERE fecha_alta BETWEEN '1900-01-01' AND CURRENT_DATE
reference: SELECT COUNT(*) FROM ${tabla}
```

**Consistency (entre columnas)**:
```sql
-- fecha inicio antes o igual que fecha fin
query:     SELECT COUNT(*) FROM ${tabla} WHERE fecha_inicio <= fecha_fin OR fecha_fin IS NULL
reference: SELECT COUNT(*) FROM ${tabla}
```

**Consistency (entre tablas)**:
```sql
-- FK valida: todo registro en tabla_a tiene su FK en tabla_b
query:     SELECT COUNT(*) FROM ${tabla_a} a WHERE EXISTS (SELECT 1 FROM ${tabla_b} b WHERE b.id = a.fk_id)
reference: SELECT COUNT(*) FROM ${tabla_a}
table_names: [tabla_a, tabla_b]
```

**Timeliness (frescura del dato)**:
```sql
-- registro cargado en las últimas 24h
query:     SELECT COUNT(*) FROM ${tabla} WHERE fecha_carga >= CURRENT_DATE - INTERVAL '1 day'
reference: SELECT COUNT(*) FROM ${tabla}
```

**Accuracy (veracidad y precisión)**:
```sql
-- importe coincide con el sumatorio de sus desglose (ejemplo de check de cuadre)
query:     SELECT COUNT(*) FROM ${tabla_cabecera} c WHERE total_importe = (SELECT SUM(sub_importe) FROM ${tabla_detalle} d WHERE d.parent_id = c.id)
reference: SELECT COUNT(*) FROM ${tabla_cabecera}
table_names: [tabla_cabecera, tabla_detalle]
```

### 3.3 Directrices de diseño

- **NUNCA usar el min/max actual de los datos como umbrales de validity**. Los umbrales deben basarse en lógica de negocio (un importe puede ser -1 hoy pero no debería ser válido). Si no conoces el rango válido, preguntar al usuario o usar un umbral conservador
- **Para enumerados**: usar los valores del EDA previo solo si el modelo confia en que son exhaustivos. Si hay duda, preguntar al usuario por los valores válidos
- **Completeness + columna siempre nula**: si el EDA previo muestra 100% nulos, informar al usuario y preguntar si de todas formas quiere la regla (podria ser un campo que aún no se usa)
- **Uniqueness + duplicados existentes**: si hay duplicados, la regla creara un KO inmediato. Informar al usuario del nivel actual antes de crear la regla

### 3.4 Configuración de Medición y Umbrales

Los parámetros `measurement_type`, `threshold_mode` y (`exact_threshold` o `threshold_breakpoints`) son **opcionales**. Si el usuario elige no configurar la medición, se aplican los valores por defecto: `measurement_type=percentage`, `threshold_mode=exact`, `exact_threshold={value: "100", equal_status: "OK", not_equal_status: "KO"}`. El plan siempre debe informar de la configuración de medición que se aplicara a cada regla (ver sección 4), y la pregunta de medición es obligatoria en el paso de aprobación — no asumir el default sin preguntar.

#### Flujo cuando el usuario pide configurar la medición

Si el usuario hace referencia a medir la calidad, configurar umbrales, o pide un tipo de medición concreto:

1. **Presentar las 4 opciones** de medición disponibles (ver tabla de tipos más abajo) con descripción clara
2. **Recoger la elección** del usuario: tipo de medición (`percentage`/`count`) + modo de umbral (`exact`/`range`)
3. **Si elige `exact`**: preguntar el valor exacto y los estados (ej: "¿=100% es OK y !=100% es KO?")
4. **Si elige `range`**: preguntar cuantos niveles (2 o 3) y los valores de corte con sus estados
5. **Confirmar la configuración completa** antes de aplicarla a la regla

No asumir la configuración de medición — siempre iterar con el usuario hasta que quede clara.

#### Tipos de medición disponibles

| Tipo | `measurement_type` | `threshold_mode` | Descripción |
|------|-------------------|-----------------|-------------|
| Valor exacto (%) | `percentage` | `exact` | Compara query/reference como porcentaje, evalúa con valor exacto |
| Valor exacto (conteo) | `count` | `exact` | Usa conteo absoluto de la query, evalúa con valor exacto |
| Rangos (%) | `percentage` | `range` | Compara query/reference como porcentaje, evalúa con rangos |
| Rangos (conteo) | `count` | `range` | Usa conteo absoluto de la query, evalúa con rangos |

**Comportamiento por defecto** (sin parámetros): `measurement_type=percentage`, `threshold_mode=exact`, `exact_threshold={value: "100", equal_status: "OK", not_equal_status: "KO"}`.

#### Directrices para sugerir el tipo de medición

Si el usuario pide recomendación o no tiene claro que tipo de medición usar, estas orientaciones pueden ayudar a guiar la conversación:

| Dimensión / Caso | Tipo recomendado | Razon |
|------------------|-----------------|-------|
| Completeness, Uniqueness, Validity, Consistency | `percentage` + `exact` (=100% OK) | Se espera paso total; cualquier fallo es KO (**este es el default**) |
| Timeliness (frescura) | `count` + `exact` | El resultado se mide en número absoluto de registros recientes |
| Reglas con tolerancia explícita del usuario | `percentage` + `range` (2-3 niveles) | Solo si el usuario pide explícitamente un rango WARNING intermedio |
| Reglas con umbral de conteo absoluto | `count` + `range` | Cuando los limites se expresan en cantidad de registros, no en porcentaje |

Son orientaciones para sugerir al usuario — la decisión final es siempre del usuario. Si el usuario indica explícitamente un tipo de medición, usar ese. **Por defecto, siempre usar medición exacta (=100% OK / !=100% KO) salvo que el usuario pida otra cosa.**

#### Ejemplos completos de parámetros de medición

Cada ejemplo muestra los parámetros tal como deben pasarse a `create_quality_rule`:

**Ejemplo 1 — Exact percentage (=100% OK / !=100% KO) [DEFAULT]:**
```json
measurement_type: "percentage"
threshold_mode: "exact"
exact_threshold: {"value": "100", "equal_status": "OK", "not_equal_status": "KO"}
```

**Ejemplo 2 — Exact count (=0 registros fallidos OK):**
```json
measurement_type: "count"
threshold_mode: "exact"
exact_threshold: {"value": "0", "equal_status": "OK", "not_equal_status": "KO"}
```

**Ejemplo 3 — Range percentage 3 niveles (<=50% KO, >50-80% WARNING, >80% OK):**
```json
measurement_type: "percentage"
threshold_mode: "range"
threshold_breakpoints: [
  {"value": "50", "status": "KO"},
  {"value": "80", "status": "WARNING"},
  {"status": "OK"}
]
```

**Ejemplo 4 — Range percentage 2 niveles (<=90% KO, >90% OK):**
```json
measurement_type: "percentage"
threshold_mode: "range"
threshold_breakpoints: [
  {"value": "90", "status": "KO"},
  {"status": "OK"}
]
```

**Ejemplo 5 — Range count (<=50 KO, >50-100 WARNING, >100 OK):**
```json
measurement_type: "count"
threshold_mode: "range"
threshold_breakpoints: [
  {"value": "50", "status": "KO"},
  {"value": "100", "status": "WARNING"},
  {"status": "OK"}
]
```

**Requisitos**: al menos una entrada con `status: "OK"` y una con `status: "KO"`. `WARNING` es opcional. En `threshold_breakpoints`, las entradas deben estar ordenadas de menor a mayor valor, y la última entrada no lleva `value` (rango abierto).

## 3.5 Validación de SQL (OBLIGATORIO)

Antes de presentar el plan al usuario, se debe verificar la validez técnica de las queries diseñadas.

**Procedimiento de validación:**
1. Para cada regla diseñada, preparar la `query` y la `query_reference`.
2. Resolver los placeholders `${tabla}` sustituyéndolos por el nombre real de la tabla.
3. Ejecutar ambas queries usando `execute_sql(query=[sql], limit=1)`.
4. Si alguna query devuelve error:
   - Revisar la sintaxis SQL.
   - Ajustar el diseño de la regla.
   - Re-validar hasta que ambas queries sean exitosas.
5. Con ambas queries exitosas, calcular el resultado y el estado de la regla:
   - Obtener `query_val` (valor numérico de `query`) y `query_ref_val` (valor numérico de `query_reference`).
   - Si `measurement_type = "percentage"`: `result = (query_val / query_ref_val) * 100` redondeado a 2 decimales. Si `query_ref_val == 0`, anotar `SIN_DATOS` (no dividir).
   - Si `measurement_type = "count"`: `result = query_val`.
   - Evaluar el estado según `threshold_mode`:
     - `"exact"`: si `result == exact_threshold.value` → `equal_status`; si no → `not_equal_status`.
     - `"range"`: recorrer `threshold_breakpoints` en orden ascendente; para el primer punto cuyo `value >= result`, usar ese `status`; si `result` supera todos los puntos con valor, usar el `status` del último punto (rango abierto, sin `value`).
   - El estado calculado (`OK`, `KO`, `WARNING` o `SIN_DATOS`) se incluye en el campo **Resultado de validación** del plan (ver sección 4).

Solo las reglas cuyas queries hayan sido validadas correctamente pueden formar parte del plan presentado al usuario.

---

## Flujo B: Regla Concreta

Este flujo aplica cuando el usuario describe directamente una regla que quiere crear, sin necesidad de una evaluación de cobertura previa. El objetivo es diseñar, validar y crear esa regla concreta con aprobación humana.

### B.1 Scope y Metadata

1. **Identificar dominio y tablas**: a partir de la descripción del usuario, determinar el `domain_name` y las tablas involucradas. Si no están claros, preguntar.
2. **Obtener metadata en paralelo**:
   ```
   Paralelo:
     A. get_table_columns_details(domain_name, tabla)  [por cada tabla involucrada]
     B. get_tables_details(domain_name, [tablas])
     C. get_quality_rule_dimensions(collection_name=domain_name)
     D. quality_rules_metadata(domain_name=domain_name)  <-- solo si no se ejecutó antes
   ```
   **Nota sobre `quality_rules_metadata`**: actualiza la metadata AI de las reglas existentes (descripción, dimensión). Se ejecuta sin `force_update` — solo procesa reglas sin metadata o modificadas, lo que cubre reglas creadas fuera de este agente. Si falla, continuar sin bloquear.
3. **Verificar existencia**: confirmar que las tablas y columnas mencionadas por el usuario existen en el dominio. Si alguna no existe, informar y preguntar.

### B.2 Diseñar la Regla

Con la metadata obtenida y la descripción del usuario, diseñar la regla:

- **`dimension`**: elegir la dimensión más adecuada según la naturaleza de la regla (completeness, validity, consistency, etc.). Usar las definiciones del dominio obtenidas en B.1.
- **`query`**: SQL que cuenta los registros que PASAN el check. Para las partes que involucren tablas gobernadas, usar `generate_sql` para obtener los nombres correctos de tablas/columnas. Para lógica de negocio específica (joins, condiciones complejas), construir el SQL manualmente respetando los nombres resueltos.
- **`query_reference`**: SQL que cuenta el total de registros (denominador).
- **`rule_name`**: seguir la convención `dq-[tabla]-[dimension]-[descripcion]` en kebab-case.
- **`description`**: descripción en lenguaje natural de forma concisa y en términos claros de negocio (sin jerga técnica) que comprueba esta regla, describiendo el resultado esperado. Aplicar las mismas reglas obligatorias que en la sección 3.1: no incluir scheduling, no usar nombres técnicos de columnas, no mencionar la dimensión — usar la definición semántica del campo.

Seguir las directrices de diseño de la sección 3.3 y los patrones SQL de la sección 3.2.

### B.3 Validación SQL (OBLIGATORIO)

Igual que en la sección 3.5:
1. Resolver los placeholders `${tabla}` por el nombre real de la tabla.
2. Ejecutar `query` y `query_reference` con `execute_sql(query=[sql], limit=1)`.
3. Si alguna query falla, revisar y corregir hasta que ambas sean exitosas.
4. Calcular el resultado y el estado de la regla aplicando la lógica del paso 5 de la sección 3.5 (measurement_type, threshold_mode y umbrales configurados).
5. **Informar del resultado al usuario** incluyendo el estado calculado. Ejemplos:
   - Percentage exact: "la query devuelve 45.000 de 45.230 totales → 99,5% → KO (umbral: =100% OK)"
   - Count exact: "la query devuelve 0 registros → OK (umbral: =0 OK)"
   - Range: "la query devuelve 72% → WARNING (rango: <=50% KO, >50-80% WARNING, >80% OK)"
   - Sin datos: "query_reference devuelve 0 registros → SIN_DATOS"

Tras informar del resultado, continuar directamente con la sección 4 (Presentar Plan y Esperar Aprobación). En el flujo B, el plan contendrá típicamente una sola regla. Incluir el resultado de la validación SQL con el estado calculado en la presentación.

**Nota**: Tras la creación de la regla (sección 5), se generará automáticamente metadata AI vía `quality_rules_metadata`.

---

## 4. PAUSA: Presentar Plan y Esperar Aprobación

Antes de ejecutar ninguna llamada a `create_quality_rule`, presentar el plan completo al usuario.

**Nota para Flujo B (regla concreta)**: El plan contendrá típicamente una sola regla. Incluir además el resultado de la validación SQL con el estado calculado (OK/KO/WARNING/SIN_DATOS).

### Formato del plan

```markdown
## Plan de Creación de Reglas de Calidad

**Dominio**: [domain_name]
**Tablas afectadas**: [lista]
**Reglas a crear**: N

---

### Regla 1: dq-account-completeness-id
- **Tabla**: account
- **Dimensión**: completeness
- **Columna**: id
- **Descripción**: Validates that every account record has a non-null primary identifier, ensuring data integrity across the system
- **SQL (registros que pasan)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL`
- **SQL (total)**: `SELECT COUNT(*) FROM ${account}`
- **Medición**: Porcentaje, valor exacto — =100% OK, !=100% KO
- **Justificación**: La columna id es la clave primaria de la tabla. Un nulo en este campo indica un registro corrupto que rompe la integridad referencial.
- **Resultado de validación**: 45.230 de 45.230 registros pasan → 100,0% → OK

### Regla 2: dq-account-uniqueness-id
[...]
```

**Nota sobre el campo de resultado**:
- **Flujo B** (regla concreta): usar siempre `**Resultado de validación**` con el valor real obtenido de las queries. Formato: `[query_val] de [query_ref_val] registros pasan → [result]% → [ESTADO]` (percentage) o `[query_val] registros → [ESTADO]` (count).
- **Flujo A** (con EDA previo): si el EDA ya aportaba datos de situación actual, combinar ambos en un campo único. Formato: `**Situación actual** (EDA previo): 0 nulos de 45.230 registros; **validación SQL**: 45.230 de 45.230 pasan → 100,0% → OK`.
- Si `query_reference` devuelve 0: `**Resultado de validación**: SIN_DATOS — query_reference devuelve 0 registros`.

---

```
¿Procedo con la creación de estas N reglas?

La medición de cada regla se indica en el campo **Medición** del plan. Si quieres cambiar la forma de medir alguna regla, indícalo antes de aprobar.

Además, ¿quieres programar la ejecución automática de las reglas?
1. Sí, con la misma planificación para todas las reglas
2. Sí, con planificación distinta por regla (o solo para algunas)
3. No, crear las reglas sin planificación (ejecución manual)

¿Quieres configurar la medición de las reglas?
1. Sí, quiero configurar cómo se miden (te preguntaré los detalles)
2. No, usar la medición por defecto (porcentaje, valor exacto: =100% OK / !=100% KO)
```

### Interpretación de la respuesta del usuario

**Aprobación sin elegir opción de scheduling ni medición** → Si el usuario simplemente dice "si", "adelante", "procede" u otra señal de aprobación sin elegir opción de scheduling ni responder la pregunta de medición, NO crear las reglas todavia. Preguntar explícitamente ambas cosas antes de continuar:

```
Antes de proceder, necesito saber:

1. **Planificación**: ¿quieres programar la ejecución automática?
   1. Sí, con la misma planificación para todas las reglas
   2. Sí, con planificación distinta por regla (o solo para algunas)
   3. No, ejecución manual

2. **Medición**: ¿quieres configurar cómo se miden las reglas?
   1. Sí, quiero configurar cómo se miden (te preguntaré los detalles)
   2. No, usar la medición por defecto (porcentaje, valor exacto: =100% OK / !=100% KO)
```

**Aprobación + opción 3 de scheduling + opción 2 de medición (ambas indicadas explícitamente)** → Crear las reglas sin parámetros de scheduling ni medición personalizada.

**Aprobación + opción 1** → Antes de crear las reglas, recopilar los parámetros de scheduling una vez para todas:

- `cron_expression` (obligatorio): preguntar en lenguaje natural si el usuario no conoce el formato Quartz ("¿cada cuánto quieres que se ejecute?") y generar la expresión equivalente. Orientar con ejemplos:
  - Diariamente a las 9:00 → `0 0 9 * * ?`
  - Cada lunes a las 9:00 → `0 0 9 ? * MON`
  - Primer día de cada mes a las 9:00 → `0 0 9 1 * ?`
- `cron_start_datetime` (opcional): preguntar "¿Cuándo quieres que empiece a ejecutarse? (deja en blanco para que empiece inmediatamente)". Si el usuario indica una fecha/hora en lenguaje natural, convertirla a ISO 8601. Ejemplo: `2026-04-01T09:00:00`
- `cron_timezone`: **NO preguntar** salvo que el usuario mencione otra zona horaria. Usar `Europe/Madrid` por defecto.

Si el usuario proporciona los detalles del cron en la misma respuesta de aprobación (ej: "sí, opción 1, diariamente a las 9"), no preguntar de nuevo — usar directamente esos datos.

**Aprobación + opción 2** → Para cada regla (o bloque de reglas que el usuario quiera tratar igual), preguntar los mismos campos anteriores. Permitir que algunas reglas tengan scheduling y otras no.

**Configuración de medición (opción 1)** → Si el usuario elige configurar la medición, seguir el flujo de interacción de la sección 3.4: presentar las 4 opciones, recoger la elección, preguntar los detalles según el modo elegido (exact o range), y confirmar. Aplicar la configuración resultante a las reglas afectadas. Si el usuario elige opción 2 o no menciona medición, no pasar los parámetros de medición (usar defaults del tool).

**Cambio de medición** → Si el usuario pide cambiar la forma de medir una o varias reglas (ej: "quiero que la regla 1 use conteo en vez de porcentaje", "pon rangos de 3 niveles para todas"), ajustar los parámetros `measurement_type`, `threshold_mode` y/o `exact_threshold`/`threshold_breakpoints` de las reglas afectadas. Si el usuario describe los umbrales en lenguaje natural (ej: "KO por debajo del 80%, WARNING entre 80-95%, OK por encima del 95%"), traducirlos al formato `threshold_breakpoints` correspondiente (ver ejemplos completos en sección 3.4). Actualizar el campo **Medición** del plan y volver a presentar para aprobación.

**Rechazo** → No crear. Si el usuario modifica alguna regla, actualizar el plan y volver a presentar para aprobación.

### Formato del plan con medición personalizada (si aplica)

Si tras la respuesta del usuario alguna regla tiene medición personalizada (distinta del default), incluir en su bloque:
```markdown
- **Medición**: Conteo, rangos — <=50 KO, >50-100 WARNING, >100 OK
```

El campo **Medición** debe aparecer siempre en todas las reglas del plan, tanto con defaults como con valores personalizados. Formato: `[Porcentaje|Conteo], [valor exacto|rangos] — [detalle de umbrales]`.

### Formato del plan con scheduling (si aplica)

Si tras la respuesta del usuario alguna regla tiene planificación configurada, incluir en su bloque:
```markdown
- **Planificación**: `0 0 9 * * ?` — diariamente a las 9:00 (Europe/Madrid)
  - Primera ejecución: 2026-04-01T09:00:00
```

Reglas sin scheduling: no añadir ningún campo de planificación (ni "Sin planificación"). Si ninguna regla tiene scheduling, omitir completamente cualquier referencia a planificación.

### Señales de aprobación válidas

Cualquiera de estas respuestas (o equivalentes en el idioma del usuario) se consideran aprobación:
- "si", "sí", "s", "yes", "y"
- "procede", "adelante", "ok", "OK", "vale"
- "crea las reglas", "hazlo", "ejecuta"
- "apruebo", "aprobado", "confirmo"

### Señales de rechazo o modificación

- "no", "cancela", "para"
- "modifica la regla X"
- "quita la regla de Y"
- "cambia el umbral de Z"

Si el usuario modifica: actualizar el plan y volver a presentar para aprobación final.

## 5. Ejecución: Crear Reglas

Solo tras aprobación explícita, crear las reglas una a una:

```
Por cada regla aprobada (secuencial, NO en paralelo):
  1. Llamar create_quality_rule con los parámetros diseñados, incluyendo los opcionales
     de scheduling si se configuraron (cron_expression, cron_timezone, cron_start_datetime)
     y los de medición si el usuario los configuró (measurement_type, threshold_mode, y exact_threshold
     o threshold_breakpoints según el modo — pasar juntos tal como se muestran en los ejemplos de la sección 3.4)
  2. Reportar el resultado inmediatamente en el chat
  3. Si falla: indicar el error y continuar con la siguiente
```

**Por que secuencial y no en paralelo**: para reportar progreso en tiempo real y que el usuario pueda interrumpir si algo sale mal.

**Formato de reporte por regla** (añadir la planificación entre paréntesis cuando exista):
```
[OK]  dq-account-completeness-id — creada correctamente (planificada: diariamente a las 9:00)
[OK]  dq-account-uniqueness-id — creada correctamente
[ERR] dq-account-validity-amount — error: [mensaje del MCP]
[OK]  dq-card-completeness-card-id — creada correctamente (planificada: cada lunes a las 9:00, desde 2026-04-01)
```

### 5.1 Generar Metadata para Reglas Creadas

Tras crear todas las reglas (exitosas o no), ejecutar una única llamada para enriquecer las reglas recién creadas con metadata AI:

```
quality_rules_metadata(domain_name=domain_name)
```

Sin `force_update` — las reglas recién creadas no tendrán metadata aún, así que se procesarán automáticamente. Si falla, informar al usuario pero no bloquear el resumen final.

## 6. Resumen Final

Al terminar la creación, presentar resumen:

```markdown
## Resultado de Creación de Reglas

- Reglas creadas exitosamente: N/M
- Reglas fallidas: X/M
- Metadata AI generada: Si/No (indicar si la llamada a `quality_rules_metadata` fue exitosa)

### Cobertura antes y después

| Tabla | Cobertura anterior | Cobertura nueva |
|-------|-------------------|-----------------|
| account | ~30% | ~75% |
| card | ~50% | ~90% |

### Próximos pasos recomendados

- Ejecutar las reglas recién creadas para obtener un baseline de calidad
- [Si alguna regla tenía estado calculado KO en la validación SQL]: **PRIORIDAD — estas reglas ya muestran KO con el dato actual**: [lista de nombres]. El estado KO indica que los datos actuales no cumplen el umbral configurado; revisar si el umbral es correcto o si hay un problema de calidad real antes de ponerlas en producción.
- [Si alguna regla tenía estado calculado WARNING en la validación SQL]: revisar estas reglas, el dato actual está en zona de aviso: [lista de nombres].
- [Si quedan gaps]: considerar cubrir también [lista de gaps restantes]
```

Si hubo errores en la creación, indicar claramente qué reglas fallaron y sugerir acciones (reintentar, revisar el SQL, contactar con el administrador de la plataforma).

## 7. Pregunta de Continuación

Al finalizar, preguntar al usuario con opciones como quiere continuar, siguiendo la convención de preguntas al usuario:
- **Generar un informe formal con los resultados**
- **Crear otra regla concreta**
- **Evaluar la cobertura de otras tablas del dominio**
- **Finalizar**
