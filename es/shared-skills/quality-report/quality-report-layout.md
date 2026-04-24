# Quality Report Layout — Guía

Guía consumida por las writer skills (`pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`) cuando el agente delega un entregable de informe de cobertura de calidad a través de la skill `quality-report`.

Esta guía captura las convenciones que hacen reconocible un informe de cobertura de calidad del dato en cualquier formato: una anatomía estable de seis secciones (portada → resumen ejecutivo → matriz de cobertura → detalle de reglas → gaps → recomendaciones), una iconografía fija para el estado de reglas, KPI cards pensadas para lectura de auditoría y un layout determinista para que el mismo dataset reproduzca el mismo esqueleto mes a mes. Las writer skills aplican su propio oficio por encima — los tokens los da la skill centralizada de theming elegida en la cascada de branding del agente; esta guía aporta los **patrones del informe de calidad**.

## 1. Propósito y alcance

Aplicar esta guía siempre que el agente produzca un informe de cobertura de calidad en un formato de fichero (PDF, DOCX, PPTX, Dashboard web, Póster/Infografía) vía la skill `quality-report`. Saltarla para el formato Chat — la respuesta de chat es markdown libre, no necesita decisiones específicas de formato.

La guía es agnóstica al formato donde puede serlo (misma anatomía en todos) y específica donde el tipo de entregable dicta la composición (§6).

## 2. Secciones canónicas

Cada entregable de fichero contiene estas seis secciones en este orden. Los nombres de sección se renderizan en el idioma del usuario (el agente pasa `lang` a la writer skill); los valores que son códigos (`OK`, `KO`, `WARNING`, `NOT_EXECUTED`, `CRITICO`, `ALTO`, `MEDIO`, `BAJO`) no se traducen.

1. **Portada / Cabecera** — título, dominio, scope (dominio completo o tablas concretas), fecha de generación, agente que produjo el informe.
2. **Resumen ejecutivo** — tablas analizadas, reglas totales, desglose de reglas (OK / KO / WARNING / NOT_EXECUTED), coverage estimado, gaps por criticidad (CRITICO / ALTO / MEDIO / BAJO), reglas creadas en esta sesión (si las hay).
3. **Cobertura por tabla** — matriz: una fila por tabla, columnas por cada dimensión (Completeness, Uniqueness, Validity, Consistency, más cualquier dimensión específica del dominio devuelta por `get_quality_rule_dimensions`) + columna de coverage estimado.
4. **Detalle de reglas** — por tabla: lista de reglas existentes con nombre, dimensión, status, % pass, descripción. KO y WARNING resaltados visualmente (negrita o codificación con `state_danger` / `state_warn`).
5. **Gaps identificados** — lista priorizada: tabla, columna (o `—` si aplica a toda la tabla), dimensión ausente, prioridad, descripción/impacto, recomendación.
6. **Recomendaciones y próximos pasos** — bullets priorizados: reglas KO/WARNING a investigar primero, gaps críticos a cubrir, estimación de esfuerzo para cobertura completa.

Si el usuario ejecutó `create-quality-rules` durante la sesión actual, una sección opcional **Reglas creadas en esta sesión** va entre §4 y §5, con nombre de regla, tabla, dimensión, lógica SQL y status calculado (OK / KO / WARNING / SIN_DATOS / created).

## 3. Iconografía y códigos de estado

El estado de reglas y dimensiones va codificado por color e icono. Las writer skills eligen el renderizado exacto (glifo Unicode en PDF/DOCX, icono CSS en web-craft, glifo tipográfico en canvas-craft) — el mapeo semántico es fijo:

| Estado | Icono (Unicode base) | Token de marca |
|---|---|---|
| `OK` | ✓ (U+2713) | `state_ok` |
| `KO` | ✗ (U+2717) | `state_danger` |
| `WARNING` | ⚠ (U+26A0) | `state_warn` |
| `NOT_EXECUTED` | ○ (U+25CB) | `muted` |

Para celdas de cobertura por dimensión:

| Cobertura | Icono | Token de marca |
|---|---|---|
| Regla completa cubre la dimensión | ✓ | `state_ok` |
| Sin regla para la dimensión | ✗ | `state_danger` |
| Parcial / solo algunas columnas cubiertas | ◐ (U+25D0) | `state_warn` |
| Dimensión no aplicable para la tabla | — | `muted` |

Nunca depender solo del color — combinar siempre icono + etiqueta. Colorblind-safe por contrato: los iconos transmiten el mensaje incluso en impresión en blanco y negro.

## 4. Priorización de gaps

Las prioridades son códigos (`CRITICO`, `ALTO`, `MEDIO`, `BAJO`) — no se traducen. Se renderizan con un peso visual acorde a su severidad:

| Prioridad | Significado | Tratamiento visual |
|---|---|---|
| `CRITICO` | Clave primaria o foránea sin cobertura; regla de negocio core ausente. Bloquea uso seguro del dato. | Negrita, acento `state_danger`, primera en la lista. |
| `ALTO` | Columna descriptiva clave sin cobertura; dimensión de negocio obligatoria ausente. | Peso normal, acento `state_warn`. |
| `MEDIO` | Columna secundaria o dimensión opcional sin regla, pero negocio sigue funcional. | Peso normal, color `ink` por defecto. |
| `BAJO` | Gap cosmético o de bajo impacto (p. ej. validación de formato en un campo de auditoría). | Color `muted`, peso visual bajo. |

Ordenar gaps primero por prioridad, luego por nombre de tabla (alfabético). Dentro de un grupo de prioridad, ordenar por columna (alfabético) para que ejecuciones repetidas produzcan la misma secuencia.

## 5. KPI cards (cabecera del resumen ejecutivo)

Exactamente cuatro KPI cards en la parte superior del Resumen ejecutivo. Orden fijo:

1. **Coverage %** — coverage estimado sobre el scope. Valor formateado como porcentaje. Subtítulo: "sobre N tablas".
2. **Rules OK %** — fracción de reglas ejecutadas que están OK. Valor formateado como porcentaje. Subtítulo: "N de M reglas".
3. **Critical gaps** — conteo de gaps con prioridad `CRITICO`. Valor formateado como entero. Subtítulo: "requieren acción inmediata".
4. **Rules created this session** — conteo de reglas creadas vía `create-quality-rules` en la conversación actual; `—` si ninguna. Subtítulo: "nuevas en este informe".

Cada KPI card contiene:

- **Etiqueta** (una línea corta, idioma del usuario).
- **Valor** (display grande, formateado con locale).
- **Subtítulo** (una línea corta de contexto).
- Opcional: un micro-indicador que muestra si el valor está mejor o peor que un informe previo en la misma carpeta history (si existe). Cuando no hay informe previo, omitir el indicador — no fabricar una tendencia.

Patrón HTML/CSS (para `web-craft`):

```html
<div class="kpi-card" data-kpi="coverage">
  <div class="kpi-label">Cobertura</div>
  <div class="kpi-value">87%</div>
  <div class="kpi-subtitle">sobre 24 tablas</div>
</div>
```

```css
.kpi-card {
  background: var(--bg-alt);
  border-left: 4px solid var(--primary);
  padding: 1.25rem 1.5rem;
  border-radius: 4px;
}
.kpi-value { font-family: var(--font-display); font-size: 2.25rem; }
.kpi-subtitle { color: var(--muted); font-size: 0.875rem; }
```

Para PDF/DOCX, renderizar las cuatro cards como fila de tabla de 4 columnas (o grid 2×2 si el ancho de página es apurado). El valor usa la fuente `display` del tema; la etiqueta y subtítulo usan `body`.

Para PPTX, las KPI cards ocupan la slide 2 (tras la portada), dispuestas horizontalmente. Si el tema declara tipografía `display` + `body`, respetarlas.

Para canvas-craft (Póster), las cuatro KPIs forman la banda superior de la composición — Coverage % dominante, las otras tres apoyándolo.

## 6. Composición por formato

Mismo contenido, distinto encuadre.

### 6.1 PDF (multipágina, tipográfico)

- Cabecera en cada página: nombre de dominio (izquierda) y fecha de generación (derecha), regla fina debajo.
- Pie: número de página (derecha), título del informe (izquierda), regla fina encima.
- Portada a sangre opcional; si no, el informe arranca con el bloque título + metadatos al inicio de la página 1.
- Resumen ejecutivo en página 1 (puede continuar en página 2 si las cuatro KPI cards + un párrafo desbordan). La matriz de cobertura puede ocupar varias páginas — repetir la fila de cabecera al inicio de cada página.
- Detalle de reglas: agrupar por tabla, una sub-cabecera por tabla. Evitar sub-cabeceras huérfanas al final de página.
- No orientación apaisada salvo que el conteo de dimensiones supere 8; en ese caso, solo la matriz de cobertura pasa a apaisada, el resto se queda en vertical.

### 6.2 DOCX (Word editable)

- Usar tablas nativas de Word (no tablas HTML renderizadas como imagen). El revisor las va a editar.
- Misma cabecera/pie/portada que PDF.
- Iconos de estado: preferir glifos Unicode para que el copy-paste desde Word siga siendo legible.
- Preservar estilos de cabecera (`Heading 1`, `Heading 2`, …) para que el usuario pueda regenerar un índice.

### 6.3 PPTX (deck ejecutivo resumen, 16:9)

Objetivo ≤12 slides. Guion:

1. Portada — título, dominio, fecha, agente.
2. Resumen ejecutivo — las cuatro KPI cards dispuestas horizontalmente.
3. Heatmap de cobertura — la matriz de §2.3 como heatmap visual. Una fila por tabla, una columna por dimensión. Celdas coloreadas.
4. Desglose de estado de reglas — tarta o barra apilada (OK / KO / WARNING / NOT_EXECUTED) + números del desglose.
5. Top gaps — lista de los 10 gaps más críticos (prioridad `CRITICO` primero). Una slide.
6. Reglas creadas en esta sesión (si las hay) — lista con extracto SQL y status. Si no, se omite la slide.
7. Recomendaciones — 3–5 bullets de los próximos pasos de mayor impacto.
8. Apéndice (opcional) — inventario completo de reglas si la audiencia ejecutiva pidió detalle.

Relación 16:9 por defecto. Caer a 4:3 solo si el usuario lo pide explícitamente. No incrustar capturas raster de tablas — renderizar tablas PPTX nativas para que el dato quede editable.

### 6.4 Dashboard web (HTML interactivo)

Consumir esta guía de layout **y** la `analytical-dashboard.md` local del agente host si está declarada. La analytical-dashboard provee los patrones genéricos de dashboard (filtros globales, tablas ordenables, KPI cards, Plotly vía CDN); esta guía añade el contenido específico de calidad:

- KPI cards: exactamente los cuatro de §5.
- Matriz de cobertura como heatmap interactivo (Plotly `heatmap` con colorway discreto mapeado a los códigos de estado).
- Filtros: un dropdown para dimensión, uno para status (OK/KO/WARNING/NOT_EXECUTED), uno para prioridad (para la sección de gaps).
- Tabla ordenable para detalle de reglas (columnas: regla, tabla, dimensión, status, % pass).
- Tabla ordenable para gaps (columnas: tabla, columna, dimensión, prioridad, recomendación).

Presupuesto de datos: los informes de calidad son densos pero no transaccionales. Una fila por regla + una fila por gap es lo habitual (<5.000 filas). Incrustar como `DASHBOARD_DATA` directamente — sin pre-agregación en la mayoría de casos.

### 6.5 Póster / Infografía (visual de página única)

- Banda superior: las cuatro KPI cards, Coverage % dominante en el centro.
- Centro: el heatmap de cobertura como visual principal.
- Columna inferior izquierda: top 3 gaps críticos con prioridad + recomendación.
- Columna inferior derecha: top 3 recomendaciones (de §6).
- Formato: A3 vertical por defecto, PDF o PNG de una sola página. Dejar al usuario elegir el tamaño si expresa preferencia.

## 7. Integración con los tokens de marca

El tema fijado en la cascada de branding del agente produce un bundle de tokens. El informe de calidad los consume como cualquier otro entregable:

- `primary` — reglas de sección, borde izquierdo de KPI cards, acentos de portada.
- `accent` — callouts, destacados de KPI cards (con moderación — los informes de calidad se leen como documentos sobrios, no como marketing).
- `ink` — cuerpo de texto.
- `muted` — captions, notas al pie, líneas de subtítulo.
- `rule` — separadores, reglas finas de cabecera/pie, líneas de borde de tabla.
- `bg` — superficie principal / de página.
- `bg_alt` — bandas de tabla (alternancia de filas), fondo de KPI cards.
- `state_ok` / `state_warn` / `state_danger` — iconos de estado de reglas y codificación cromática de prioridad de gaps (ver §3, §4).
- `chart_categorical` — mapeo de colores del heatmap para la matriz de cobertura. Mapear los cuatro estados a posiciones estables:
  - Posición 0 → OK
  - Posición 1 → WARNING
  - Posición 2 → KO
  - Posición 3 → NOT_EXECUTED
- Tipografía: `display` para valores de KPI y H1 de sección; `body` para texto corrido; `mono` para fragmentos SQL y nombres de regla (los nombres de regla suelen llevar underscores — mono lee mejor).

Si el tema declara extensiones `print`, `pdf-writer` y `canvas-craft` las honran (un `paper` crema queda mejor que un `bg` blanco puro sobre papel).

## 8. Idioma

- `lang` lo pasa el agente a cada writer skill. Cada cabecera, etiqueta, subtítulo, label de KPI, título de columna y texto de pie se renderiza en ese idioma.
- El atributo `<html lang="...">` (web-craft) y la propiedad de idioma de DOCX (docx-writer) deben coincidir.
- Los códigos de estado (`OK`, `KO`, `WARNING`, `NOT_EXECUTED`) y códigos de prioridad (`CRITICO`, `ALTO`, `MEDIO`, `BAJO`) NO se traducen — son identificadores canónicos y deben leerse igual en todos los idiomas para que los diffs de auditoría cross-locale alineen.
- Los nombres de dimensión vienen de `get_quality_rule_dimensions` — son específicos de dominio y locale según el modelo de gobernanza; pasarlos tal cual.

`web-craft` debería incluir un objeto `LABELS` siguiendo el patrón de `analytical-dashboard.md` §12 para que las cadenas de UI (nombres de sección, labels de filtros, labels de ordenación) sean fáciles de regenerar en otro idioma.

## 9. Qué NO dicta esta guía

Las writer skills mantienen el control de estas decisiones:

- Tono específico (editorial-serious, forensic-audit, technical-minimal, etc.) — viene del tema.
- Tipografía exacta — viene de `display` / `body` / `mono` en el tema.
- Valores exactos de acento y neutros — vienen del tema.
- Micro-composición de secciones individuales (padding interno de KPI card, layout de portada, estilizado de celdas de tabla, coloreado de SQL) — cada writer skill los diseña según su propio workflow, coherente con el tema.
- Motion, hover, fondos en web-craft — ver `analytical-dashboard.md` §9–§11 y las cinco decisiones de web-craft.
- Transiciones de slide en PPTX, estilo de notas de orador — pptx-writer decide según su workflow.

Esta guía restringe el **contrato del informe de calidad** (qué contiene el informe y en qué orden); las writer skills aportan la **voz visual**.

## 10. Contenido obligatorio del `quality-report.md` interno

El agente compone un `quality-report.md` interno en el idioma del usuario, dentro de `output/YYYY-MM-DD_HHMM_quality_<slug>/`, antes de delegar a cualquier writer skill. Este fichero es la única fuente de verdad que consumen las writer skills. Debe contener las siguientes secciones, incluso si alguna no tiene datos (en ese caso, escribir una frase explícita de "No se han detectado X" en lugar de omitir la cabecera):

- **Portada** — título, dominio, scope, fecha de generación, nombre del agente.
- **Resumen ejecutivo** — tablas analizadas, reglas totales, desglose de reglas (OK / KO / WARNING / NOT_EXECUTED), coverage estimado, desglose de gaps por prioridad, reglas creadas en esta sesión.
- **Cobertura por tabla** — una fila por tabla del scope, con una columna por dimensión y coverage estimado.
- **Detalle de reglas** — agrupado por tabla. Si una tabla no tiene reglas, una línea explícita ("No hay reglas definidas para esta tabla todavía"). Si las tiene, la lista con nombre, dimensión, status, % pass, descripción.
- **Gaps identificados** — lista priorizada. Si no hay gaps, una línea explícita ("No se han detectado gaps en el scope actual").
- **Reglas creadas en esta sesión** — solo si se creó al menos una regla vía `create-quality-rules` en la conversación actual. Si no, se omite la cabecera entera.
- **Recomendaciones y próximos pasos** — al menos un bullet. Si la cobertura es completa y no hay gaps, la recomendación puede ser algo como "Planificar una re-evaluación periódica cada N meses" — pero al menos un bullet debe estar presente.

Ninguna cabecera de sección se omite silenciosamente (con la única excepción de la condicional "Reglas creadas en esta sesión" — cuya presencia es en sí misma una señal). Así los diffs mes a mes siguen siendo legibles: el lector escanea la misma estructura cada vez.

## 11. Layout determinista para auditoría

Para informes que se repiten periódicamente (gobierno, compliance) el esqueleto estructural debe ser estable entre ejecuciones. Las writer skills mantienen libertad tipográfica y cromática dentro del tema, pero estas reglas son no negociables:

- **Orden de secciones fijo**: Portada → Resumen ejecutivo → Cobertura por tabla → Detalle de reglas → Gaps → (Reglas creadas en esta sesión) → Recomendaciones. No reordenar.
- **KPI cards**: exactamente los cuatro de §5, en el orden exacto de §5. No añadir un quinto, no quitar ninguno, no reordenar.
- **Columnas de la matriz de cobertura**: nombre de tabla (primera), luego las dimensiones en orden estable — Completeness, Uniqueness, Validity, Consistency, luego cualquier dimensión específica de dominio devuelta por `get_quality_rule_dimensions` en orden alfabético, luego Coverage % (última). Mantener este orden entre ejecuciones incluso cuando una dimensión no tiene cobertura en ninguna tabla del scope actual (renderizar la columna con todas las celdas vacías o `—`).
- **Agrupación del detalle de reglas**: agrupar por tabla, no por dimensión. Una sub-sección por tabla, en orden alfabético de nombre de tabla.
- **Ordenación de gaps**: prioridad (CRITICO → ALTO → MEDIO → BAJO) → tabla (alfabético) → columna (alfabético).
- **Límites de ítems por formato**:
  - PDF / DOCX: hasta 20 gaps visibles; el resto se agrega en una línea `"… y N gaps más de prioridad menor"`.
  - PPTX: top 10 gaps solamente (una slide).
  - Dashboard web: sin límite — usar filtros y tablas ordenables.
  - Póster / Infografía: top 3 críticos + top 3 recomendaciones.
- **Marcadores de sección vacía**: cada sección canónica (§2.1–§2.6) emite siempre su cabecera. Si no tiene contenido, una única línea explícita reemplaza al contenido ("No hay reglas definidas para esta tabla todavía", "No se han detectado gaps en el scope actual", "No se han creado reglas en esta sesión"). Nunca se salta la sección silenciosamente — la presencia de la cabecera es lo que hace que los diffs mes a mes alineen.
- **Formato de fecha de generación**: ISO 8601 (`YYYY-MM-DD`) en los metadatos del documento y en el `quality-report.md` interno. Las writer skills pueden renderizar una forma visible localizada (`24 April 2026` / `24 de abril de 2026`) en la portada, pero el metadato subyacente se queda en ISO.
- **Nombres de fichero**: `<slug>-quality-report.<ext>` para PDF/DOCX/HTML, `<slug>-quality-summary.pptx`, `<slug>-quality-poster.pdf` o `.png`. `<slug>` es el dominio o scope normalizado (ASCII minúsculas, underscores, ≤30 caracteres). Nombres consistentes facilitan hacer diff entre carpetas con herramientas externas.

La combinación de orden de secciones fijo, orden de KPIs fijo, orden de columnas fijo, reglas de ordenación fijas y convención de nombres hace que dos ejecuciones sobre el mismo dataset produzcan informes visualmente comparables — que es lo que los lectores de auditoría esperan.
