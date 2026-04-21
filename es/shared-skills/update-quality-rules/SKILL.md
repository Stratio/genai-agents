---
name: update-quality-rules
description: "Modificar reglas de calidad existentes: corregir queries SQL, cambiar umbrales, actualizar descripciones, añadir o quitar planificación, o cambiar la configuración de medición. Requiere el UUID de la regla (obtenido via get_tables_quality_details si no está en contexto) y confirmación humana obligatoria antes de ejecutar."
argument-hint: "[nombre de la regla o dominio] [opcional: qué cambiar]"
---

# Skill: Actualización de Reglas de Calidad

Workflow para modificar una regla de calidad existente con aprobación humana. Solo se envían los campos que el usuario quiere cambiar — el resto permanece sin modificar.

## PREREQUISITO

El usuario quiere modificar una regla de calidad existente. Hay dos vías de entrada:

**Vía directa**: El usuario identifica la regla por nombre, UUID o descripción. El agente puede o no tener ya el UUID en contexto.

**Desde contexto de assessment**: El agente ya listó las reglas de calidad (via `get_tables_quality_details`) y el usuario quiere corregir una o varias reglas en estado KO o WARNING.

Este skill NO requiere una evaluación de cobertura previa.

## PAUSA CRÍTICA DE APROBACIÓN

**NUNCA llamar a `update_quality_rule` sin que el usuario haya confirmado explícitamente los cambios propuestos.**

Esta pausa es obligatoria. No interpretar silencio ni respuestas ambiguas como aprobación.

Si la query o query_reference cambia, **la validación SQL es OBLIGATORIA** antes de presentar el plan. No mostrar el plan sin verificar primero que ambas queries son válidas.

**Cada invocación de este skill es independiente.** Una aprobación dada para un cambio anterior NO es válida para una nueva modificación.

---

## 1. Identificar la Regla

**Si el UUID ya es conocido** (en el contexto de la conversación): usarlo directamente. Ir al paso 2.

**Si solo se conoce el nombre o descripción de la regla**:
1. Llamar a `get_tables_quality_details(domain_name, [tabla])` para obtener el inventario completo de reglas
2. Localizar la regla por nombre o descripción en la lista devuelta
3. Extraer su UUID y parámetros actuales: nombre, queries SQL, dimensión, configuración de medición, planificación y estado actual (OK/KO/WARNING + % pass)

Si el usuario no proporciona el dominio o la tabla, preguntar con opciones antes de llamar al tool.

**Mostrar al usuario el estado actual** de la regla antes de continuar:

```markdown
### Estado actual de la regla dq-account-completeness-id (UUID: fa989da8-...)
- **Tabla**: account
- **Dimensión**: completeness
- **SQL (registros que pasan)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL`
- **SQL (total)**: `SELECT COUNT(*) FROM ${account}`
- **Medición**: porcentaje, rangos — [0%-80%] KO, (80%-95%] WARNING, (95%-100%] OK
- **Planificación**: diariamente a las 9:00 (Europe/Madrid)
- **Estado actual**: KO (72%)
```

---

## 2. Recopilar los Cambios

**Si el usuario ya describió los cambios en la petición**: proceder directamente con esos cambios.

**Si la petición es vaga** (ej: "arregla la regla X", "actualízala"): preguntar qué quiere cambiar con opciones:

```
¿Qué quieres cambiar en esta regla?
1. La query SQL (corregir la lógica, añadir/eliminar condiciones)
2. Los umbrales de medición (cambiar niveles, tipo o valores)
3. La planificación (añadir, modificar o eliminar la ejecución automática)
4. La descripción o el nombre
5. La dimensión
6. Varias de las anteriores (descríbelas)
```

### Casos especiales

**Eliminar planificación**: pasar `cron_expression=""` (cadena vacía). Esto elimina el schedule sin cambiar ningún otro campo.

**Solo cambiar umbrales**: pasar solo el nuevo `measurement_type`, `threshold_mode` y `exact_threshold` o `threshold_breakpoints`. No tocar queries ni otros campos.

**Cambiar SQL**: ver sección 3 (la validación SQL es OBLIGATORIA).

**Cambiar descripción**: aplicar las mismas reglas obligatorias que en la sección 3.1 de la skill `create-quality-rules` — sin información de planificación, sin nombres técnicos de columnas, sin mencionar la dimensión, sin información de medición, sin estado activo/inactivo.

**Activar/desactivar**: pasar `active=true` o `active=false` si el usuario quiere cambiar el estado activo de la regla.

---

## 3. Validación de SQL (OBLIGATORIO si cambia query o query_reference)

Si los cambios propuestos incluyen una nueva `query` o `query_reference`, validar ambas antes de presentar el plan.

**Procedimiento de validación:**
1. Preparar la nueva `query` y la `query_reference`.
2. Resolver los placeholders `${tabla}` sustituyéndolos por el nombre real de la tabla.
3. Ejecutar ambas queries usando `execute_sql(query=[sql], limit=1)`.
4. Si alguna query devuelve error:
   - Revisar la sintaxis SQL.
   - Corregir la query.
   - Re-validar hasta que ambas sean correctas.
5. Con ambas queries exitosas, calcular el resultado y el estado de la regla:
   - Obtener `query_val` (valor numérico de `query`) y `query_ref_val` (valor numérico de `query_reference`).
   - Aplicar la configuración de medición (la existente, o la nueva si también se está cambiando):
     - Si `measurement_type = "percentage"`: `result = (query_val / query_ref_val) * 100` redondeado a 2 decimales. Si `query_ref_val == 0`, anotar `SIN_DATOS`.
     - Si `measurement_type = "count"`: `result = query_val`.
   - Evaluar el estado según `threshold_mode` (umbrales existentes salvo que también se cambien):
     - `"exact"`: si `result == exact_threshold.value` → `equal_status`; si no → `not_equal_status`.
     - `"range"`: recorrer `threshold_breakpoints` en orden ascendente; usar el `status` del primer punto cuyo `value >= result`; si el resultado supera todos los puntos con valor, usar el `status` del último punto (rango abierto).
   - El estado calculado se incluye en el campo **Nuevo resultado de validación** del plan.

Si solo cambian los umbrales (no el SQL), se puede calcular el nuevo estado proyectado usando los valores SQL ya conocidos (ej: de `get_tables_quality_details`). Si no están disponibles, indicar que la regla será reevaluada en la próxima ejecución.

---

## 4. PAUSA: Presentar Plan y Esperar Aprobación

Antes de ejecutar ninguna llamada a `update_quality_rule`, presentar los cambios propuestos en formato antes/después.

### Formato del plan

```markdown
## Plan de Actualización de Regla de Calidad

**Regla**: dq-account-completeness-id (UUID: fa989da8-...)
**Dominio**: [domain_name]

### Estado actual
- **SQL (registros que pasan)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL`
- **SQL (total)**: `SELECT COUNT(*) FROM ${account}`
- **Medición**: porcentaje, rangos — [0%-80%] KO, (80%-95%] WARNING, (95%-100%] OK
- **Planificación**: diariamente a las 9:00 (Europe/Madrid)
- **Estado**: KO (72%)

### Cambios propuestos
- **SQL (registros que pasan)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL AND id != ''`
- **Nuevo resultado de validación**: 45.230 de 45.230 registros pasan → 100,00% → OK

(Los campos no listados aquí permanecen sin cambios.)
```

Solo listar en la sección "Cambios propuestos" los campos que realmente cambian. Los campos no mencionados permanecen exactamente como están.

**Si el SQL cambia y valida correctamente**: mostrar siempre el nuevo resultado de validación.

**Si solo cambian los umbrales**: mostrar el antes/después de los umbrales. Si se conoce el porcentaje de estado anterior, calcular el nuevo estado proyectado.

**Si se elimina la planificación**: indicarlo explícitamente — "Planificación: eliminada (actualmente: diariamente a las 9:00)".

**Si cambian múltiples campos**: listar cada uno claramente en la sección "Cambios propuestos".

---

```
¿Procedo con esta actualización?
```

### Interpretación de la respuesta del usuario

**Señales válidas de aprobación**: "sí", "procede", "adelante", "ok", "actualiza", "aplica", "confirmo", o equivalentes en el idioma del usuario.

**Señales de rechazo o modificación**: "no", "cancela", "cambia X en su lugar", "también cambia Y", "espera".

Si el usuario modifica la petición: actualizar el plan y volver a presentarlo para aprobación final.

---

## 5. Ejecución: Actualizar la Regla

Solo tras aprobación explícita, llamar a `update_quality_rule` con **solo los campos que cambian**. No enviar campos que permanecen sin modificar.

```
update_quality_rule(
  uuid="fa989da8-ae49-4e50-bcd5-1e1be33dbbe8",
  query="SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL AND id != ''",
  query_reference="SELECT COUNT(*) FROM ${account}"
)
```

**Ejemplos por tipo de cambio:**

Corregir solo SQL:
```
update_quality_rule(uuid=..., query=..., query_reference=...)
```

Cambiar solo umbrales:
```
update_quality_rule(uuid=..., measurement_type="percentage", threshold_mode="exact", exact_threshold={"value": "100", "equal_status": "OK", "not_equal_status": "KO"})
```

Añadir planificación:
```
update_quality_rule(uuid=..., cron_expression="0 0 9 * * ?", cron_timezone="Europe/Madrid")
```

Eliminar planificación:
```
update_quality_rule(uuid=..., cron_expression="")
```

Cambiar solo descripción:
```
update_quality_rule(uuid=..., description="Valida que cada registro de cuenta tiene un identificador primario no nulo y no vacío, garantizando la integridad de los datos en todo el sistema")
```

Cambiar múltiples campos:
```
update_quality_rule(uuid=..., query=..., query_reference=..., cron_expression="0 0 9 * * ?")
```

Reportar el resultado inmediatamente tras la llamada:

```
[OK]  dq-account-completeness-id — actualizada correctamente
[ERR] dq-account-completeness-id — error: [mensaje MCP]
```

---

## 6. Resumen

Tras una actualización exitosa, presentar un resumen breve:

```markdown
## Resultado de la Actualización

- **Regla**: dq-account-completeness-id
- **Cambios aplicados**: query SQL corregida, sin cambios en medición ni planificación
- **Estado anterior**: KO (72%)
- **Estado proyectado** (basado en nueva validación SQL): OK (100,00%)

### Próximos pasos recomendados

- Ejecutar la regla para confirmar el nuevo estado con los datos actuales
- [Si la regla estaba en KO antes de la corrección]: verificar que ahora pasa de forma consistente
```

Si la actualización falla, indicar claramente el error y sugerir alternativas (reintentar, verificar el UUID, contactar al administrador de la plataforma).

## 7. Pregunta de Continuación

Al finalizar, preguntar al usuario con opciones cómo quiere continuar, siguiendo la convención de preguntas del agente:
- **Actualizar otra regla**
- **Crear una regla nueva** (cargar `create-quality-rules`)
- **Evaluar la cobertura** del dominio
- **Finalizar**
