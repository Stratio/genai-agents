# Guía de Validación de Output Final

Checklist de validación del producto terminado antes de reportar al usuario. La validación se estructura en 4 bloques con criterios PASS/WARNING/FAIL por item.

## Cuándo generar

| Profundidad | Bloques | Formato |
|-------------|---------|---------|
| Rápido | Solo Bloque A (integridad de archivos) | Solo chat (sin fichero) |
| Estándar | Bloques A + B + C | Generar `validation/validation.md` + resumen en chat |
| Profundo | Bloques A + B + C + D | Generar `validation/validation.md` + resumen en chat |

**Override del usuario**: Si el usuario pide explícitamente validación en otros formatos (PDF, HTML, DOCX), generar el .md primero y luego convertir con:
```bash
python3 skills/analyze/report/tools/md_to_report.py output/[ANALISIS_DIR]/validation/validation.md --style corporate
```
Añadir `--html` si solicitó HTML. Añadir `--docx` si solicitó DOCX.

## Bloques de Validación

### Bloque A — Integridad de archivos

**Comando de verificación (OBLIGATORIO ejecutar):**
```bash
ls -lh output/[ANALISIS_DIR]/
```
Revisar que cada fichero declarado en el plan aparece en el listado con tamaño > 0 bytes.

**Si un deliverable no aparece o tiene 0 bytes → FAIL bloqueante**: regenerar el fichero antes de continuar con la validación. No pasar al Bloque B hasta que el Bloque A sea PASS.

| Item | Verificación | Criterio |
|------|-------------|----------|
| report.md | Existe en `output/[ANALISIS_DIR]/` | PASS si existe, FAIL si no |
| Deliverables solicitados | Cada formato pedido tiene su archivo | PASS si todos existen, FAIL si falta alguno |
| Assets referenciados | Cada gráfica referenciada en report.md existe en `assets/` | PASS si todos existen, WARNING si falta alguno |
| CSVs referenciados | Datos intermedios referenciados en scripts existen en `data/` | PASS si todos existen, WARNING si falta alguno |
| Reasoning | reasoning.md existe en `reasoning/` | PASS si existe (solo verificar en Estándar/Profundo) |
| Validation | validation.md existe en `validation/` | PASS si existe (solo verificar en Estándar/Profundo) |

**Ajuste para Rápido**: En profundidad Rápido, solo verificar deliverables (report.md, formatos solicitados, assets). No verificar reasoning ni validation ya que no se generan como fichero.

**Criterios:**
- **PASS**: Todos los archivos esperados existen
- **WARNING**: Faltan archivos no criticos (assets, CSVs intermedios)
- **FAIL**: Falta un deliverable principal (report.md, formato solicitado)

### Bloque B — Calidad de visualizaciones

Para cada gráfica en `output/[ANALISIS_DIR]/assets/`:

| Item | Verificación | Criterio |
|------|-------------|----------|
| Tamaño mínimo | Archivo > 1 KB | PASS si > 1KB, WARNING si ≤ 1KB |
| Datos suficientes | > 5 valores no-nulos en columna principal | PASS si suficientes, WARNING si no |

**Umbrales por tipo de gráfica:**

| Tipo | Mínimo de puntos de datos |
|------|--------------------------|
| Tendencia (line chart) | > 6 puntos temporales |
| Ranking (bar chart) | > 3 categorías |
| Distribución (histogram, box) | > 10 valores |
| Scatter | > 10 puntos |
| Heatmap | > 2 filas y > 2 columnas |

**Criterios:**
- **PASS**: Gráfica cumple tamaño y datos mínimos
- **WARNING**: Gráfica existe pero no cumple umbrales → excluir del deliverable y documentar por que
- **FAIL**: Gráfica no se generó (cubierto en Bloque A)

### Bloque C — Completitud del análisis

| Item | Verificación | Criterio |
|------|-------------|----------|
| Dimensiones cubiertas | Cada dimensión pedida por el usuario aparece en al menos un análisis/gráfica | PASS si todas cubiertas, WARNING si falta alguna |
| Secciones de reasoning | Todas las secciones obligatorias presentes (ver reasoning-guide.md) | PASS si completo, WARNING si falta alguna |
| Hipótesis validadas | Cada hipótesis formulada tiene resultado (CONFIRMADA/REFUTADA/PARCIAL) | PASS si todas tienen resultado, WARNING si alguna queda sin validar |
| So What test | Hallazgos del resumen ejecutivo pasan las 4 preguntas obligatorias | PASS si todos pasan, WARNING si alguno no |

**Criterios:**
- **PASS**: Análisis cubre todas las dimensiones y secciones esperadas
- **WARNING**: Falta alguna dimensión o sección — documentar que falta y por que
- **FAIL**: No aplica (la completitud es siempre WARNING, nunca bloqueante)

### Bloque D — Consistencia de datos

Para 1-2 KPIs clave del análisis:

| Item | Verificación | Criterio |
|------|-------------|----------|
| KPI en deliverable vs datos | Comparar valor reportado en deliverable con valor calculado desde `output/[ANALISIS_DIR]/data/` | PASS si discrepancia ≤ 1% |
| Totales cruzados | Si hay subtotales, verificar que suman al total | PASS si cuadran, WARNING si discrepancia ≤ 5% |

**Criterios:**
- **PASS**: KPIs consistentes entre deliverable y datos fuente (discrepancia ≤ 1%)
- **WARNING**: Discrepancia > 1% y ≤ 5% — documentar diferencia y posible causa (redondeo, filtros)
- **FAIL**: Discrepancia > 5% — investigar antes de entregar

## Formato del fichero validation.md

```markdown
# Validación de Output

## Resumen
- **Estado general**: PASS / WARNING / FAIL
- **Bloques ejecutados**: A, B, C [, D]
- **Fecha**: YYYY-MM-DD HH:MM

## Bloque A — Integridad de archivos
| Item | Estado | Detalle |
|------|--------|---------|
| report.md | PASS | Existe |
| ... | ... | ... |

## Bloque B — Calidad de visualizaciones
| Gráfica | Tamaño | Datos | Estado | Detalle |
|---------|--------|-------|--------|---------|
| ventas_por_region.png | 45 KB | 12 categorías | PASS | — |
| ... | ... | ... | ... | ... |

## Bloque C — Completitud del análisis
| Item | Estado | Detalle |
|------|--------|---------|
| Dimensiones cubiertas | PASS | región, tiempo, producto |
| ... | ... | ... |

## Bloque D — Consistencia de datos
| KPI | Valor deliverable | Valor datos | Discrepancia | Estado |
|-----|-------------------|-------------|--------------|--------|
| Ventas totales | €1.2M | €1.2M | 0.0% | PASS |
| ... | ... | ... | ... | ... |
```

## Regla general

- **Bloque A (integridad de archivos)**: FAIL es **bloqueante** — regenerar los ficheros faltantes antes de continuar.
- **Bloques B, C, D**: la validación **no bloquea la entrega**. Si hay WARNINGs o FAILs, se reportan en el chat junto con el resumen de hallazgos, pero el análisis se entrega igualmente. El objetivo es transparencia, no bloqueo.
