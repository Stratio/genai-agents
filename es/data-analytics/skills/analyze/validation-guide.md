# Guia de Validacion de Output Final

Checklist de validacion del producto terminado antes de reportar al usuario. La validacion se estructura en 4 bloques con criterios PASS/WARNING/FAIL por item.

## Cuando generar

| Profundidad | Bloques | Formato |
|-------------|---------|---------|
| Rapido | Solo Bloque A (integridad de archivos) | Solo chat (sin fichero) |
| Estandar | Bloques A + B + C | Generar `validation/validation.md` + resumen en chat |
| Profundo | Bloques A + B + C + D | Generar `validation/validation.md` + resumen en chat |

**Override del usuario**: Si el usuario pide explicitamente validacion en otros formatos (PDF, HTML, DOCX), generar el .md primero y luego convertir con:
```bash
bash -c "source .venv/bin/activate && python tools/md_to_report.py output/[ANALISIS_DIR]/validation/validation.md --style corporate"
```
Anadir `--html` si solicito HTML. Anadir `--docx` si solicito DOCX.

## Bloques de Validacion

### Bloque A — Integridad de archivos

**Comando de verificación (OBLIGATORIO ejecutar):**
```bash
ls -lh output/[ANALISIS_DIR]/
```
Revisar que cada fichero declarado en el plan aparece en el listado con tamaño > 0 bytes.

**Si un deliverable no aparece o tiene 0 bytes → FAIL bloqueante**: regenerar el fichero antes de continuar con la validación. No pasar al Bloque B hasta que el Bloque A sea PASS.

| Item | Verificacion | Criterio |
|------|-------------|----------|
| report.md | Existe en `output/[ANALISIS_DIR]/` | PASS si existe, FAIL si no |
| Deliverables solicitados | Cada formato pedido tiene su archivo | PASS si todos existen, FAIL si falta alguno |
| Assets referenciados | Cada grafica referenciada en report.md existe en `assets/` | PASS si todos existen, WARNING si falta alguno |
| CSVs referenciados | Datos intermedios referenciados en scripts existen en `data/` | PASS si todos existen, WARNING si falta alguno |
| Reasoning | reasoning.md existe en `reasoning/` | PASS si existe (solo verificar en Estandar/Profundo) |
| Validation | validation.md existe en `validation/` | PASS si existe (solo verificar en Estandar/Profundo) |

**Ajuste para Rapido**: En profundidad Rapido, solo verificar deliverables (report.md, formatos solicitados, assets). No verificar reasoning ni validation ya que no se generan como fichero.

**Criterios:**
- **PASS**: Todos los archivos esperados existen
- **WARNING**: Faltan archivos no criticos (assets, CSVs intermedios)
- **FAIL**: Falta un deliverable principal (report.md, formato solicitado)

### Bloque B — Calidad de visualizaciones

Para cada grafica en `output/[ANALISIS_DIR]/assets/`:

| Item | Verificacion | Criterio |
|------|-------------|----------|
| Tamano minimo | Archivo > 1 KB | PASS si > 1KB, WARNING si ≤ 1KB |
| Datos suficientes | > 5 valores no-nulos en columna principal | PASS si suficientes, WARNING si no |

**Umbrales por tipo de grafica:**

| Tipo | Minimo de puntos de datos |
|------|--------------------------|
| Tendencia (line chart) | > 6 puntos temporales |
| Ranking (bar chart) | > 3 categorias |
| Distribucion (histogram, box) | > 10 valores |
| Scatter | > 10 puntos |
| Heatmap | > 2 filas y > 2 columnas |

**Criterios:**
- **PASS**: Grafica cumple tamano y datos minimos
- **WARNING**: Grafica existe pero no cumple umbrales → excluir del deliverable y documentar por que
- **FAIL**: Grafica no se genero (cubierto en Bloque A)

### Bloque C — Completitud del analisis

| Item | Verificacion | Criterio |
|------|-------------|----------|
| Dimensiones cubiertas | Cada dimension pedida por el usuario aparece en al menos un analisis/grafica | PASS si todas cubiertas, WARNING si falta alguna |
| Secciones de reasoning | Todas las secciones obligatorias presentes (ver reasoning-guide.md) | PASS si completo, WARNING si falta alguna |
| Hipotesis validadas | Cada hipotesis formulada tiene resultado (CONFIRMADA/REFUTADA/PARCIAL) | PASS si todas tienen resultado, WARNING si alguna queda sin validar |
| So What test | Hallazgos del resumen ejecutivo pasan las 4 preguntas obligatorias | PASS si todos pasan, WARNING si alguno no |

**Criterios:**
- **PASS**: Analisis cubre todas las dimensiones y secciones esperadas
- **WARNING**: Falta alguna dimension o seccion — documentar que falta y por que
- **FAIL**: No aplica (la completitud es siempre WARNING, nunca bloqueante)

### Bloque D — Consistencia de datos

Para 1-2 KPIs clave del analisis:

| Item | Verificacion | Criterio |
|------|-------------|----------|
| KPI en deliverable vs datos | Comparar valor reportado en deliverable con valor calculado desde `output/[ANALISIS_DIR]/data/` | PASS si discrepancia ≤ 1% |
| Totales cruzados | Si hay subtotales, verificar que suman al total | PASS si cuadran, WARNING si discrepancia ≤ 5% |

**Criterios:**
- **PASS**: KPIs consistentes entre deliverable y datos fuente (discrepancia ≤ 1%)
- **WARNING**: Discrepancia > 1% y ≤ 5% — documentar diferencia y posible causa (redondeo, filtros)
- **FAIL**: Discrepancia > 5% — investigar antes de entregar

## Formato del fichero validation.md

```markdown
# Validacion de Output

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
| Grafica | Tamano | Datos | Estado | Detalle |
|---------|--------|-------|--------|---------|
| ventas_por_region.png | 45 KB | 12 categorias | PASS | — |
| ... | ... | ... | ... | ... |

## Bloque C — Completitud del analisis
| Item | Estado | Detalle |
|------|--------|---------|
| Dimensiones cubiertas | PASS | region, tiempo, producto |
| ... | ... | ... |

## Bloque D — Consistencia de datos
| KPI | Valor deliverable | Valor datos | Discrepancia | Estado |
|-----|-------------------|-------------|--------------|--------|
| Ventas totales | €1.2M | €1.2M | 0.0% | PASS |
| ... | ... | ... | ... | ... |
```

## Regla general

- **Bloque A (integridad de archivos)**: FAIL es **bloqueante** — regenerar los ficheros faltantes antes de continuar.
- **Bloques B, C, D**: la validacion **no bloquea la entrega**. Si hay WARNINGs o FAILs, se reportan en el chat junto con el resumen de hallazgos, pero el analisis se entrega igualmente. El objetivo es transparencia, no bloqueo.
