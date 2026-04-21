---
name: update-quality-scheduler
description: "Modificar una planificación (scheduler) de reglas de calidad existente: cambiar el schedule (cron), actualizar colecciones o filtros de tablas, renombrar, actualizar descripción, activar/desactivar o cambiar el tamaño de ejecución. Requiere el UUID del scheduler (descubierto via list_quality_rule_schedulers si no está en contexto) y confirmación humana obligatoria antes de ejecutar."
argument-hint: "[nombre o UUID del scheduler] [opcional: qué cambiar]"
---

# Skill: Actualización de Planificación de Reglas de Calidad

Workflow para modificar una planificación de reglas de calidad existente con aprobación humana. Solo se envían los campos que el usuario quiere cambiar — el resto permanece sin modificar.

## PAUSA DE APROBACIÓN CRÍTICA

**NUNCA llamar `update_quality_rule_scheduler` sin que el usuario haya confirmado explícitamente los cambios propuestos.**

Esta pausa es obligatoria. No interpretar silencio ni respuestas ambiguas como aprobación.

**Cada invocación de este skill es independiente.** Una aprobación dada para un cambio anterior NO es válida para una nueva modificación.

---

## 1. Identificar el Scheduler

**Si el UUID ya es conocido** (en el contexto de la conversación, ej. de una llamada reciente a `create_quality_rule_scheduler`): usarlo directamente. Ir al paso 2.

**Si el UUID no es conocido**:
1. Llamar `list_quality_rule_schedulers()` — sin parámetros.
2. Presentar los resultados al usuario en formato legible:

```markdown
### Planificaciones de Calidad Existentes

| Nombre | Activa | Colecciones | Planificación | UUID |
|--------|--------|-------------|---------------|------|
| plan-financial | ✓ | financial_domain | `0 0 9 * * ?` (diariamente a las 9:00) | fa989da8-... |
| plan-payments | ✗ | payments_domain | `0 30 8 ? * MON` (lunes a las 8:30) | bc123ef4-... |
```

3. Preguntar al usuario qué scheduler quiere modificar.
4. Extraer el UUID y el estado actual del scheduler seleccionado.

**Mostrar al usuario el estado actual** del scheduler seleccionado antes de continuar:

```markdown
### Estado actual del scheduler plan-financial (UUID: fa989da8-...)
- **Nombre**: plan-financial
- **Descripción**: Ejecución periódica de las validaciones de calidad del dominio financiero
- **Colecciones**: financial_domain
- **Filtro de tablas**: todas las tablas
- **Planificación**: `0 0 9 * * ?` — diariamente a las 9:00 (Europe/Madrid)
- **Primera ejecución**: inmediatamente
- **Tamaño de ejecución**: XS
- **Activa**: sí
```

---

## 2. Recopilar los Cambios

**Si el usuario ya describió los cambios en la petición**: proceder directamente con esos cambios.

**Si la petición es vaga** (ej: "actualiza el scheduler X", "modifícalo"): preguntar qué quiere cambiar con opciones:

```
¿Qué quieres cambiar en este scheduler?
1. La planificación (expresión cron, frecuencia, zona horaria)
2. Las colecciones o el filtro de tablas (qué carpetas ejecutar)
3. El nombre o la descripción
4. Activar o desactivar el scheduler
5. El tamaño de ejecución (XS/S/M/L/XL)
6. Varias de las anteriores (descríbelas)
```

### Casos especiales

**Activar/desactivar**: pasar `active=true` o `active=false`. No es necesario cambiar ningún otro campo.

**Cambiar solo el cron**: pasar `cron_expression` (y opcionalmente `cron_timezone`, `cron_start_datetime`). No tocar colecciones ni otros campos.

**Reemplazar colecciones**: `collection_names` **reemplaza** todos los recursos planificados existentes — no es acumulativo. Si se proporciona, validar las nuevas colecciones (ver sección 3).

**Filtro de tablas**: `table_names` solo se usa cuando también se proporciona `collection_names`. Si solo cambia el filtro de tablas dentro de las colecciones existentes, hay que pasar también `collection_names`.

**`cron_timezone` y `cron_start_datetime`**: solo se usan cuando se proporciona `cron_expression`.

**Cambiar descripción**: aplicar las mismas reglas obligatorias que en la sección 3.2 de la skill `create-quality-scheduler` — sin información de scheduling, sin nombres técnicos de tablas o columnas, sin información de medición, sin estado activo/inactivo.

**Expresión cron**: aceptar la frecuencia en **lenguaje natural** y traducir a expresión Quartz cron (6 o 7 campos). Ejemplos:
- "diariamente a las 9:00" → `0 0 9 * * ?`
- "cada lunes a las 8:30" → `0 30 8 ? * MON`
- "primer día de cada mes a las 6:00" → `0 0 6 1 * ?`

NO permitir expresiones de frecuencia muy baja (como `* * * * * *`). Si el usuario proporciona directamente una expresión Quartz válida, usarla tal cual.

---

## 3. Validar Nuevas Colecciones (OBLIGATORIO si cambia `collection_names`)

Si los cambios propuestos incluyen una lista de `collection_names` nueva o diferente:

1. Validar cada nombre de colección contra `search_domains` o `list_domains` para confirmar que existe.
2. Para cada nueva colección, llamar `list_domain_tables(domain_name)` y `get_tables_quality_details(domain_name, [tablas])` para verificar que contiene reglas de calidad.
3. Si una colección no tiene reglas: avisar al usuario — planificar una carpeta vacía no tiene sentido. Preguntar con opciones (siguiendo la convención de preguntas al usuario) si quiere continuar de todas formas o crear reglas primero.
4. Resumir las reglas encontradas en las nuevas colecciones:

```markdown
### Reglas en las nuevas colecciones

| Colección | Tablas con reglas | Reglas totales | OK | KO | Warning | Sin ejecutar |
|-----------|-------------------|----------------|----|----|---------|-------------|
| payments_domain | 3 | 12 | 10 | 0 | 2 | 0 |
```

---

## 4. PAUSA: Presentar Plan y Esperar Aprobación

Antes de ejecutar ninguna llamada a `update_quality_rule_scheduler`, presentar los cambios propuestos en formato antes/después.

### Formato del plan

```markdown
## Plan de Actualización del Scheduler de Calidad

**Scheduler**: plan-financial (UUID: fa989da8-...)

### Estado actual
- **Colecciones**: financial_domain
- **Planificación**: `0 0 9 * * ?` — diariamente a las 9:00 (Europe/Madrid)
- **Activa**: sí
- **Tamaño de ejecución**: XS

### Cambios propuestos
- **Planificación**: `0 30 8 ? * MON` — cada lunes a las 8:30 (Europe/Madrid)

(Los campos no listados aquí permanecen sin cambios.)
```

Solo listar en "Cambios propuestos" los campos que realmente cambian. Los campos no mencionados permanecen exactamente como están.

---

```
¿Procedo con esta actualización?
```

### Interpretación de la respuesta del usuario

**Señales válidas de aprobación**: "sí", "procede", "adelante", "ok", "actualiza", "aplica", "confirmo", o equivalentes en el idioma del usuario.

**Señales de rechazo o modificación**: "no", "cancela", "cambia X en su lugar", "también cambia Y", "espera".

Si el usuario modifica la petición: actualizar el plan y volver a presentarlo para aprobación final.

---

## 5. Ejecución: Actualizar el Scheduler

Solo tras aprobación explícita, llamar a `update_quality_rule_scheduler` con **solo los campos que cambian**. No enviar campos que permanecen sin modificar.

**Ejemplos por tipo de cambio:**

Cambiar solo el cron:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  cron_expression="0 30 8 ? * MON",
  cron_timezone="Europe/Madrid"
)
```

Activar/desactivar:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  active=false
)
```

Reemplazar colecciones:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  collection_names=["payments_domain", "financial_domain"]
)
```

Cambiar nombre y descripción:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  name="plan-financial-payments",
  description="Ejecución periódica de las validaciones de calidad de los dominios financiero y de pagos"
)
```

Cambiar tamaño de ejecución:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  execution_size="M"
)
```

Múltiples campos:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  cron_expression="0 0 6 1 * ?",
  collection_names=["financial_domain", "payments_domain"],
  execution_size="S"
)
```

Reportar el resultado inmediatamente tras la llamada:

```
[OK]  plan-financial — actualizado correctamente
[ERR] plan-financial — error: [mensaje MCP]
```

---

## 6. Resumen

Tras una actualización exitosa, presentar un resumen breve:

```markdown
## Resultado de la Actualización

- **Scheduler**: plan-financial
- **Cambios aplicados**: cron actualizado — anteriormente diariamente a las 9:00, ahora cada lunes a las 8:30
- **Próxima ejecución**: el próximo lunes a las 8:30 (Europe/Madrid)
```

Si la actualización falla, indicar claramente el error y sugerir alternativas (reintentar, verificar el UUID, contactar al administrador de la plataforma).

## 7. Pregunta de Continuación

Al finalizar, preguntar al usuario con opciones cómo quiere continuar, siguiendo la convención de preguntas al usuario:
- **Actualizar otro scheduler**
- **Crear una nueva planificación** (cargar `create-quality-scheduler`)
- **Listar las planificaciones actuales**
- **Finalizar**
