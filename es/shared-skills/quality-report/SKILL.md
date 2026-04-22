---
name: quality-report
description: "Generar un informe formal de cobertura de calidad del dato en el formato que elija el usuario (chat, PDF, DOCX o Markdown en disco). Usar cuando el usuario quiera un documento o presentación con el estado actual de la calidad, después de evaluar la cobertura o crear reglas de calidad."
argument-hint: "[formato: chat|pdf|docx|md] [nombre-fichero (opcional)]"
---

# Skill: Generación de Informe de Calidad

Workflow para generar un informe estructurado con el estado de cobertura de calidad del dato.

## 1. Prerequisitos y Datos del Informe

Esta skill necesita datos de calidad para generar el informe. Verificar si ya existen en la conversación actual:

**Si ya existen datos de evaluación de cobertura o de creación de reglas en la conversación**: usar esos datos directamente. Esto incluye tanto reglas creadas desde el flujo de gaps (Flujo A) como reglas concretas creadas directamente por el usuario (Flujo B).

**Si NO hay datos de cobertura en el contexto** (inventario de reglas, gaps, EDA): es necesario realizar primero una evaluación completa del scope solicitado antes de generar el informe. Indicar al usuario y detenerse.

### Datos a recopilar para el informe

Si los datos ya están en contexto, extraerlos directamente. Si faltan, obtenerlos con llamadas MCP en paralelo:

```
Paralelo:
  A. get_tables_quality_details(domain_name, tablas)
  B. get_table_columns_details(domain_name, tabla)  [por cada tabla]
  C. get_quality_rule_dimensions(collection_name=domain_name)
```

## 2. Selección de Formato

Si el usuario no ha especificado formato, preguntar al usuario con opciones siguiendo la convención de preguntas al usuario:

```
¿En que formato quieres el informe?
  1. Chat — resumen estructurado en esta conversación (sin archivo)
  2. PDF — documento formal descargable
  3. DOCX — documento Word editable
  4. Markdown — archivo .md en disco
```

Si el usuario ha especificado formato en los argumentos o en el mensaje, usar ese directamente.

## 3. Estructura del Informe

El informe tiene la misma estructura independientemente del formato:

### Portada / Cabecera
- Título: "Informe de Cobertura de Calidad del Dato"
- Dominio / Colección: [nombre]
- Scope: [dominio completo / tabla(s) específica(s)]
- Fecha de generación: [hoy]
- Agente: Data Quality Expert

### Sección 1 — Resumen Ejecutivo
- Tablas analizadas: N
- Reglas de calidad existentes: N
- Cobertura global estimada: XX%
- Reglas en estado OK: N | KO: N | WARNING: N | Sin ejecutar: N
- Gaps identificados: N criticos, N moderados, N bajos
- Reglas creadas en esta sesión (si aplica): N

### Sección 2 — Cobertura por Tabla

Tabla matricial (incluir dimensiones estándar y propias del dominio):
```
| Tabla | Completeness | Uniqueness | Validity | Consistency | Otras Dimensiones | Cobertura |
```

Con leyenda de iconos o colores (según formato).

### Sección 3 — Detalle de Reglas Existentes

Por cada tabla, listar sus reglas:
```
| Regla | Dimensión | Estado | % Pass | Descripción |
```

Destacar (negrita o color rojo) las reglas en KO o WARNING.

### Sección 4 — Gaps Identificados

Lista priorizada de gaps:
- Para cada gap: tabla, columna, dimensión ausente, impacto estimado, recomendación

### Sección 5 — Reglas Creadas en esta Sesión (si aplica)

Si se crearon reglas de calidad en esta sesión, incluir:
- Lista de reglas creadas con su SQL
- Cobertura antes y después (solo si se realizo una evaluación de cobertura previamente; para reglas del Flujo B sin evaluación previa, omitir la comparación de cobertura)

**Para reglas del Flujo B (regla concreta)**: indicar que fueron solicitadas directamente por el usuario, incluir la lógica de negocio descrita, el resultado de la validación SQL (registros que pasan / total, % o conteo) y el estado calculado (OK / KO / WARNING / SIN_DATOS) basado en la configuración de medición aplicada (measurement_type + threshold_mode + umbrales).

**Para reglas del Flujo A (gaps)**: incluir el resultado de la validación SQL con el estado calculado. Si la validación mostro KO o WARNING, destacarlo visualmente (negrita) como dato a revisar.

### Sección 6 — Recomendaciones y Próximos Pasos

- Reglas KO/WARNING a investigar con prioridad
- Gaps criticos pendientes de cubrir
- Estimación de esfuerzo para cobertura completa

## 4. Generación por Formato

### Formato: Chat

Generar directamente el informe en markdown dentro de la respuesta del chat. Seguir la estructura de la sección 3 con headers, tablas y listas bien formateadas.

No ejecutar Python ni crear archivos.

### Formatos de archivo: PDF, DOCX y Markdown en disco

Los tres formatos de archivo (PDF, DOCX, MD) usan el mismo generador Python y el mismo fichero `report-input.json`. El proceso es idéntico salvo el flag `--format` y la extensión del fichero de salida.

#### Paso 1 — Verificar entorno

El stack Python (`weasyprint`, `jinja2`, `markdown`, `beautifulsoup4`, `python-docx`) lo provee el entorno (imagen del sandbox Stratio Cowork o, en dev local, tu venv). Verificar con `python3 -c "import weasyprint, jinja2, markdown, bs4, docx"`. Si algún import falla, ejecutar `pip install <pkg>` en el entorno actual.

#### Paso 2 — Determinar la carpeta del informe

Se replica la convención de carpeta usada por los informes de análisis para que cada informe de calidad viva en su propio directorio autocontenido junto con su JSON de entrada y los artefactos generados.

1. Construir el nombre de carpeta: `YYYY-MM-DD_HHMM_quality_<slug>` donde `<slug>` es el dominio o scope normalizado (ASCII en minúsculas, acentos eliminados, espacios reemplazados por guion bajo, máximo 30 caracteres). Ejemplo: `2026-04-20_1530_quality_semantic_analiticabanca`.
2. Crear el directorio: `mkdir -p "output/<carpeta>/"` y después `readlink -f "output/<carpeta>/"` para obtener la ruta absoluta. Todos los archivos producidos por esta skill (JSON de entrada, PDF, DOCX, Markdown) van dentro de esta carpeta — nunca directamente bajo `output/`.
3. Si el usuario ya tiene una carpeta de análisis activa en esta sesión y pide expresamente almacenar el informe de calidad junto al análisis, reutilizar esa carpeta en lugar de crear una nueva.

#### Paso 3 — Preparar report-input.json

Escribir `<ruta-absoluta>/<carpeta>/report-input.json` con el schema exacto que sigue. **Los nombres de campo son literales — el generador los lee con `data.get("campo")` y devuelve `-` si no existen.**

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

**Notas de mapeo desde los datos de evaluación de cobertura:**
- `summary.rules_total` ← total de reglas existentes en la colección (no solo las ejecutadas)
- `summary.rules_not_executed` ← reglas sin resultado aún (pendientes)
- `summary.gaps_critical` ← gaps con priority `CRITICO`; `gaps_moderate` ← `ALTO`; `gaps_low` ← `MEDIO` + `BAJO`
- `tables[].completeness/uniqueness/validity/consistency` ← `OK` si hay regla activa, `Gap` si ninguna, `Parcial` si incompleta, `N/A` si no aplica
- `tables[].rules[].status` ← para reglas sin ejecutar usar `WARNING` (nunca "Pendiente" ni "Sin ejecutar")
- `tables[].gaps[].priority` ← `CRITICO` para PK/FK sin regla, `ALTO` para columnas clave, `MEDIO` para resto, `BAJO` para dimensiones opcionales
- `rules_created[].status` ← usar `"created"` para reglas recién creadas en esta sesión sin validación; `OK|KO|WARNING|SIN_DATOS` si se ejecutó validación SQL

#### Paso 4 — Determinar los nombres de los artefactos

Todos los artefactos viven **dentro** de la carpeta del Paso 2. Los nombres llevan el `<slug>` descriptivo (la parte del nombre de carpeta tras el timestamp) como prefijo para que sigan siendo reconocibles tras la descarga.

- Si el usuario indicó un nombre: usar ese (con la extensión correcta), siempre dentro de la carpeta.
- Si no:
  - PDF: `output/<carpeta>/<slug>-quality-report.pdf`
  - DOCX: `output/<carpeta>/<slug>-quality-report.docx`
  - MD: `output/<carpeta>/<slug>-quality-report.md`

#### Paso 5 — Validar el JSON (OBLIGATORIO antes de ejecutar el generador)

```bash
python3 scripts/validate_report_input.py output/<carpeta>/report-input.json
```

- Si termina con `[OK]`: continuar al paso 6.
- Si termina con `[VALIDATION FAILED]`: leer cada error, corregir el `report-input.json` y volver a ejecutar la validación hasta que pase sin errores. **No ejecutar el generador con un JSON invalido** — producira un informe en blanco sin avisar.

#### Paso 6 — Ejecutar el generador

```bash
python3 scripts/quality_report_generator.py \
  --format <pdf|docx|md> \
  --output "output/<carpeta>/<slug>-quality-report.<ext>" \
  --input-file "output/<carpeta>/report-input.json" \
  --lang <código_idioma_usuario>
```

**Opcional — tono visual** (afecta solo a PDF y DOCX; el formato Markdown es neutro e ignora este flag):

```bash
python3 scripts/quality_report_generator.py \
  --format pdf \
  --output "output/<carpeta>/<slug>-quality-report.pdf" \
  --input-file "output/<carpeta>/report-input.json" \
  --lang <código_idioma_usuario> \
  --tone <default|technical-minimal|executive-editorial|forensic>
```

Los tonos cambian la paleta de acento y el emparejamiento tipográfico del documento generado:

- `default` — preserva la paleta histórica (Arial body, acento azul naval). Se usa cuando se omite `--tone`.
- `technical-minimal` — IBM Plex Serif para body, IBM Plex Sans para display y IBM Plex Mono para datos tabulares; acento azul frío. Adecuado para audiencias de ingeniería o revisiones de incidencias.
- `executive-editorial` — Crimson Pro body con Instrument Serif display; acento oxblood cálido sobre crema. Adecuado para resúmenes a nivel de comité o informes trimestrales.
- `forensic` — IBM Plex Mono body con Plex Serif display; acento rojo profundo sobre hueso. Adecuado para documentación estilo auditoría donde cada cifra está para ser escrutada.

Consulta `skills-guides/visual-craftsmanship.md` para los principios estéticos compartidos (roles de paleta, emparejamiento tipográfico, anti-patrones, checklist de artesanía).

**Nota sobre disponibilidad de fuentes**: los tonos no-default referencian familias (IBM Plex Serif/Sans/Mono, Crimson Pro, Instrument Serif, JetBrains Mono). Deben estar instaladas a nivel de sistema o entregadas por el entorno; si WeasyPrint no puede resolver una familia hace fallback silencioso y el tono visible no cambia. En caso de duda, mantén `--tone default` (Arial) o instala la familia vía el entorno del agente.

**Idioma de los labels estáticos** (títulos de sección, nombres de columnas de tabla, footer, atributo HTML `lang`). Orden de resolución (mayor prioridad primero):

1. `--labels-json '{...}'` en la línea de comandos — override por clave.
2. `"labels": {...}` dentro del JSON input — override por clave.
3. `--lang <código>` en la línea de comandos — selecciona del catálogo.
4. `"lang": "<código>"` dentro del JSON input — selecciona del catálogo.
5. Fichero `.agent_lang` en la raíz del agente (escrito al empaquetar) — idioma por defecto del paquete.
6. `"en"` como fallback final.

**Regla práctica**: pasar `--lang <código>` con el idioma del usuario actual (el mismo que estás usando en el chat). Los idiomas del catálogo hoy son `en` y `es`; códigos desconocidos hacen fallback a inglés por clave. Si necesitas un label que el catálogo no trae en el idioma del usuario (p. ej. usuario en francés), pasa las traducciones vía `--labels-json` o el campo `"labels"` del JSON.

Si el usuario pide PDF y DOCX en la misma sesión, el `report-input.json` puede reutilizarse — ejecutar el generador dos veces con distinto `--format` y `--output`.

## 5. Verificación Post-Generación

Para formatos de archivo (PDF, DOCX, MD en disco):
1. Verificar que los archivos existen: `ls -lh output/<carpeta>/`
2. Informar al usuario: ruta de la carpeta, nombres de los artefactos y tamaño de cada uno
3. Si la generación fallo: mostrar el error y ofrecer alternativa en chat

## 6. Mensaje Final al Usuario

Tras generar el informe, presentar en el chat:
- Confirmación de generación (o el informe si es formato chat)
- Ruta del archivo (si aplica)
- Resumen de 2-3 puntos clave del informe
- Pregunta de si desea algo más (crear reglas de los gaps, ampliar scope, etc.)
