# create-quality-rules

Diseña y crea reglas de calidad de datos en Stratio Governance con **confirmación humana obligatoria antes de ejecutar**. Soporta dos flujos de entrada: **Flow A** (cubrir gaps identificados por una ejecución previa de `assess-quality`) y **Flow B** (crear una regla específica descrita por el usuario, sin assessment previo).

El scheduling (cron Quartz) y la configuración de medición (percentage/count × exact/range thresholds) se negocian junto con el paso de aprobación — nunca como añadido posterior.

## Qué hace

- **Flow A — gaps:** lee el inventario de reglas existentes (`get_tables_quality_details`) y la EDA previa de `assess-quality`, y luego diseña reglas solo para dimensiones/columnas no cubiertas.
- **Flow B — regla específica:** consulta columnas, detalles de tabla y definiciones de dimensión, y luego diseña una regla única a partir de la descripción del usuario.
- Diseña cada regla con: nombre en kebab-case (`dq-[table]-[dimension]-[column]`), descripción en lenguaje de negocio (sin scheduling, sin nombres técnicos de columnas, sin mención de la dimensión), SQL `query` (numerador — registros que pasan) y `query_reference` (denominador — total), dimensión, tipo de medición + configuración de thresholds y cron opcional.
- Cubre siete dimensiones con patrones SQL canónicos: `completeness`, `uniqueness`, `validity` (rango numérico, enumeración, fecha), `consistency` (intra-fila y entre tablas), `timeliness`, `accuracy`.
- **La validación SQL es obligatoria** antes del paso de aprobación: ejecuta `execute_sql(query, limit=1)` sobre ambos SQLs, calcula el resultado actual y el estado (OK / KO / WARNING / NO_DATA) y lo muestra en el plan.
- Presenta el plan completo y espera aprobación explícita. Pregunta scheduling y medición junto con la aprobación — sin defaults silenciosos.
- Crea las reglas secuencialmente (no en paralelo) y reporta el estado `[OK]` / `[ERR]` por regla en chat.
- Refresca la metadata AI (`quality_rules_metadata`) tras la creación y muestra una tabla de cobertura antes-vs-después.

## Cuándo usarla

- Seguimiento de `assess-quality` para cubrir los gaps identificados (Flow A).
- Creación ad-hoc de una regla específica (check de FK, amount no negativo, reconciliación de accuracy a medida) sin ejecutar un assessment completo antes (Flow B).
- Para scheduling de reglas **ya existentes**, prefiere `create-quality-schedule` — ese es un scheduler a nivel de carpeta para lotes de reglas.

## Dependencias

### Otras skills
- **Predecesora típica para Flow A:** `assess-quality`.
- **Siguiente paso típico:** `create-quality-schedule` (automatización folder-level) o `quality-report` (formalizar el resultado).
- **Referencia a cargar antes:** `stratio-data` (reglas de MCPs).

### Guides
- `quality-exploration.md` — paso obligatorio de `get_quality_rule_dimensions` y señales de EDA por tipo de columna; guía el razonamiento del Flow A y la elección de dimensión del Flow B.

### MCPs
- **Data (`sql`):** `get_table_columns_details`, `get_tables_details`, `generate_sql`, `execute_sql`.
- **Governance (`gov`):** `get_quality_rule_dimensions`, `quality_rules_metadata`, `get_tables_quality_details`, `create_quality_rule`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Pausa crítica de aprobación:** `create_quality_rule` **nunca** se llama sin confirmación explícita del usuario. El silencio o la ambigüedad no son aprobación. La aprobación de un lote previo en la misma conversación no vale para un lote nuevo.
- **La validación SQL es obligatoria, no opcional.** Solo reglas cuyas queries se han ejecutado con éxito pueden formar parte del plan presentado al usuario.
- **Nunca uses min/max actuales de la EDA como thresholds de validity.** Los thresholds vienen de la lógica de negocio; la EDA solo parametriza y prioriza.
- **El default de medición** es `percentage` + `exact` (=100% OK, !=100% KO). Las otras cuatro combinaciones (count/exact, percentage/range, count/range) se ofrecen cuando el usuario lo pide.
- **El timezone de scheduling** es `Europe/Madrid` por defecto salvo que el usuario pida otro. Las expresiones cron de frecuencia muy baja (cada segundo/minuto) se bloquean.
- **La ejecución secuencial es intencionada** para que el usuario pueda interrumpir si algo va mal.
