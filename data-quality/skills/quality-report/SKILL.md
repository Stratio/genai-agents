---
name: quality-report
description: Generar un informe formal de cobertura de calidad del dato en el formato que elija el usuario (chat, PDF, DOCX o Markdown en disco). Usar cuando el usuario quiera un documento o presentacion con el estado actual de la calidad, despues de ejecutar assess-quality o create-quality-rules.
argument-hint: [formato: chat|pdf|docx|md] [nombre-fichero (opcional)]
---

# Skill: Generacion de Informe de Calidad

Workflow para generar un informe estructurado con el estado de cobertura de calidad del dato.

## 1. Prerequisitos y Datos del Informe

Esta skill necesita datos de calidad para generar el informe. Verificar si ya existen en la conversacion actual:

**Si se ejecuto `assess-quality` o `create-quality-rules` previamente**: usar esos datos directamente. Esto incluye tanto reglas creadas desde el flujo de gaps (Flujo A) como reglas concretas creadas directamente por el usuario (Flujo B de `create-quality-rules`).

**Si NO hay datos previos**: ejecutar primero la skill `assess-quality` con el scope indicado por el usuario, luego continuar con esta skill.

### Datos a recopilar para el informe

Si los datos ya estan en contexto, extraerlos directamente. Si faltan, obtenerlos con llamadas MCP en paralelo:

```
Paralelo:
  A. get_tables_quality_details(domain_name, tablas)
  B. get_table_columns_details(domain_name, tabla)  [por cada tabla]
  C. get_quality_rule_dimensions(collection_name=domain_name)
```

## 2. Seleccion de Formato

Si el usuario no ha especificado formato, preguntar con opciones:

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

Si se ejecuto `create-quality-rules` antes, incluir:
- Lista de reglas creadas con su SQL
- Cobertura antes y despues (solo si se ejecuto `assess-quality` previamente; para reglas del Flujo B sin assess previo, omitir la comparacion de cobertura)

**Para reglas del Flujo B (regla concreta)**: indicar que fueron solicitadas directamente por el usuario, incluir la logica de negocio descrita y el resultado de la validacion SQL (registros que pasan / total, % esperado).

### Seccion 6 — Recomendaciones y Proximos Pasos

- Reglas KO/WARNING a investigar con prioridad
- Gaps criticos pendientes de cubrir
- Estimation de esfuerzo para cobertura completa

## 4. Generacion por Formato

### Formato: Chat

Generar directamente el informe en markdown dentro de la respuesta del chat. Seguir la estructura de la seccion 3 con headers, tablas y listas bien formateadas.

No ejecutar Python ni crear archivos.

### Formato: Markdown en disco

1. Construir el contenido del informe en markdown siguiendo la estructura de la seccion 3
2. Determinar la ruta de salida:
   - Si el usuario indico un nombre: usar ese nombre (anadir .md si no lo tiene)
   - Si no: `output/quality-report-[dominio]-[YYYY-MM-DD].md`
3. Obtener la ruta absoluta del directorio output:
   ```bash
   mkdir -p output/ && readlink -f output/
   ```
   Usar el resultado (p.ej. `/home/user/session/output`) como prefijo absoluto para el Write tool.
4. Escribir el archivo en `<ruta-absoluta>/quality-report-[dominio]-[YYYY-MM-DD].md` (ruta absoluta requerida por el Write tool)

### Formato: PDF

1. Verificar que el entorno virtual existe y tiene las dependencias instaladas:
   ```bash
   bash setup_env.sh
   ```
2. Preparar el payload JSON con todos los datos del informe y guardarlo en disco:
   - Obtener la ruta absoluta del directorio output:
     ```bash
     mkdir -p output/ && readlink -f output/
     ```
     Usar el resultado como prefijo para el Write tool (p.ej. `/home/user/session/output`).
   - Escribir el contenido JSON en `<ruta-absoluta>/report-input.json` siguiendo **exactamente** este schema (los campos que falten quedan como `null` o lista vacía `[]`):

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
             "column": "<columna>",
             "dimension": "<dimension ausente>",
             "priority": "<CRITICO|ALTO|MEDIO|BAJO>",
             "description": "<descripcion del gap>"
           }
         ]
       }
     ],
     "rules_created": [],
     "recommendations": ["<recomendacion 1>", "..."]
   }
   ```

   **Notas de mapeo desde los datos de assess-quality:**
   - `summary.tables_analyzed`: número de tablas en el scope
   - `summary.rules_total`: total de reglas existentes en la coleccion
   - `summary.coverage_estimate`: porcentaje estimado (dimensiones cubiertas / total posibles)
   - `tables[].completeness/uniqueness/validity/consistency`: estado de cobertura de cada dimension para esa tabla (`OK` si hay regla activa, `Gap` si no hay ninguna, `Parcial` si hay alguna pero no completa)
   - `tables[].gaps[].priority`: `CRITICO` para PK/FK sin regla, `ALTO` para columnas clave, `MEDIO` para resto
3. Determinar la ruta de salida:
   - Si el usuario indico un nombre: usar ese
   - Si no: `output/quality-report-[dominio]-[YYYY-MM-DD].pdf`
4. Ejecutar el generador usando el Python del venv directamente (sin activar):
   ```bash
   .venv/bin/python tools/quality_report_generator.py \
     --format pdf \
     --output "output/quality-report-[dominio]-[fecha].pdf" \
     --input-file output/report-input.json
   ```
5. Verificar que el archivo se ha generado correctamente
6. Informar al usuario de la ruta del archivo

### Formato: DOCX

Mismo proceso que PDF pero con `--format docx` y extension `.docx`. El archivo temporal `output/report-input.json` puede reutilizarse si ya fue escrito en el paso PDF; si no, crearlo siguiendo el mismo proceso del paso 2 de PDF.

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
