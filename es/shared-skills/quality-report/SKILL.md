---
name: quality-report
description: "Generar un informe formal de cobertura de calidad del dato en el formato que elija el usuario — chat, PDF, DOCX, PPTX, dashboard web, informe web, póster o matriz de cobertura en XLSX. Delega la generación de ficheros a las writer skills del agente (pdf-writer, docx-writer, pptx-writer, web-craft, canvas-craft, xlsx-writer) más la skill centralizada de theming; el formato chat funciona en solitario, los formatos-fichero solo se ofrecen si el agente host declara la writer skill correspondiente. Usar cuando el usuario quiera un informe de calidad, un resumen de cobertura, un dashboard de calidad, un deck ejecutivo de hallazgos de calidad, o cualquier entregable que consolide resultados de assess-quality."
argument-hint: "[formato: chat|pdf|docx|pptx|web|poster|xlsx] [nombre-fichero (opcional)]"
---

# Skill: Generación de Informe de Calidad

Workflow guidance-first para producir un informe estructurado de cobertura de calidad del dato. Esta skill orquesta: recopila y compone el contenido, resuelve el tema de marca y delega la generación del formato final a las skills de escritura del agente. Solo el formato Chat lo produce directamente esta skill.

## 1. Prerequisitos y datos del informe

Esta skill necesita datos de calidad para generar el informe. Verificar si ya existen en la conversación actual:

**Si ya existen datos de evaluación de cobertura o de creación de reglas en la conversación**: usar esos datos directamente. Esto incluye tanto reglas creadas desde el flujo de gaps (Flujo A) como reglas concretas creadas directamente por el usuario (Flujo B).

**Si NO hay datos de cobertura en el contexto** (inventario de reglas, gaps, EDA): es necesario realizar primero una evaluación completa del scope solicitado antes de generar el informe. Indicar al usuario y detenerse.

### Datos a recopilar para el informe

Si los datos ya están en contexto, extraerlos directamente. Si faltan, obtenerlos con llamadas MCP en paralelo:

```
Paralelo:
  A. get_tables_quality_details(domain_name, tablas)
  B. get_table_columns_details(domain_name, tabla)  [por cada tabla]
  C. get_quality_rule_dimensions(domain_name=domain_name)
  D. get_critical_data_elements(collection_name=domain_name)  [si no están ya en contexto]
```

## 2. Selección de formato

### 2.1 Pre-check — disponibilidad de writer skills (PRIMER PASO OBLIGATORIO)

Antes de ofrecer opciones de formato de fichero, confirmar qué writer skills declara el agente host. Si el agente host NO declara `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` ni `xlsx-writer`, el único formato disponible es Chat — saltar el §2.2 entero y proceder directamente al §5.1 (Chat).

Este pre-check es bloqueante: NO ofrecer formatos de fichero que el agente host no puede materializar, y NO intentar cargar una writer skill que el agente host no declara, aunque el usuario insista en un formato de fichero.

### 2.2 Opciones de formato

Si al menos una writer skill está declarada, preguntar al usuario siguiendo la convención de preguntas al usuario. Ofrecer únicamente las opciones cuya skill requerida esté declarada por el agente:

- **Chat** — resumen estructurado en esta conversación (sin fichero). Siempre disponible.
- **PDF** — documento tipográfico multipágina. Requiere `pdf-writer`.
- **DOCX** — documento Word editable. Requiere `docx-writer`.
- **PowerPoint** — deck ejecutivo (16:9 por defecto). Requiere `pptx-writer`.
- **Dashboard web** — HTML interactivo con filtros, KPI cards y tablas ordenables. Requiere `web-craft`.
- **Informe web / Artículo web** — página HTML autocontenida, layout narrativo o editorial. Requiere `web-craft`.
- **Póster / Infografía** — resumen visual de una página para imprenta o publicación. Requiere `canvas-craft`.
- **Excel (XLSX)** — libro tabular de cobertura multi-hoja (portada + matriz de cobertura con formato condicional + detalle de reglas + gaps + recomendaciones). Requiere `xlsx-writer`.

Se admite selección múltiple (el mismo contenido se materializa en varios formatos reutilizando el mismo `quality-report.md` interno).

Si el usuario ya especificó el formato en los argumentos o mensaje, usarlo directamente y saltar la pregunta.

## 3. Estructura del informe

El informe tiene la misma estructura independientemente del formato. Seis secciones canónicas en este orden fijo:

1. **Portada / Cabecera** — título, dominio, scope, fecha de generación, nombre del agente.
2. **Resumen ejecutivo** — tablas analizadas, reglas totales, desglose OK/KO/WARNING/NOT_EXECUTED, coverage estimado, gaps por prioridad (CRITICO/ALTO/MEDIO/BAJO), reglas creadas en esta sesión.
3. **Cobertura por tabla** — matriz tablas × dimensiones con icono/color por estado.
4. **Detalle de reglas** — por tabla: reglas con nombre, dimensión, status, % pass, descripción. KO y WARNING resaltados visualmente.
5. **Gaps identificados** — lista priorizada con tabla, columna, dimensión, prioridad, descripción y recomendación.
6. **Recomendaciones y próximos pasos** — bullets priorizados.

Si el usuario creó reglas vía `create-quality-rules` en la conversación actual, se incluye una sección opcional **Reglas creadas en esta sesión** entre §4 y §5.

Para el contrato completo de layout (iconografía, KPI cards, composición por formato, reglas deterministas para auditoría), ver `quality-report-layout.md` en esta misma skill.

## 4. Decisiones de branding

Antes de invocar cualquier writer skill para un formato de fichero, fijar el tema siguiendo la cascada de branding del agente host. Cuando el agente host declara un contrato format→skill con una sub-sección §Decisiones de branding, seguir esa cascada — típicamente 5 niveles: pin → señal explícita → continuidad intra-sesión → preferencia en MEMORY → propuesta curada.

**Default neutro primario para informes de calidad** (cuando ninguna regla de la cascada resuelve a un tema concreto): `forensic-audit`. Encaja con el registro de auditoría de un informe de cobertura y mantiene visualmente estables las re-ejecuciones mes a mes del mismo dataset. La propuesta curada debe preferir temas cuyo descriptor mencione "audit", "technical", "editorial" o "corporate".

Si el usuario pide neutralidad explícita ("no me importa el diseño" / "hazlo neutro" / "sin branding"), aplicar `technical-minimal` como fallback sobrio — máxima contención, salida predecible para contextos no-auditoría.

El tema elegido se registra silenciosamente como última línea del `quality-report.md` interno (p. ej. `theme applied: forensic-audit`). Informativo, no contractual.

## 5. Generación del entregable

### 5.1 Formato Chat

Emitir el informe directamente como markdown en la respuesta actual, siguiendo las seis secciones canónicas de §3. No se produce fichero, no se invoca writer skill, no se ejecuta la cascada de branding.

Cerrar el mensaje con el resumen de 2-3 puntos clave según §7.

### 5.2 Markdown en disco (opcional, trivial)

Si el usuario pide un fichero `.md` en disco (no Chat, no uno de los formatos con writer), escribirlo directamente con la herramienta Write en `output/<carpeta>/<slug>-quality-report.md`. No se invoca writer skill — markdown es texto plano.

Usar la misma convención de carpeta que §5.3.

### 5.3 Formatos de fichero (PDF, DOCX, PPTX, Dashboard web, Informe web, Póster)

1. **Carpeta**: crear `output/YYYY-MM-DD_HHMM_quality_<slug>/` (todos los artefactos viven aquí). `<slug>` = dominio o scope normalizado (ASCII en minúsculas, acentos eliminados, espacios por guiones bajos, máximo 30 caracteres). Ejemplo: `2026-04-24_1530_quality_analiticabanca`.

2. **Tokens de marca (una sola vez, antes de cualquier formato visual)**: cargar la skill centralizada de theming (`brand-kit`) con el tema fijado en §4. El fichero del tema provee el bundle de tokens — colores, tipografía, paleta de gráficos — que consumen las writer skills downstream para que todos los entregables queden coherentes.

3. **Ensamblar el origen del contenido**: escribir `output/<carpeta>/quality-report.md` en el idioma del usuario, con cada sección canónica de §3 utilizando la estructura descrita en `quality-report-layout.md` §10. Cuando una sección no tenga datos, incluir la cabecera y una línea explícita "No se han detectado X" — nunca omitir silenciosamente. Aplicar las reglas de layout determinista de `quality-report-layout.md` §11 (orden de secciones fijo, orden de KPI cards, orden de columnas de la matriz, ordenación de gaps, límites de ítems por formato). Este fichero interno es la única fuente de verdad que consumen las writer skills.

4. **Para cada formato seleccionado, cargar la writer skill correspondiente y producir el entregable. Seguir `quality-report-layout.md` para la composición específica del formato**:

   - **PDF** → cargar `pdf-writer`. Salida: `<slug>-quality-report.pdf`. El entregable debe renderizar las seis secciones canónicas, aplicar tokens de marca, respetar el patrón de KPI cards de la guía §5 y cumplir las reglas de composición PDF de §6.1 (cabecera/pie en cada página, repetir cabecera de matriz al saltar de página, orientación vertical salvo si el conteo de dimensiones es >8).
   - **DOCX** → cargar `docx-writer`. Salida: `<slug>-quality-report.docx`. Las mismas seis secciones; usar tablas nativas de Word para la matriz de cobertura y el detalle de reglas para que el usuario pueda editarlas. Preservar estilos de cabecera (`Heading 1`, `Heading 2`, …).
   - **PowerPoint** → cargar `pptx-writer`. Salida: `<slug>-quality-summary.pptx`. 16:9 por defecto; 4:3 solo si el usuario lo pide explícitamente. Objetivo ≤12 slides siguiendo el guion de `quality-report-layout.md` §6.3.
   - **Dashboard web** → cargar `web-craft`. Salida: `<slug>-quality-dashboard.html`. Aplicar el layout específico de calidad de §6.4 (exactamente los cuatro KPI cards de §5, heatmap interactivo de cobertura, filtros por dimensión/status/prioridad, tablas ordenables). Si el agente host también declara una guía general `analytical-dashboard.md`, cargarla en paralelo para que los patrones genéricos de dashboard (filtros globales, Plotly vía CDN, presupuesto de datos, responsive, motion, idioma) apliquen por encima.
   - **Informe web / Artículo web** → cargar `web-craft`. Salida: `<slug>-quality-article.html`. NO aplicar el layout de dashboard de §6.4. Usar artifact class `Page` o `Article`. Renderizar las seis secciones canónicas como página HTML scrollable y autocontenida: headings narrativos, callouts KPI inline, gráficos Plotly de cobertura incrustados como figuras, tablas HTML estáticas (no ordenables). El contenido es el mismo que en los demás formatos; la presentación es editorial, no interactiva.
   - **Póster / Infografía** → cargar `canvas-craft`. Salida: `<slug>-quality-poster.pdf` o `<slug>-quality-poster.png`. Composición de página única según §6.5 (banda superior de KPIs, heatmap central, top 3 gaps + top 3 recomendaciones en columnas laterales, A3 vertical por defecto).
   - **Excel (XLSX)** → cargar `xlsx-writer`. Salida: `<slug>-quality-report.xlsx`. Libro multi-hoja según `quality-report-layout.md` §6.6 (Cover con 4 KPI cards en banda de celdas combinadas, matriz de Coverage como Table nativa con formato condicional para OK/KO/WARNING/NOT_EXECUTED, detalle de Rules agrupado por tabla, Gaps priorizados, opcional Rules-created-this-session, Recomendaciones). Sin fórmulas de Excel (todos los valores son datos mostrados); sin gráficos nativos (la matriz de cobertura es en sí el heatmap). Los tokens de marca aplican solo a colores de fill, bordes y estados — XLSX usa las fuentes del sistema del lector, no fuentes embebidas.

5. **Convención de nombres**: `<slug>` = parte descriptiva del dominio/scope (según paso 1). Los ficheros internos (`quality-report.md`) se mantienen sin prefijo.

6. **Verificar que cada fichero existe en disco con `ls -lh output/<carpeta>/` tras el retorno de cada writer skill.** Si falta alguno, regenerar — NO reportar éxito parcial al usuario.

## 6. Verificación post-generación

Para formatos de fichero:
1. `ls -lh output/<carpeta>/` — confirmar que todos los ficheros esperados están presentes con tamaño no nulo.
2. Si falta alguno o tiene tamaño cero: regenerar ese formato antes de responder al usuario.

## 7. Mensaje final al usuario

Tras la generación, presentar en chat:

- Confirmación de generación (para Chat: el propio informe; para ficheros: path de la carpeta + lista de artefactos con tamaños).
- 2-3 puntos clave del informe (p. ej. gap de cobertura más grande, regla KO más crítica, mejora más relevante frente a un informe previo si existe).
- Pregunta de seguimiento (crear reglas para los gaps detectados, ampliar scope a otras tablas, planificar re-evaluación periódica, etc.).
