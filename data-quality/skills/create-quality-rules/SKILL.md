---
name: create-quality-rules
description: Disenar y crear reglas de calidad. Flujo A (gaps): cubrir gaps identificados por assess-quality. Flujo B (regla concreta): crear una regla especifica descrita por el usuario sin assess-quality previo. Ambos flujos requieren confirmacion humana obligatoria antes de ejecutar.
argument-hint: [dominio] [tabla (opcional)]
---

# Skill: Creacion de Reglas de Calidad

Workflow para disenar, proponer y crear reglas de calidad con aprobacion humana. Esta skill tiene un prerequisito obligatorio y una pausa de aprobacion critica.

## PREREQUISITO

Esta skill tiene dos flujos de entrada con prerequisitos distintos:

**Flujo A — Gaps (requiere assess-quality):**
El usuario quiere cubrir gaps de cobertura (ej: "crea reglas para el dominio X", "completa la cobertura de la tabla Y"). Antes de ejecutar este flujo, debe existir una evaluacion de cobertura previa (skill `assess-quality`). Si no se ha ejecutado en la conversacion actual:
1. Indicar al usuario que primero es necesario evaluar la cobertura
2. Ejecutar la skill `assess-quality` con el mismo scope
3. Continuar con este flujo una vez completada la evaluacion

**Flujo B — Regla concreta (NO requiere assess-quality):**
El usuario describe una regla especifica que quiere crear (ej: "crea una regla que verifique que todo cliente en tabla A existe en tabla B", "quiero una regla de validity que compruebe que el importe es positivo en transactions"). En este caso, NO es necesario ejecutar `assess-quality` previamente — ir directamente a la seccion "Flujo B: Regla Concreta" mas adelante.

## PAUSA DE APROBACION CRITICA

**NUNCA llamar `create_quality_rule` sin que el usuario haya confirmado explicitamente el plan.**

Esta pausa es el paso mas importante de toda la skill. Si hay dudas sobre si el usuario ha aprobado, preguntar de nuevo. No interpretar silencio ni respuestas ambiguas como aprobacion.

**La pregunta de scheduling esta integrada en la seccion 4 (aprobacion).** No es un paso separado — se presenta junto con la peticion de confirmacion para que sea imposible omitirla.

**Cada invocacion de esta skill es independiente.** Una aprobacion dada anteriormente en la misma conversacion NO es valida para un nuevo lote de reglas. Aunque el usuario ya haya aprobado un plan anterior, siempre se debe seguir el paso 4 de nuevo desde cero.

---

## 1. Determinar Tablas con Gaps

A partir del resultado de `assess-quality`, recuperar el inventario de reglas existentes obtenido via `get_tables_quality_details`. Este inventario es la fuente de verdad: **solo diseñar reglas para dimensiones/columnas que NO estén ya cubiertas por una regla existente**.

Identificar:
- Que tablas tienen gaps de cobertura (dimensiones esperadas no cubiertas por ninguna regla existente)
- Que dimensiones faltan en cada tabla (considerando tanto las estandar como las especificas del dominio)
- Cuales son los gaps prioritarios basandose en el EDA previo de `profile_data`

**Sobre dimensiones**: las definiciones del dominio (obtenidas en `assess-quality` via `get_quality_rule_dimensions`) prevalecen siempre sobre las estándar. Ver sección 2 de `skills-guides/exploration.md`.

Si el usuario ha especificado un subset ("solo la tabla account"), respetar esa restriccion.

Si hay reglas existentes en estado KO o WARNING: mencionarlas como accion prioritaria antes de crear nuevas. Preguntar si quiere resolver primero esas o continuar con los gaps.

## 2. Diseño de Reglas (a partir del análisis completo de assess-quality)

`assess-quality` ya ha producido dos fuentes de información que se usan aquí directamente — no repetir ninguna llamada MCP salvo que el scope haya cambiado:

**Fuente 1 — Análisis semántico** (de `get_tables_details` + `get_table_columns_details`):
El análisis semántico de `assess-quality` determinó *por qué* cada columna necesita cada dimensión: rol de la columna (clave, métrica, estado, FK…), obligatoriedad según negocio, restricciones documentadas en la gobernanza. Ese razonamiento es la justificación de cada regla. Recuperarlo y usarlo como base para la descripción y el diseño del SQL.

**Nota para dominios tecnicos**: Si el dominio es tecnico, las descripciones de negocio pueden ser limitadas o inexistentes. En ese caso, dar mayor peso al EDA y razonar por nombres/tipos de columnas (convenciones como `*_id`, `*_date`, `*_amount`). Validar con el usuario las asunciones sobre semantica antes de disenar reglas de `validity` (rangos, enumerados).

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

## 3. Diseno de Reglas

Para cada gap identificado, disenar la regla de calidad correspondiente.

### 3.1 Estructura de una regla

Cada regla tiene los siguientes campos:
- `rule_name`: nombre descriptivo en kebab-case. Convencion: `dq-[tabla]-[dimension]-[columna-o-descripcion]`
- `primary_table`: tabla principal a la que pertenece la regla
- `table_names`: lista de tablas referenciadas en los SQLs (incluir primary_table siempre)
- `description`: descripcion en lenguaje natural de forma concisa y en terminos claros de negocio (sin jerga tecnica) que comprueba esta regla, describiendo el resultado esperado. **Reglas obligatorias**: (1) NO incluir informacion de planificacion ni scheduling (frecuencia, horarios, cron). (2) NO usar nombres tecnicos de columnas (como `card_id`, `district_id`); en su lugar, usar la definicion semantica/de negocio del campo obtenida de `get_table_columns_details`. (3) NO mencionar la dimension de la regla (completeness, uniqueness, validity, etc.) — la dimension ya es un campo separado. Ejemplo correcto: "Validates that every account record has a non-null district identifier, ensuring all accounts are assigned to a district". Ejemplo incorrecto: "Completeness check: Checks that district_id is never null. Scheduled daily at 09:00"
- `query`: SQL que cuenta los registros que PASAN el check (numerador)
- `query_reference`: SQL que cuenta el total de registros (denominador)
- `dimension`: completeness / uniqueness / validity / consistency
- `collection_name`: el domain_name del dominio
- `measurement_type`: (opcional) como se mide el resultado de calidad. Valores posibles:
  - `percentage` (por defecto): compara query vs query_reference como porcentaje
  - `count`: usa el conteo absoluto de registros de la query
- `threshold_mode`: (opcional) como se definen los umbrales de evaluacion. Valores posibles:
  - `exact` (por defecto): valor exacto con operadores `=` y `!=`
  - `range`: rangos con operadores como `>`, `<=`
- `exact_threshold`: (opcional, solo para `threshold_mode=exact`) objeto con:
  - `value`: valor de comparacion (ej: `"100"`, `"0"`)
  - `equal_status`: estado cuando resultado = value (`OK`, `KO`, o `WARNING`)
  - `not_equal_status`: estado cuando resultado != value (`OK`, `KO`, o `WARNING`)
  - Default: `{value: "100", equal_status: "OK", not_equal_status: "KO"}`
- `threshold_breakpoints`: (opcional, solo para `threshold_mode=range`) lista ordenada ascendente de puntos de corte. Cada entrada tiene:
  - `value`: limite superior del intervalo (ej: `"50"`, `"80"`)
  - `status`: estado para ese intervalo (`OK`, `KO`, o `WARNING`)
  - La **ultima entrada** NO lleva `value` (rango abierto hacia arriba); solo `status`
  - Minimo 2 entradas, al menos una `OK` y una `KO`. Ver seccion 3.4
- `cron_expression`: (opcional) expresion Quartz cron para ejecucion automatica. Si no se indica, la regla no se planifica
- `cron_timezone`: (opcional) timezone del cron; si hay cron y no se especifica, usar `Europe/Madrid`
- `cron_start_datetime`: (opcional) ISO 8601 con la primera ejecucion programada; si no se indica, la planificacion empieza inmediatamente tras la creacion

### 3.2 Patrones SQL por dimension

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

**Validity (rango numerico)**:
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

### 3.3 Directrices de diseno

- **NUNCA usar el min/max actual de los datos como umbrales de validity**. Los umbrales deben basarse en logica de negocio (un importe puede ser -1 hoy pero no deberia ser valido). Si no conoces el rango valido, preguntar al usuario o usar un umbral conservador
- **Para enumerados**: usar los valores del EDA previo solo si el modelo confia en que son exhaustivos. Si hay duda, preguntar al usuario por los valores validos
- **Completeness + columna siempre nula**: si el EDA previo muestra 100% nulos, informar al usuario y preguntar si de todas formas quiere la regla (podria ser un campo que aun no se usa)
- **Uniqueness + duplicados existentes**: si hay duplicados, la regla creara un KO inmediato. Informar al usuario del nivel actual antes de crear la regla

### 3.4 Configuracion de Medicion y Umbrales

Los parametros `measurement_type`, `threshold_mode` y (`exact_threshold` o `threshold_breakpoints`) son **opcionales**. Si el usuario no los especifica, se aplican los valores por defecto: `measurement_type=percentage`, `threshold_mode=exact`, `exact_threshold={value: "100", equal_status: "OK", not_equal_status: "KO"}`. No es necesario preguntar al usuario. Sin embargo, el plan siempre debe informar de la configuracion de medicion que se aplicara a cada regla (ver seccion 4).

#### Flujo cuando el usuario pide configurar la medicion

Si el usuario hace referencia a medir la calidad, configurar umbrales, o pide un tipo de medicion concreto:

1. **Presentar las 4 opciones** de medicion disponibles (ver tabla de tipos mas abajo) con descripcion clara
2. **Recoger la eleccion** del usuario: tipo de medicion (`percentage`/`count`) + modo de umbral (`exact`/`range`)
3. **Si elige `exact`**: preguntar el valor exacto y los estados (ej: "¿=100% es OK y !=100% es KO?")
4. **Si elige `range`**: preguntar cuantos niveles (2 o 3) y los valores de corte con sus estados
5. **Confirmar la configuracion completa** antes de aplicarla a la regla

No asumir la configuracion de medicion — siempre iterar con el usuario hasta que quede clara.

#### Tipos de medicion disponibles

| Tipo | `measurement_type` | `threshold_mode` | Descripcion |
|------|-------------------|-----------------|-------------|
| Valor exacto (%) | `percentage` | `exact` | Compara query/reference como porcentaje, evalua con valor exacto |
| Valor exacto (conteo) | `count` | `exact` | Usa conteo absoluto de la query, evalua con valor exacto |
| Rangos (%) | `percentage` | `range` | Compara query/reference como porcentaje, evalua con rangos |
| Rangos (conteo) | `count` | `range` | Usa conteo absoluto de la query, evalua con rangos |

**Comportamiento por defecto** (sin parametros): `measurement_type=percentage`, `threshold_mode=exact`, `exact_threshold={value: "100", equal_status: "OK", not_equal_status: "KO"}`.

#### Directrices para sugerir el tipo de medicion

Si el usuario pide recomendacion o no tiene claro que tipo de medicion usar, estas orientaciones pueden ayudar a guiar la conversacion:

| Dimension / Caso | Tipo recomendado | Razon |
|------------------|-----------------|-------|
| Completeness, Uniqueness, Validity, Consistency | `percentage` + `exact` (=100% OK) | Se espera paso total; cualquier fallo es KO (**este es el default**) |
| Timeliness (frescura) | `count` + `exact` | El resultado se mide en numero absoluto de registros recientes |
| Reglas con tolerancia explicita del usuario | `percentage` + `range` (2-3 niveles) | Solo si el usuario pide explicitamente un rango WARNING intermedio |
| Reglas con umbral de conteo absoluto | `count` + `range` | Cuando los limites se expresan en cantidad de registros, no en porcentaje |

Son orientaciones para sugerir al usuario — la decision final es siempre del usuario. Si el usuario indica explicitamente un tipo de medicion, usar ese. **Por defecto, siempre usar medicion exacta (=100% OK / !=100% KO) salvo que el usuario pida otra cosa.**

#### Ejemplos completos de parametros de medicion

Cada ejemplo muestra los parametros tal como deben pasarse a `create_quality_rule`:

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

**Requisitos**: al menos una entrada con `status: "OK"` y una con `status: "KO"`. `WARNING` es opcional. En `threshold_breakpoints`, las entradas deben estar ordenadas de menor a mayor valor, y la ultima entrada no lleva `value` (rango abierto).

## 3.5 Validacion de SQL (OBLIGATORIO)

Antes de presentar el plan al usuario, se debe verificar la validez tecnica de las queries diseñadas.

**Procedimiento de validacion:**
1. Para cada regla diseñada, preparar la `query` y la `query_reference`.
2. Resolver los placeholders `${tabla}` sustituyendolos por el nombre real de la tabla.
3. Ejecutar ambas queries usando `execute_sql(query=[sql], limit=1)`.
4. Si alguna query devuelve error:
   - Revisar la sintaxis SQL.
   - Ajustar el diseño de la regla.
   - Re-validar hasta que ambas queries sean exitosas.
5. Con ambas queries exitosas, calcular el resultado y el estado de la regla:
   - Obtener `query_val` (valor numerico de `query`) y `query_ref_val` (valor numerico de `query_reference`).
   - Si `measurement_type = "percentage"`: `result = (query_val / query_ref_val) * 100` redondeado a 2 decimales. Si `query_ref_val == 0`, anotar `SIN_DATOS` (no dividir).
   - Si `measurement_type = "count"`: `result = query_val`.
   - Evaluar el estado segun `threshold_mode`:
     - `"exact"`: si `result == exact_threshold.value` → `equal_status`; si no → `not_equal_status`.
     - `"range"`: recorrer `threshold_breakpoints` en orden ascendente; para el primer punto cuyo `value >= result`, usar ese `status`; si `result` supera todos los puntos con valor, usar el `status` del ultimo punto (rango abierto, sin `value`).
   - El estado calculado (`OK`, `KO`, `WARNING` o `SIN_DATOS`) se incluye en el campo **Resultado de validacion** del plan (ver seccion 4).

Solo las reglas cuyas queries hayan sido validadas correctamente pueden formar parte del plan presentado al usuario.

---

## Flujo B: Regla Concreta

Este flujo aplica cuando el usuario describe directamente una regla que quiere crear, sin necesidad de `assess-quality` previo. El objetivo es disenar, validar y crear esa regla concreta con aprobacion humana.

### B.1 Scope y Metadata

1. **Identificar dominio y tablas**: a partir de la descripcion del usuario, determinar el `domain_name` y las tablas involucradas. Si no estan claros, preguntar.
2. **Obtener metadata en paralelo**:
   ```
   Paralelo:
     A. get_table_columns_details(domain_name, tabla)  [por cada tabla involucrada]
     B. get_tables_details(domain_name, [tablas])
     C. get_quality_rule_dimensions(collection_name=domain_name)
   ```
3. **Verificar existencia**: confirmar que las tablas y columnas mencionadas por el usuario existen en el dominio. Si alguna no existe, informar y preguntar.

### B.2 Disenar la Regla

Con la metadata obtenida y la descripcion del usuario, disenar la regla:

- **`dimension`**: elegir la dimension mas adecuada segun la naturaleza de la regla (completeness, validity, consistency, etc.). Usar las definiciones del dominio obtenidas en B.1.
- **`query`**: SQL que cuenta los registros que PASAN el check. Para las partes que involucren tablas gobernadas, usar `generate_sql` para obtener los nombres correctos de tablas/columnas. Para logica de negocio especifica (joins, condiciones complejas), construir el SQL manualmente respetando los nombres resueltos.
- **`query_reference`**: SQL que cuenta el total de registros (denominador).
- **`rule_name`**: seguir la convencion `dq-[tabla]-[dimension]-[descripcion]` en kebab-case.
- **`description`**: descripcion en lenguaje natural de forma concisa y en terminos claros de negocio (sin jerga tecnica) que comprueba esta regla, describiendo el resultado esperado. Aplicar las mismas reglas obligatorias que en la seccion 3.1: no incluir scheduling, no usar nombres tecnicos de columnas, no mencionar la dimension — usar la definicion semantica del campo.

Seguir las directrices de diseno de la seccion 3.3 y los patrones SQL de la seccion 3.2.

### B.3 Validacion SQL (OBLIGATORIO)

Igual que en la seccion 3.5:
1. Resolver los placeholders `${tabla}` por el nombre real de la tabla.
2. Ejecutar `query` y `query_reference` con `execute_sql(query=[sql], limit=1)`.
3. Si alguna query falla, revisar y corregir hasta que ambas sean exitosas.
4. Calcular el resultado y el estado de la regla aplicando la logica del paso 5 de la seccion 3.5 (measurement_type, threshold_mode y umbrales configurados).
5. **Informar del resultado al usuario** incluyendo el estado calculado. Ejemplos:
   - Percentage exact: "la query devuelve 45.000 de 45.230 totales → 99,5% → KO (umbral: =100% OK)"
   - Count exact: "la query devuelve 0 registros → OK (umbral: =0 OK)"
   - Range: "la query devuelve 72% → WARNING (rango: <=50% KO, >50-80% WARNING, >80% OK)"
   - Sin datos: "query_reference devuelve 0 registros → SIN_DATOS"

Tras informar del resultado, continuar directamente con la seccion 4 (Presentar Plan y Esperar Aprobacion). En el flujo B, el plan contendra tipicamente una sola regla. Incluir el resultado de la validacion SQL con el estado calculado en la presentacion.

**Nota**: Tras la creacion de la regla (seccion 5), se generara automaticamente metadata AI via `quality_rules_metadata`.

---

## 4. PAUSA: Presentar Plan y Esperar Aprobacion

Antes de ejecutar ninguna llamada a `create_quality_rule`, presentar el plan completo al usuario.

**Nota para Flujo B (regla concreta)**: El plan contendra tipicamente una sola regla. Incluir ademas el resultado de la validacion SQL con el estado calculado (OK/KO/WARNING/SIN_DATOS).

### Formato del plan

```markdown
## Plan de Creacion de Reglas de Calidad

**Dominio**: [domain_name]
**Tablas afectadas**: [lista]
**Reglas a crear**: N

---

### Regla 1: dq-account-completeness-id
- **Tabla**: account
- **Dimension**: completeness
- **Columna**: id
- **Descripcion**: Validates that every account record has a non-null primary identifier, ensuring data integrity across the system
- **SQL (registros que pasan)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL`
- **SQL (total)**: `SELECT COUNT(*) FROM ${account}`
- **Medicion**: Porcentaje, valor exacto — =100% OK, !=100% KO
- **Justificacion**: La columna id es la clave primaria de la tabla. Un nulo en este campo indica un registro corrupto que rompe la integridad referencial.
- **Resultado de validacion**: 45.230 de 45.230 registros pasan → 100,0% → OK

### Regla 2: dq-account-uniqueness-id
[...]
```

**Nota sobre el campo de resultado**:
- **Flujo B** (regla concreta): usar siempre `**Resultado de validacion**` con el valor real obtenido de las queries. Formato: `[query_val] de [query_ref_val] registros pasan → [result]% → [ESTADO]` (percentage) o `[query_val] registros → [ESTADO]` (count).
- **Flujo A** (con EDA previo): si el EDA ya aportaba datos de situacion actual, combinar ambos en un campo unico. Formato: `**Situacion actual** (EDA previo): 0 nulos de 45.230 registros; **validacion SQL**: 45.230 de 45.230 pasan → 100,0% → OK`.
- Si `query_reference` devuelve 0: `**Resultado de validacion**: SIN_DATOS — query_reference devuelve 0 registros`.

---

¿Procedo con la creacion de estas N reglas?

La medicion de cada regla se indica en el campo **Medicion** del plan. Si quieres cambiar la forma de medir alguna regla, indicalo antes de aprobar.

Ademas, ¿quieres programar la ejecucion automatica de las reglas?
1. Si, con la misma planificacion para todas las reglas
2. Si, con planificacion distinta por regla (o solo para algunas)
3. No, crear las reglas sin planificacion (ejecucion manual)

¿Quieres configurar la medicion de las reglas?
1. Si, quiero configurar como se miden (te preguntare los detalles)
2. No, usar la medicion por defecto (porcentaje, valor exacto: =100% OK / !=100% KO)
```

### Interpretacion de la respuesta del usuario

**Aprobacion + opcion 3 (o aprobacion sin mencionar scheduling)** → Crear las reglas sin parametros de scheduling. Si el usuario simplemente dice "si", "adelante", "procede" u otra señal de aprobacion sin elegir opcion de scheduling, interpretar como opcion 3 (sin planificacion).

**Aprobacion + opcion 1** → Antes de crear las reglas, recopilar los parametros de scheduling una vez para todas:

- `cron_expression` (obligatorio): preguntar en lenguaje natural si el usuario no conoce el formato Quartz ("¿cada cuanto quieres que se ejecute?") y generar la expresion equivalente. Orientar con ejemplos:
  - Diariamente a las 9:00 → `0 0 9 * * ?`
  - Cada lunes a las 9:00 → `0 0 9 ? * MON`
  - Primer dia de cada mes a las 9:00 → `0 0 9 1 * ?`
- `cron_start_datetime` (opcional): preguntar "¿Cuando quieres que empiece a ejecutarse? (deja en blanco para que empiece inmediatamente)". Si el usuario indica una fecha/hora en lenguaje natural, convertirla a ISO 8601. Ejemplo: `2026-04-01T09:00:00`
- `cron_timezone`: **NO preguntar** salvo que el usuario mencione otra zona horaria. Usar `Europe/Madrid` por defecto.

Si el usuario proporciona los detalles del cron en la misma respuesta de aprobacion (ej: "si, opcion 1, diariamente a las 9"), no preguntar de nuevo — usar directamente esos datos.

**Aprobacion + opcion 2** → Para cada regla (o bloque de reglas que el usuario quiera tratar igual), preguntar los mismos campos anteriores. Permitir que algunas reglas tengan scheduling y otras no.

**Configuracion de medicion (opcion 1)** → Si el usuario elige configurar la medicion, seguir el flujo de interaccion de la seccion 3.4: presentar las 4 opciones, recoger la eleccion, preguntar los detalles segun el modo elegido (exact o range), y confirmar. Aplicar la configuracion resultante a las reglas afectadas. Si el usuario elige opcion 2 o no menciona medicion, no pasar los parametros de medicion (usar defaults del tool).

**Cambio de medicion** → Si el usuario pide cambiar la forma de medir una o varias reglas (ej: "quiero que la regla 1 use conteo en vez de porcentaje", "pon rangos de 3 niveles para todas"), ajustar los parametros `measurement_type`, `threshold_mode` y/o `exact_threshold`/`threshold_breakpoints` de las reglas afectadas. Si el usuario describe los umbrales en lenguaje natural (ej: "KO por debajo del 80%, WARNING entre 80-95%, OK por encima del 95%"), traducirlos al formato `threshold_breakpoints` correspondiente (ver ejemplos completos en seccion 3.4). Actualizar el campo **Medicion** del plan y volver a presentar para aprobacion.

**Rechazo** → No crear. Si el usuario modifica alguna regla, actualizar el plan y volver a presentar para aprobacion.

### Formato del plan con medicion personalizada (si aplica)

Si tras la respuesta del usuario alguna regla tiene medicion personalizada (distinta del default), incluir en su bloque:
```markdown
- **Medicion**: Conteo, rangos — <=50 KO, >50-100 WARNING, >100 OK
```

El campo **Medicion** debe aparecer siempre en todas las reglas del plan, tanto con defaults como con valores personalizados. Formato: `[Porcentaje|Conteo], [valor exacto|rangos] — [detalle de umbrales]`.

### Formato del plan con scheduling (si aplica)

Si tras la respuesta del usuario alguna regla tiene planificacion configurada, incluir en su bloque:
```markdown
- **Planificacion**: `0 0 9 * * ?` — diariamente a las 9:00 (Europe/Madrid)
  - Primera ejecucion: 2026-04-01T09:00:00
```

Reglas sin scheduling: no añadir ningun campo de planificacion (ni "Sin planificacion"). Si ninguna regla tiene scheduling, omitir completamente cualquier referencia a planificacion.

### Senales de aprobacion validas

Cualquiera de estas respuestas (o equivalentes en el idioma del usuario) se consideran aprobacion:
- "si", "sí", "s", "yes", "y"
- "procede", "adelante", "ok", "OK", "vale"
- "crea las reglas", "hazlo", "ejecuta"
- "apruebo", "aprobado", "confirmo"

### Senales de rechazo o modificacion

- "no", "cancela", "para"
- "modifica la regla X"
- "quita la regla de Y"
- "cambia el umbral de Z"

Si el usuario modifica: actualizar el plan y volver a presentar para aprobacion final.

## 5. Ejecucion: Crear Reglas

Solo tras aprobacion explicita, crear las reglas una a una:

```
Por cada regla aprobada (secuencial, NO en paralelo):
  1. Llamar create_quality_rule con los parametros disenados, incluyendo los opcionales
     de scheduling si se configuraron (cron_expression, cron_timezone, cron_start_datetime)
     y los de medicion si el usuario los configuro (measurement_type, threshold_mode, y exact_threshold
     o threshold_breakpoints segun el modo — pasar juntos tal como se muestran en los ejemplos de la seccion 3.4)
  2. Reportar el resultado inmediatamente en el chat
  3. Si falla: indicar el error y continuar con la siguiente
```

**Por que secuencial y no en paralelo**: para reportar progreso en tiempo real y que el usuario pueda interrumpir si algo sale mal.

**Formato de reporte por regla** (añadir la planificacion entre parentesis cuando exista):
```
[OK]  dq-account-completeness-id — creada correctamente (planificada: diariamente a las 9:00)
[OK]  dq-account-uniqueness-id — creada correctamente
[ERR] dq-account-validity-amount — error: [mensaje del MCP]
[OK]  dq-card-completeness-card-id — creada correctamente (planificada: cada lunes a las 9:00, desde 2026-04-01)
```

### 5.1 Generar Metadata para Reglas Creadas

Tras crear todas las reglas (exitosas o no), ejecutar una unica llamada para enriquecer las reglas recien creadas con metadata AI:

```
quality_rules_metadata(domain_name=domain_name)
```

Sin `force_update` — las reglas recien creadas no tendran metadata aun, asi que se procesaran automaticamente. Si falla, informar al usuario pero no bloquear el resumen final.

## 6. Resumen Final

Al terminar la creacion, presentar resumen:

```markdown
## Resultado de Creacion de Reglas

- Reglas creadas exitosamente: N/M
- Reglas fallidas: X/M
- Metadata AI generada: Si/No (indicar si la llamada a `quality_rules_metadata` fue exitosa)

### Cobertura antes y despues

| Tabla | Cobertura anterior | Cobertura nueva |
|-------|-------------------|-----------------|
| account | ~30% | ~75% |
| card | ~50% | ~90% |

### Proximos pasos recomendados

- Ejecutar las reglas recien creadas para obtener un baseline de calidad
- [Si alguna regla tenia estado calculado KO en la validacion SQL]: **PRIORIDAD — estas reglas ya muestran KO con el dato actual**: [lista de nombres]. El estado KO indica que los datos actuales no cumplen el umbral configurado; revisar si el umbral es correcto o si hay un problema de calidad real antes de ponerlas en produccion.
- [Si alguna regla tenia estado calculado WARNING en la validacion SQL]: revisar estas reglas, el dato actual esta en zona de aviso: [lista de nombres].
- [Si quedan gaps]: considerar cubrir tambien [lista de gaps restantes]
```

Si hubo errores en la creacion, indicar claramente que reglas fallaron y sugerir acciones (reintentar, revisar el SQL, contactar con el administrador de la plataforma).

## 7. Pregunta de Continuacion

Al finalizar, preguntar si quiere:
- Generar un informe con el resultado (activar skill `quality-report`)
- Crear otra regla concreta (volver al Flujo B)
- Evaluar otras tablas del dominio
- Finalizar
