# Guia de Reasoning (Documentacion del Proceso)

Guia detallada para generar el reasoning de cada analisis. El reasoning documenta el razonamiento completo del analista: desde la pregunta original hasta las conclusiones y sugerencias.

## Cuando generar

| Profundidad | Reasoning | Formato |
|-------------|-----------|---------|
| Rapido | No generar fichero. Incluir notas clave en el chat (ver SKILL.md sec 7.1) | Solo chat |
| Estandar | Generar en `output/[ANALISIS_DIR]/reasoning/reasoning.md` | Solo .md |
| Profundo | Generar en `output/[ANALISIS_DIR]/reasoning/reasoning.md` | Solo .md (completo + sugerencias detalladas) |

**Override del usuario**: Si el usuario pide explicitamente reasoning en otros formatos (PDF, HTML, DOCX), generar el .md primero y luego convertir con:
```bash
bash -c "source .venv/bin/activate && python tools/md_to_report.py output/[ANALISIS_DIR]/reasoning/reasoning.md --style corporate"
```
Anadir `--docx` si solicito DOCX.

## Contenido obligatorio

El reasoning debe incluir todas las secciones siguientes:

1. **Pregunta original del usuario** — Transcripcion literal de la peticion
2. **Hipotesis formuladas y resultado de su validacion** — Tabla resumen obligatoria:
   ```
   | ID | Hipotesis | Resultado | Esperado | Real | So What |
   ```
3. **Dominio y tablas utilizadas** — Nombre exacto del dominio y listado de tablas consultadas
4. **Resumen de calidad de datos** — Data Quality Score de la Fase 1.1 (ALTO/MEDIO/BAJO con %)
5. **Decisiones tomadas y justificacion** — Elecciones metodologicas, filtros aplicados, exclusiones
6. **Preguntas realizadas al MCP y resumen de los datos obtenidos** — Cada query con descripcion del resultado
7. **Analisis realizados y hallazgos clave** — Tecnicas aplicadas y principales insights
8. **Clustering o feature importance** (si aplica) — Enfoque, variables, resultados, limitaciones
9. **Limitaciones identificadas** — En los datos o en el analisis
10. **Sugerencias para analisis futuros** — Preguntas que quedaron abiertas o lineas de investigacion
11. **Rutas de todos los archivos generados** — Listado completo de deliverables, scripts, datos y assets

## Diferencias por profundidad

### Estandar
- Contenido completo (todas las secciones anteriores)
- Sugerencias para analisis futuros: breves, 2-3 lineas de investigacion

### Profundo
- Contenido completo (todas las secciones anteriores)
- Sugerencias de analisis de seguimiento detalladas: para cada sugerencia incluir pregunta de negocio, hipotesis inicial, datos necesarios y tecnica analitica recomendada
- Si se usaron tecnicas avanzadas (tests estadisticos, Monte Carlo, root cause analysis): documentar parametros, supuestos y sensibilidad de los resultados
