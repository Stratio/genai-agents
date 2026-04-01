---
name: create-quality-planification
description: Crear una planificacion (schedule) para ejecutar automaticamente todas las reglas de calidad de una o varias carpetas/colecciones. Opera a nivel de carpeta (dominio/coleccion), no de regla individual. Requiere confirmacion humana obligatoria antes de ejecutar.
argument-hint: [dominio/coleccion] [frecuencia (opcional)]
---

# Skill: Creacion de Planificacion de Reglas de Calidad

Workflow para crear una planificacion que ejecute automaticamente todas las reglas de calidad contenidas en una o varias carpetas (colecciones/dominios) segun un calendario definido por el usuario.

## PAUSA DE APROBACION CRITICA

**NUNCA llamar `create_quality_rule_planification` sin que el usuario haya confirmado explicitamente el plan.**

Si hay dudas sobre si el usuario ha aprobado, preguntar de nuevo. No interpretar silencio ni respuestas ambiguas como aprobacion.

---

## 1. Determinacion de Scope

### 1.1 Identificar colecciones/dominios

A partir de la peticion del usuario, determinar que colecciones (dominios) incluir en la planificacion.

- Si el usuario especifica nombres de dominio: validarlos usando `search_domains` o `list_domains` con el `domain_type` correspondiente (semantico o tecnico). Si no especifica el tipo, preguntar al usuario con opciones siguiendo la convencion de preguntas al usuario.
- **Regla CRITICA**: los nombres de coleccion usados en la llamada a `create_quality_rule_planification` deben ser **exactamente** los valores devueltos por las herramientas de listado. NUNCA traducirlos, interpretarlos ni parafrasearlos.
- Si el usuario no especifica dominios concretos: listar los disponibles y preguntar cuales incluir.
- La planificacion soporta **multiples colecciones** en una sola llamada (`collection_names` es una lista).

### 1.2 Filtro opcional por tablas

Si el usuario quiere incluir solo tablas especificas dentro de las colecciones:

1. Validar las tablas con `list_domain_tables(domain_name)` por cada coleccion.
2. Confirmar que las tablas mencionadas existen en el dominio.
3. Si alguna tabla no existe, informar y preguntar.

Si el usuario no menciona tablas especificas, la planificacion incluira todas las tablas de cada coleccion (comportamiento por defecto).

---

## 2. Verificacion de Reglas Existentes

Antes de crear la planificacion, verificar que las carpetas seleccionadas contienen reglas de calidad. Planificar la ejecucion de una carpeta sin reglas no tiene sentido.

**Procedimiento** — por cada coleccion incluida:

1. Obtener las tablas del dominio con `list_domain_tables(domain_name)`.
2. Llamar `get_tables_quality_details(domain_name, [tablas])` para obtener el inventario de reglas.
   - Si se filtro por tablas (seccion 1.2), usar solo esas tablas.
   - Si no, usar todas las tablas del dominio.
3. Contar las reglas existentes y su estado (OK / KO / Warning / Sin ejecutar).

**Evaluacion de resultados:**

- **Coleccion sin reglas**: avisar al usuario explicitamente. Sugerir evaluar la cobertura y crear reglas antes de planificar. Preguntar al usuario con opciones, siguiendo la convencion de preguntas al usuario, si quiere continuar de todas formas o crear reglas primero.
- **Coleccion con reglas en estado KO**: mencionarlo como informacion relevante — la planificacion ejecutara tambien las reglas KO, lo que puede generar alertas recurrentes.
- **Coleccion con reglas**: resumir cuantas reglas hay, en cuantas tablas, y su estado general.

Si todas las colecciones seleccionadas estan vacias, no continuar con la planificacion. Redirigir al usuario a crear reglas primero.

**Presentar resumen al usuario** antes de continuar:

```markdown
### Reglas en las colecciones seleccionadas

| Coleccion | Tablas con reglas | Reglas totales | OK | KO | Warning | Sin ejecutar |
|-----------|-------------------|----------------|----|----|---------|-------------|
| financial | 5 | 23 | 18 | 2 | 1 | 2 |
| payments  | 3 | 12 | 10 | 0 | 2 | 0 |
```

---

## 3. Recopilar Parametros de la Planificacion

Recopilar los parametros necesarios para crear la planificacion. Algunos se preguntan al usuario, otros tienen defaults razonables.

### 3.1 Nombre (`name`) — obligatorio

Sugerir un nombre siguiendo la convencion `plan-[dominio]-[frecuencia]`:
- `plan-financial-daily`
- `plan-payments-weekly`
- `plan-financial-payments-monthly`

El usuario puede aceptar la sugerencia o proponer otro nombre. Si hay multiples colecciones, combinar los nombres relevantes o usar un nombre generico descriptivo.

### 3.2 Descripcion (`description`) — obligatorio

Generar una descripcion en lenguaje de negocio que explique el proposito de la planificacion. **Reglas obligatorias** (mismas que para descripciones de reglas de calidad):
1. NO incluir detalles tecnicos de scheduling (frecuencia, cron, horarios) — esa informacion ya esta en los campos de planificacion
2. NO usar nombres tecnicos de tablas o columnas
3. Describir el proposito de negocio de la planificacion

Ejemplo correcto: "Ejecucion periodica de las validaciones de calidad del dominio financiero para garantizar la integridad de los datos de cuentas y transacciones"
Ejemplo incorrecto: "Cron diario a las 9:00 que ejecuta las reglas de la coleccion financial_domain sobre las tablas account y transaction"

Presentar la descripcion propuesta al usuario para su validacion.

### 3.3 Expresion cron (`cron_expression`) — obligatorio

Aceptar la frecuencia en **lenguaje natural** y traducir a expresion Quartz cron (6 o 7 campos: segundo minuto hora dia-mes mes dia-semana [ano]).

**Ejemplos de traduccion:**
- "diariamente a las 9:00" → `0 0 9 * * ?`
- "cada lunes a las 8:30" → `0 30 8 ? * MON`
- "primer dia de cada mes a las 6:00" → `0 0 6 1 * ?`
- "cada 6 horas" → `0 0 */6 * * ?`
- "de lunes a viernes a las 7:00" → `0 0 7 ? * MON-FRI`

**Restriccion**: NO permitir expresiones de frecuencia muy baja (como `* * * * * *` o similares que ejecuten cada segundo/minuto). Si el usuario pide algo asi, explicar el riesgo y sugerir una frecuencia minima razonable.

Si el usuario proporciona directamente una expresion Quartz valida, usarla tal cual.

### 3.4 Zona horaria (`cron_timezone`) — opcional

Default: `Europe/Madrid`. **NO preguntar** salvo que el usuario mencione explicitamente otra zona horaria. Si la menciona, usar la zona indicada (ej: `UTC`, `America/New_York`).

### 3.5 Fecha de inicio (`cron_start_datetime`) — opcional

Preguntar: "¿Cuando quieres que empiece a ejecutarse? (dejar en blanco para empezar inmediatamente)".

Si el usuario indica una fecha/hora en lenguaje natural, convertir a formato ISO 8601 (ej: "el proximo lunes a las 9" → `<YYYY-MM-DD>T09:00:00`, donde `<YYYY-MM-DD>` es la fecha del proximo lunes calculada desde hoy). Si no indica nada, la planificacion empieza inmediatamente tras la creacion.

### 3.6 Tamano de ejecucion (`execution_size`) — opcional

Default: `XS`. **NO preguntar** salvo que el usuario mencione preocupaciones de rendimiento, volumen de datos o tamano de ejecucion. Opciones disponibles: `XS`, `S`, `M`, `L`, `XL`.

Si el usuario pregunta o la planificacion abarca un volumen grande de reglas/tablas, orientar:
- `XS` / `S`: dominios pequenos, pocas reglas
- `M`: dominios medianos, decenas de reglas
- `L` / `XL`: dominios grandes, cientos de reglas o queries complejas

---

## 4. PAUSA: Presentar Plan y Esperar Aprobacion

Antes de ejecutar la llamada a `create_quality_rule_planification`, presentar el plan completo al usuario.

### Formato del plan

```markdown
## Plan de Planificacion de Calidad

**Nombre**: plan-financial-daily
**Descripcion**: Ejecucion periodica de las validaciones de calidad del dominio financiero para garantizar la integridad de los datos de cuentas y transacciones
**Colecciones**: financial_domain
**Tablas filtradas**: todas (o lista de tablas si se filtro)
**Reglas que se ejecutaran**: 23 reglas en 5 tablas
**Programacion**: `0 0 9 * * ?` — diariamente a las 9:00 (Europe/Madrid)
**Primera ejecucion**: inmediatamente (o fecha ISO 8601 si se indico)
**Tamano de ejecucion**: XS

---

¿Procedo con la creacion de esta planificacion?
```

### Senales de aprobacion validas

Cualquiera de estas respuestas (o equivalentes en el idioma del usuario):
- "si", "sí", "s", "yes", "y"
- "procede", "adelante", "ok", "OK", "vale"
- "creala", "hazlo", "ejecuta"
- "apruebo", "aprobado", "confirmo"

### Senales de rechazo o modificacion

- "no", "cancela", "para"
- "cambia la frecuencia a..."
- "cambia el nombre a..."
- "añade/quita la coleccion X"
- "filtra solo las tablas Y"

Si el usuario modifica algun parametro: actualizar el plan y volver a presentar para aprobacion.

---

## 5. Ejecucion

Solo tras aprobacion explicita del usuario:

1. Llamar `create_quality_rule_planification` con todos los parametros configurados:
   - `name`: nombre de la planificacion
   - `description`: descripcion de negocio
   - `collection_names`: lista de colecciones/dominios
   - `cron_expression`: expresion Quartz cron
   - `table_names`: lista de tablas (solo si se filtro; si no, omitir)
   - `cron_timezone`: zona horaria (solo si difiere del default)
   - `cron_start_datetime`: fecha de inicio (solo si se indico)
   - `execution_size`: tamano (solo si difiere del default)

2. Reportar el resultado inmediatamente en el chat.

3. Si la llamada falla:
   - Informar del error al usuario con el mensaje del MCP.
   - Si el error es corregible (ej: expresion cron invalida, nombre duplicado), sugerir un ajuste y preguntar si quiere reintentar.
   - Maximo 2 reintentos con parametros ajustados. Si sigue fallando, informar y sugerir acciones alternativas.

---

## 6. Resumen Final

Tras la creacion exitosa, presentar confirmacion:

```markdown
## Planificacion Creada

- **Nombre**: plan-financial-daily
- **Estado**: Creada correctamente
- **Colecciones**: financial_domain
- **Reglas programadas**: 23 reglas en 5 tablas
- **Programacion**: diariamente a las 9:00 (Europe/Madrid)
- **Primera ejecucion**: inmediatamente
- **Tamano**: XS
```

---

## 7. Pregunta de Continuacion

Al finalizar, preguntar al usuario con opciones como quiere continuar, siguiendo la convencion de preguntas al usuario:
- **Crear otra planificacion para otras colecciones**
- **Crear reglas de calidad para colecciones que estaban vacias**
- **Evaluar la cobertura de calidad actual**
- **Finalizar**
