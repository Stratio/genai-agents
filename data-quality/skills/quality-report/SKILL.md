---
name: quality-report
description: Generar un informe formal de cobertura de calidad del dato en el formato que elija el usuario (chat, PDF, DOCX o Markdown en disco). Usar cuando el usuario quiera un documento o presentacion con el estado actual de la calidad, despues de evaluar la cobertura o crear reglas de calidad.
argument-hint: [formato: chat|pdf|docx|md] [nombre-fichero (opcional)]
---

# Skill: Generacion de Informe de Calidad

Workflow para generar un informe estructurado con el estado de cobertura de calidad del dato.

## 1. Prerequisitos y Datos del Informe

Esta skill necesita datos de calidad para generar el informe. Verificar si ya existen en la conversacion actual:

**Si ya existen datos de evaluacion de cobertura o de creacion de reglas en la conversacion**: usar esos datos directamente. Esto incluye tanto reglas creadas desde el flujo de gaps (Flujo A) como reglas concretas creadas directamente por el usuario (Flujo B).

**Si NO hay datos de cobertura en el contexto** (inventario de reglas, gaps, EDA): es necesario realizar primero una evaluacion completa del scope solicitado antes de generar el informe. Indicar al usuario y detenerse.

### Datos a recopilar para el informe

Si los datos ya estan en contexto, extraerlos directamente. Si faltan, obtenerlos con llamadas MCP en paralelo:

```
Paralelo:
  A. get_tables_quality_details(domain_name, tablas)
  B. get_table_columns_details(domain_name, tabla)  [por cada tabla]
  C. get_quality_rule_dimensions(collection_name=domain_name)
```

## 2. Seleccion de Formato

Si el usuario no ha especificado formato, preguntar al usuario con opciones siguiendo la convencion de preguntas al usuario:

```
¿En que formato quieres el informe?
  1. Chat — resumen estructurado en esta conversacion (sin archivo)
  2. PDF — documento formal descargable
  3. DOCX — documento Word editable
  4. Markdown — archivo .md en disco
```

Si el usuario ha especificado formato en los argumentos o en el mensaje, usar ese directamente.

## 3. Estructura del Informe

El informe tiene la misma estructura independientemente del formato:

### Portada / Cabecera
- Titulo: "Informe de Cobertura de Calidad del Dato"
- Dominio / Coleccion: [nombre]
- Scope: [dominio completo / tabla(s) especifica(s)]
- Fecha de generacion: [hoy]
- Agente: Data Quality Expert

### Seccion 1 — Resumen Ejecutivo
- Tablas analizadas: N
- Reglas de calidad existentes: N
- Cobertura global estimada: XX%
- Reglas en estado OK: N | KO: N | WARNING: N | Sin ejecutar: N
- Gaps identificados: N criticos, N moderados, N bajos
- Reglas creadas en esta sesion (si aplica): N

### Seccion 2 — Cobertura por Tabla

Tabla matricial (incluir dimensiones estandar y propias del dominio):
```
| Tabla | Completeness | Uniqueness | Validity | Consistency | Otras Dimensiones | Cobertura |
```

Con leyenda de iconos o colores (segun formato).

### Seccion 3 — Detalle de Reglas Existentes

Por cada tabla, listar sus reglas:
```
| Regla | Dimension | Estado | % Pass | Descripcion |
```

Destacar (negrita o color rojo) las reglas en KO o WARNING.

### Seccion 4 — Gaps Identificados

Lista priorizada de gaps:
- Para cada gap: tabla, columna, dimension ausente, impacto estimado, recomendacion

### Seccion 5 — Reglas Creadas en esta Sesion (si aplica)

Si se crearon reglas de calidad en esta sesion, incluir:
- Lista de reglas creadas con su SQL
- Cobertura antes y despues (solo si se realizo una evaluacion de cobertura previamente; para reglas del Flujo B sin evaluacion previa, omitir la comparacion de cobertura)

**Para reglas del Flujo B (regla concreta)**: indicar que fueron solicitadas directamente por el usuario, incluir la logica de negocio descrita, el resultado de la validacion SQL (registros que pasan / total, % o conteo) y el estado calculado (OK / KO / WARNING / SIN_DATOS) basado en la configuracion de medicion aplicada (measurement_type + threshold_mode + umbrales).

**Para reglas del Flujo A (gaps)**: incluir el resultado de la validacion SQL con el estado calculado. Si la validacion mostro KO o WARNING, destacarlo visualmente (negrita) como dato a revisar.

### Seccion 6 — Recomendaciones y Proximos Pasos

- Reglas KO/WARNING a investigar con prioridad
- Gaps criticos pendientes de cubrir
- Estimation de esfuerzo para cobertura completa

## 4. Generacion por Formato

### Formato: Chat

Generar directamente el informe en markdown dentro de la respuesta del chat. Seguir la estructura de la seccion 3 con headers, tablas y listas bien formateadas.

No ejecutar Python ni crear archivos.

### Formatos de archivo: PDF, DOCX y Markdown en disco

Los tres formatos de archivo (PDF, DOCX, MD) usan el mismo generador Python y el mismo fichero `report-input.json`. El proceso es identico salvo el flag `--format` y la extension del fichero de salida.

#### Paso 1 — Verificar entorno

```bash
bash setup_env.sh
```

#### Paso 2 — Preparar report-input.json

Obtener la ruta absoluta del directorio output:
```bash
mkdir -p output/ && readlink -f output/
```

Escribir `<ruta-absoluta>/report-input.json` con el schema exacto que sigue. **Los nombres de campo son literales — el generador los lee con `data.get("campo")` y devuelve `-` si no existen.**

**Errores comunes a evitar (producen informe en blanco):**
- NO `report_title` → `title`
- NO `report_date` / `date` → `generated_at`
- NO `executive_summary` → `summary`
- NO `total_rules` / `rules_count` → `summary.rules_total`
- NO `rules_pending` / `rules_not_run` → `summary.rules_not_executed`
- NO `quality_rules` → `tables[].rules`
- NO `coverage_by_dimension` (objeto anidado) → campos planos `tables[].completeness`, `tables[].uniqueness`, etc.
- NO prioridades en español (`Alta/Media/Baja`) → `CRITICO|ALTO|MEDIO|BAJO`
- NO `recommendations` como array de objetos → array de **strings** planos
- NO `calculated_status` en `rules_created` → `status`

```json
{
  "title": "Informe de Cobertura de Calidad del Dato — <tabla> — <dominio>",
  "domain": "<domain_name>",
  "scope": "<tabla(s) o 'Dominio completo'>",
  "generated_at": "<YYYY-MM-DD>",
  "summary": {
    "tables_analyzed": <N>,
    "rules_total": <N>,
    "rules_ok": <N>,
    "rules_ko": <N>,
    "rules_warning": <N>,
    "rules_not_executed": <N>,
    "coverage_estimate": "<XX%>",
    "gaps_critical": <N>,
    "gaps_moderate": <N>,
    "gaps_low": <N>,
    "rules_created_this_session": <N o null>
  },
  "tables": [
    {
      "name": "<tabla>",
      "coverage_estimate": "<XX%>",
      "completeness": "<OK|Gap|Parcial|N/A>",
      "uniqueness": "<OK|Gap|Parcial|N/A>",
      "validity": "<OK|Gap|Parcial|N/A>",
      "consistency": "<OK|Gap|Parcial|N/A>",
      "rules": [
        {
          "name": "<nombre-regla>",
          "dimension": "<dimension>",
          "status": "<OK|KO|WARNING>",
          "pass_pct": <0-100 o null>,
          "description": "<descripcion>"
        }
      ],
      "gaps": [
        {
          "column": "<columna o '—' si aplica a la tabla>",
          "dimension": "<dimension ausente>",
          "priority": "<CRITICO|ALTO|MEDIO|BAJO>",
          "description": "<descripcion del gap>"
        }
      ]
    }
  ],
  "rules_created": [
    {
      "name": "<nombre-regla>",
      "table": "<tabla>",
      "dimension": "<completeness|uniqueness|validity|consistency|...>",
      "status": "<created|OK|KO|WARNING|SIN_DATOS>"
    }
  ],
  "recommendations": ["<recomendacion 1 como string plano>", "<recomendacion 2>"]
}
```

**Notas de mapeo desde los datos de evaluacion de cobertura:**
- `summary.rules_total` ← total de reglas existentes en la coleccion (no solo las ejecutadas)
- `summary.rules_not_executed` ← reglas sin resultado aun (pendientes)
- `summary.gaps_critical` ← gaps con priority `CRITICO`; `gaps_moderate` ← `ALTO`; `gaps_low` ← `MEDIO` + `BAJO`
- `tables[].completeness/uniqueness/validity/consistency` ← `OK` si hay regla activa, `Gap` si ninguna, `Parcial` si incompleta, `N/A` si no aplica
- `tables[].rules[].status` ← para reglas sin ejecutar usar `WARNING` (nunca "Pendiente" ni "Sin ejecutar")
- `tables[].gaps[].priority` ← `CRITICO` para PK/FK sin regla, `ALTO` para columnas clave, `MEDIO` para resto, `BAJO` para dimensiones opcionales
- `rules_created[].status` ← usar `"created"` para reglas recien creadas en esta sesion sin validacion; `OK|KO|WARNING|SIN_DATOS` si se ejecuto validacion SQL

#### Paso 3 — Determinar ruta de salida

- Si el usuario indico un nombre: usar ese (con la extension correcta)
- Si no:
  - PDF: `output/quality-report-[dominio]-[YYYY-MM-DD].pdf`
  - DOCX: `output/quality-report-[dominio]-[YYYY-MM-DD].docx`
  - MD: `output/quality-report-[dominio]-[YYYY-MM-DD].md`

#### Paso 4 — Validar el JSON (OBLIGATORIO antes de ejecutar el generador)

```bash
.venv/bin/python scripts/validate_report_input.py output/report-input.json
```

- Si termina con `[OK]`: continuar al paso 5.
- Si termina con `[VALIDATION FAILED]`: leer cada error, corregir el `report-input.json` y volver a ejecutar la validacion hasta que pase sin errores. **No ejecutar el generador con un JSON invalido** — producira un informe en blanco sin avisar.

#### Paso 5 — Ejecutar el generador

```bash
.venv/bin/python scripts/quality_report_generator.py \
  --format <pdf|docx|md> \
  --output "output/quality-report-[dominio]-[fecha].<ext>" \
  --input-file output/report-input.json
```

Si el usuario pide PDF y DOCX en la misma sesion, el `report-input.json` puede reutilizarse — ejecutar el generador dos veces con distinto `--format` y `--output`.

## 5. Verificacion Post-Generacion

Para formatos de archivo (PDF, DOCX, MD en disco):
1. Verificar que el archivo existe: `ls -lh output/[nombre-archivo]`
2. Informar al usuario: nombre del archivo, ruta completa, tamaño
3. Si la generacion fallo: mostrar el error y ofrecer alternativa en chat

## 6. Mensaje Final al Usuario

Tras generar el informe, presentar en el chat:
- Confirmacion de generacion (o el informe si es formato chat)
- Ruta del archivo (si aplica)
- Resumen de 2-3 puntos clave del informe
- Pregunta de si desea algo mas (crear reglas de los gaps, ampliar scope, etc.)
