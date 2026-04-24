# create-quality-schedule

Crea un **schedule a nivel de carpeta** que ejecuta automáticamente todas las reglas de calidad contenidas en una o varias colecciones de Stratio Governance sobre un calendario cron Quartz. Planifica a nivel de carpeta / colección — no por regla individual — y siempre requiere confirmación explícita del usuario.

## Qué hace

- Resuelve las colecciones objetivo (validando cada nombre exactamente contra `search_domains` / `list_domains`) y soporta planificar múltiples colecciones en una sola llamada.
- Filtro opcional por tabla: cuando el usuario quiere ejecutar el schedule solo sobre ciertas tablas de una colección, valida que esas tablas existen (`list_domain_tables`).
- Verifica que cada colección tiene reglas vía `get_tables_quality_details` y presenta un conteo por colección con desglose OK/KO/Warning/No-ejecutadas.
- Avisa sobre colecciones vacías (no tiene sentido planificarlas) y sobre reglas KO (que seguirán disparando alertas).
- Recoge parámetros del schedule: nombre (sugerido como `plan-[domain]-[frequency]`), descripción de negocio (sin detalles de scheduling dentro, sin nombres técnicos de columnas), expresión cron Quartz traducida desde frecuencia en lenguaje natural, datetime de inicio opcional (ISO 8601), timezone (por defecto `Europe/Madrid`), tamaño de ejecución (`XS` por defecto, hasta `XL` para dominios grandes).
- Presenta un plan completo y espera aprobación explícita antes de llamar a `create_quality_rule_planification`.

## Cuándo usarla

- El usuario quiere automatizar checks de calidad recurrentes (diario, semanal, mensual) para un dominio o un conjunto de dominios.
- El usuario quiere un único schedule que cubra varias colecciones a la vez.
- Para crear **las reglas** en sí, prefiere `create-quality-rules` — esta skill solo planifica reglas que ya existen.
- Para filtrar ejecución a tablas específicas dentro de una colección, pasa el filtro en el paso 1.2.

## Dependencias

### Otras skills
- **Prerrequisito:** `create-quality-rules` (el schedule tiene sentido solo si existen reglas).
- **Predecesores típicos:** `assess-quality` → `create-quality-rules` → `create-quality-schedule`.
- **Referencia a cargar antes:** `stratio-semantic-layer` (reglas de los MCPs de gobierno).

### Guides
Ninguno. Los ejemplos de traducción cron y la guía de tamaños están inline en `SKILL.md`.

### MCPs
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`.
- **Governance (`gov`):** `get_tables_quality_details`, `create_quality_rule_planification`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Pausa crítica de aprobación:** `create_quality_rule_planification` **nunca** se llama sin confirmación explícita del usuario.
- **El timezone por defecto es `Europe/Madrid`.** La skill no pregunta por el timezone salvo que el usuario mencione otro.
- **El tamaño de ejecución por defecto es `XS`.** Usa `M` / `L` / `XL` solo para dominios grandes o cientos de reglas — la skill no pregunta salvo que el usuario plantee problemas de rendimiento.
- **Las expresiones cron de frecuencia muy baja** (cada segundo/minuto) se rechazan; la skill explica el riesgo y sugiere un mínimo razonable.
- **La traducción cron desde lenguaje natural** está integrada en la skill: "daily at 9" → `0 0 9 * * ?`, "every Monday at 8:30" → `0 30 8 ? * MON`, etc.
