# Guía de Reasoning (Documentación del Proceso)

Guía detallada para generar el reasoning de cada análisis. El reasoning documenta el razonamiento completo del analista: desde la pregunta original hasta las conclusiones y sugerencias.

## Cuándo generar

| Profundidad | Reasoning | Formato |
|-------------|-----------|---------|
| Rápido | No generar fichero. Incluir notas clave en el chat (ver SKILL.md sec 7.1) | Solo chat |
| Estándar | Generar en `output/[ANALISIS_DIR]/reasoning/reasoning.md` | Solo .md |
| Profundo | Generar en `output/[ANALISIS_DIR]/reasoning/reasoning.md` | Solo .md (completo + sugerencias detalladas) |

**Override del usuario**: Si el usuario pide explícitamente reasoning en otros formatos (PDF, HTML, DOCX), generar el .md primero y luego convertir con:
```bash
python3 skills/analyze/report/tools/md_to_report.py output/[ANALISIS_DIR]/reasoning/reasoning.md --style corporate
```
Añadir `--html` si solicitó HTML. Añadir `--docx` si solicitó DOCX.

## Contenido obligatorio

El reasoning debe incluir todas las secciones siguientes:

1. **Pregunta original del usuario** — Transcripción literal de la petición
2. **Hipótesis formuladas y resultado de su validación** — Tabla resumen obligatoria:
   ```
   | ID | Hipótesis | Resultado | Esperado | Real | So What |
   ```
3. **Dominio y tablas utilizadas** — Nombre exacto del dominio y listado de tablas consultadas
4. **Resumen de calidad de datos** — Ambas señales de la Fase 1.1: Data Profiling Score (ALTO/MEDIO/BAJO con %) Y Governance Quality Status (reglas OK/KO/WARNING, señalando explícitamente cualquier regla KO que afecte a columnas analizadas)
5. **Decisiones tomadas y justificación** — Elecciones metodologicas, filtros aplicados, exclusiones
6. **Preguntas realizadas al MCP y resumen de los datos obtenidos** — Cada query con descripción del resultado
7. **Análisis realizados y hallazgos clave** — Técnicas aplicadas y principales insights
8. **Clustering o feature importance** (si aplica) — Enfoque, variables, resultados, limitaciones
9. **Limitaciones identificadas** — En los datos o en el análisis
10. **Sugerencias para análisis futuros** — Preguntas que quedaron abiertas o líneas de investigación
11. **Rutas de todos los archivos generados** — Listado completo de deliverables, scripts, datos y assets

## Diferencias por profundidad

### Estándar
- Contenido completo (todas las secciones anteriores)
- Sugerencias para análisis futuros: breves, 2-3 líneas de investigación

### Profundo
- Contenido completo (todas las secciones anteriores)
- Sugerencias de análisis de seguimiento detalladas: para cada sugerencia incluir pregunta de negocio, hipótesis inicial, datos necesarios y técnica analítica recomendada
- Si se usaron técnicas avanzadas (tests estadísticos, Monte Carlo, root cause analysis): documentar parámetros, supuestos y sensibilidad de los resultados
