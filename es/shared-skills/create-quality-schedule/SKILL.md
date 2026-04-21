---
name: create-quality-schedule
description: "Crear una planificación (schedule) para ejecutar automáticamente todas las reglas de calidad de una o varias carpetas/colecciones. Opera a nivel de carpeta (dominio/colección), no de regla individual. Requiere confirmación humana obligatoria antes de ejecutar."
argument-hint: "[dominio/colección] [frecuencia (opcional)]"
---

# Skill: Creación de Planificación de Reglas de Calidad

Workflow para crear una planificación que ejecute automáticamente todas las reglas de calidad contenidas en una o varias carpetas (colecciones/dominios) según un calendario definido por el usuario.

## PAUSA DE APROBACION CRITICA

**NUNCA llamar `create_quality_rule_planification` sin que el usuario haya confirmado explícitamente el plan.**

Si hay dudas sobre si el usuario ha aprobado, preguntar de nuevo. No interpretar silencio ni respuestas ambiguas como aprobación.

---

## 1. Determinación de Scope

### 1.1 Identificar colecciones/dominios

A partir de la petición del usuario, determinar que colecciones (dominios) incluir en la planificación.

- Si el usuario específica nombres de dominio: validarlos usando `search_domains` o `list_domains` con el `domain_type` correspondiente (semántico o técnico). Si no específica el tipo, preguntar al usuario con opciones siguiendo la convención de preguntas al usuario.
- **Regla CRITICA**: los nombres de colección usados en la llamada a `create_quality_rule_planification` deben ser **exactamente** los valores devueltos por las herramientas de listado. NUNCA traducirlos, interpretarlos ni parafrasearlos.
- Si el usuario no específica dominios concretos: listar los disponibles y preguntar cuales incluir.
- La planificación soporta **múltiples colecciones** en una sola llamada (`collection_names` es una lista).

### 1.2 Filtro opcional por tablas

Si el usuario quiere incluir solo tablas específicas dentro de las colecciones:

1. Validar las tablas con `list_domain_tables(domain_name)` por cada colección.
2. Confirmar que las tablas mencionadas existen en el dominio.
3. Si alguna tabla no existe, informar y preguntar.

Si el usuario no menciona tablas específicas, la planificación incluira todas las tablas de cada colección (comportamiento por defecto).

---

## 2. Verificación de Reglas Existentes

Antes de crear la planificación, verificar que las carpetas seleccionadas contienen reglas de calidad. Planificar la ejecución de una carpeta sin reglas no tiene sentido.

**Procedimiento** — por cada colección incluida:

1. Obtener las tablas del dominio con `list_domain_tables(domain_name)`.
2. Llamar `get_tables_quality_details(domain_name, [tablas])` para obtener el inventario de reglas.
   - Si se filtro por tablas (sección 1.2), usar solo esas tablas.
   - Si no, usar todas las tablas del dominio.
3. Contar las reglas existentes y su estado (OK / KO / Warning / Sin ejecutar).

**Evaluación de resultados:**

- **Colección sin reglas**: avisar al usuario explícitamente. Sugerir evaluar la cobertura y crear reglas antes de planificar. Preguntar al usuario con opciones, siguiendo la convención de preguntas al usuario, si quiere continuar de todas formas o crear reglas primero.
- **Colección con reglas en estado KO**: mencionarlo como información relevante — la planificación ejecutara también las reglas KO, lo que puede generar alertas recurrentes.
- **Colección con reglas**: resumir cuantas reglas hay, en cuantas tablas, y su estado general.

Si todas las colecciones seleccionadas están vacias, no continuar con la planificación. Redirigir al usuario a crear reglas primero.

**Presentar resumen al usuario** antes de continuar:

```markdown
### Reglas en las colecciones seleccionadas

| Colección | Tablas con reglas | Reglas totales | OK | KO | Warning | Sin ejecutar |
|-----------|-------------------|----------------|----|----|---------|-------------|
| financial | 5 | 23 | 18 | 2 | 1 | 2 |
| payments  | 3 | 12 | 10 | 0 | 2 | 0 |
```

---

## 3. Recopilar Parámetros de la Planificación

Recopilar los parámetros necesarios para crear la planificación. Algunos se preguntan al usuario, otros tienen defaults razonables.

### 3.1 Nombre (`name`) — obligatorio

Sugerir un nombre siguiendo la convención `plan-[dominio]-[frecuencia]`:
- `plan-financial-daily`
- `plan-payments-weekly`
- `plan-financial-payments-monthly`

El usuario puede aceptar la sugerencia o proponer otro nombre. Si hay múltiples colecciones, combinar los nombres relevantes o usar un nombre genérico descriptivo.

### 3.2 Descripción (`description`) — obligatorio

Generar una descripción en lenguaje de negocio que explique el propósito de la planificación. **Reglas obligatorias** (mismas que para descripciones de reglas de calidad):
1. NO incluir detalles técnicos de scheduling (frecuencia, cron, horarios) — esa información ya está en los campos de planificación
2. NO usar nombres técnicos de tablas o columnas
3. Describir el propósito de negocio de la planificación

Ejemplo correcto: "Ejecución periodica de las validaciones de calidad del dominio financiero para garantizar la integridad de los datos de cuentas y transacciones"
Ejemplo incorrecto: "Cron diario a las 9:00 que ejecuta las reglas de la colección financial_domain sobre las tablas account y transaction"

Presentar la descripción propuesta al usuario para su validación.

### 3.3 Expresión cron (`cron_expression`) — obligatorio

Aceptar la frecuencia en **lenguaje natural** y traducir a expresión Quartz cron (6 o 7 campos: segundo minuto hora día-mes mes día-semana [año]).

**Ejemplos de traduccion:**
- "diariamente a las 9:00" → `0 0 9 * * ?`
- "cada lunes a las 8:30" → `0 30 8 ? * MON`
- "primer día de cada mes a las 6:00" → `0 0 6 1 * ?`
- "cada 6 horas" → `0 0 */6 * * ?`
- "de lunes a viernes a las 7:00" → `0 0 7 ? * MON-FRI`

**Restricción**: NO permitir expresiones de frecuencia muy baja (como `* * * * * *` o similares que ejecuten cada segundo/minuto). Si el usuario pide algo así, explicar el riesgo y sugerir una frecuencia mínima razonable.

Si el usuario proporciona directamente una expresión Quartz válida, usarla tal cual.

### 3.4 Zona horaria (`cron_timezone`) — opcional

Default: `Europe/Madrid`. **NO preguntar** salvo que el usuario mencione explícitamente otra zona horaria. Si la menciona, usar la zona indicada (ej: `UTC`, `America/New_York`).

### 3.5 Fecha de inicio (`cron_start_datetime`) — opcional

Preguntar: "¿Cuándo quieres que empiece a ejecutarse? (dejar en blanco para empezar inmediatamente)".

Si el usuario indica una fecha/hora en lenguaje natural, convertir a formato ISO 8601 (ej: "el proximo lunes a las 9" → `<YYYY-MM-DD>T09:00:00`, donde `<YYYY-MM-DD>` es la fecha del proximo lunes calculada desde hoy). Si no indica nada, la planificación empieza inmediatamente tras la creación.

### 3.6 Tamaño de ejecución (`execution_size`) — opcional

Default: `XS`. **NO preguntar** salvo que el usuario mencione preocupaciones de rendimiento, volumen de datos o tamaño de ejecución. Opciones disponibles: `XS`, `S`, `M`, `L`, `XL`.

Si el usuario pregunta o la planificación abarca un volumen grande de reglas/tablas, orientar:
- `XS` / `S`: dominios pequeños, pocas reglas
- `M`: dominios medianos, decenas de reglas
- `L` / `XL`: dominios grandes, cientos de reglas o queries complejas

---

## 4. PAUSA: Presentar Plan y Esperar Aprobación

Antes de ejecutar la llamada a `create_quality_rule_planification`, presentar el plan completo al usuario.

### Formato del plan

```markdown
## Plan de Planificación de Calidad

**Nombre**: plan-financial-daily
**Descripción**: Ejecución periodica de las validaciones de calidad del dominio financiero para garantizar la integridad de los datos de cuentas y transacciones
**Colecciones**: financial_domain
**Tablas filtradas**: todas (o lista de tablas si se filtro)
**Reglas que se ejecutaran**: 23 reglas en 5 tablas
**Programacion**: `0 0 9 * * ?` — diariamente a las 9:00 (Europe/Madrid)
**Primera ejecución**: inmediatamente (o fecha ISO 8601 si se indicó)
**Tamaño de ejecución**: XS

---

¿Procedo con la creación de esta planificación?
```

### Señales de aprobación válidas

Cualquiera de estas respuestas (o equivalentes en el idioma del usuario):
- "si", "sí", "s", "yes", "y"
- "procede", "adelante", "ok", "OK", "vale"
- "creala", "hazlo", "ejecuta"
- "apruebo", "aprobado", "confirmo"

### Señales de rechazo o modificación

- "no", "cancela", "para"
- "cambia la frecuencia a..."
- "cambia el nombre a..."
- "añade/quita la colección X"
- "filtra solo las tablas Y"

Si el usuario modifica algún parámetro: actualizar el plan y volver a presentar para aprobación.

---

## 5. Ejecución

Solo tras aprobación explícita del usuario:

1. Llamar `create_quality_rule_planification` con todos los parámetros configurados:
   - `name`: nombre de la planificación
   - `description`: descripción de negocio
   - `collection_names`: lista de colecciones/dominios
   - `cron_expression`: expresión Quartz cron
   - `table_names`: lista de tablas (solo si se filtro; si no, omitir)
   - `cron_timezone`: zona horaria (solo si difiere del default)
   - `cron_start_datetime`: fecha de inicio (solo si se indicó)
   - `execution_size`: tamaño (solo si difiere del default)

2. Reportar el resultado inmediatamente en el chat.

3. Si la llamada falla:
   - Informar del error al usuario con el mensaje del MCP.
   - Si el error es corregible (ej: expresión cron invalida, nombre duplicado), sugerir un ajuste y preguntar si quiere reintentar.
   - Máximo 2 reintentos con parámetros ajustados. Si sigue fallando, informar y sugerir acciones alternativas.

---

## 6. Resumen Final

Tras la creación exitosa, presentar confirmación:

```markdown
## Planificación Creada

- **Nombre**: plan-financial-daily
- **Estado**: Creada correctamente
- **Colecciones**: financial_domain
- **Reglas programadas**: 23 reglas en 5 tablas
- **Programacion**: diariamente a las 9:00 (Europe/Madrid)
- **Primera ejecución**: inmediatamente
- **Tamaño**: XS
```

---

## 7. Pregunta de Continuación

Al finalizar, preguntar al usuario con opciones como quiere continuar, siguiendo la convención de preguntas al usuario:
- **Crear otra planificación para otras colecciones**
- **Crear reglas de calidad para colecciones que estaban vacias**
- **Evaluar la cobertura de calidad actual**
- **Finalizar**
