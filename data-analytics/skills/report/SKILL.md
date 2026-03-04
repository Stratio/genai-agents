---
name: report
description: Generacion de informes profesionales en multiples formatos (PDF, DOCX, web interactiva con Plotly, PowerPoint) a partir de analisis de datos. Usar cuando el usuario necesite generar informes, dashboards, presentaciones o documentacion a partir de datos analizados.
argument-hint: '[formato: pdf|web|pptx] [tema (opcional)]'
---

# Skill: Generacion de Informes

Guia para generar informes profesionales en multiples formatos a partir de datos y analisis.

## 1. Determinar Formato, Estructura y Estilo

Parsear argumento: $ARGUMENTS

Si el formato no esta especificado, preguntar al usuario las 3 preguntas siguientes en una sola interaccion, siguiendo la convencion de preguntas (sec "Interaccion con el Usuario" de AGENTS.md) (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no). Las opciones son literales — no inventar, no omitir, no sustituir:

| # | Pregunta | Opciones (literales) | Seleccion |
|---|----------|---------------------|-----------|
| 1 | ¿En que formatos quieres los deliverables? | **Documento** (PDF + DOCX) · **Web** (HTML interactivo con Plotly) · **PowerPoint** (.pptx) | Multiple |
| 2 | ¿Que estructura prefieres para el reporte? | **Scaffold base** (Recomendado): resumen ejecutivo → metodologia → datos → analisis → conclusiones · **Al vuelo**: estructura libre segun contexto | Unica |
| 3 | ¿Que estilo visual prefieres? | **Corporativo** (`corporate.css`, Recomendado): limpio, profesional · **Formal/academico** (`academic.css`): serif, margenes amplios, estilo paper · **Moderno/creativo** (`modern.css`): colores, gradientes, visualmente atractivo | Unica |

- La pregunta 1 SIEMPRE permite seleccion multiple (el usuario puede querer varios formatos)
- Si no selecciona ningun formato, solo se da respuesta textual en el chat
- Siempre se genera `output/[ANALISIS_DIR]/report.md` automaticamente como documentacion interna (no necesita opcion)
- Si el formato viene en el argumento ($ARGUMENTS), saltar directamente a preguntar estructura y estilo (preguntas 2 y 3)

## 2. Verificar Datos Disponibles

- Comprobar si existen datos previos en `output/[ANALISIS_DIR]/data/` (CSVs, DataFrames)
- Comprobar si existen graficas en `output/[ANALISIS_DIR]/assets/`
- Si no hay datos: informar al usuario que primero necesita ejecutar un analisis
- Si hay datos parciales: preguntar si reutilizar o regenerar

### 2.1 Visualizacion y storytelling

Leer y seguir `skills-guides/visualization.md` para:
- Seleccion de tipo de grafica segun pregunta analitica (sec 1)
- Principios de visualizacion y accesibilidad (sec 2)
- Data storytelling: estructura narrativa Hook→Contexto→Hallazgos→Tension→Resolucion (sec 3)
- Mapping hallazgos analiticos → rol narrativo (sec 4)

**Especifico de report — Layout anti-solapamiento**: Titulo como insight arriba, contexto como subtitulo, leyenda posicionada debajo del grafico o a la derecha exterior. Usar `tools/chart_layout.py` para layout estandar.

## 3. Setup del Entorno

```bash
bash setup_env.sh
```
Verificar que las dependencias del formato estan disponibles (weasyprint para PDF, python-pptx para PowerPoint, etc.).

## 4. Herramientas de Estilo

Todos los formatos comparten la misma fuente de verdad para colores y fuentes:

- **CSS (PDF, Web):** `build_css(style, target)` de `tools/css_builder.py` ensambla tokens + theme + target
- **No-CSS (PPTX, DOCX):** `get_palette(style)` de `tools/css_builder.py` devuelve colores RGB y fuentes
- **Reasoning (Markdown → PDF/HTML):** `tools/md_to_report.py` con opciones `--style`, `--cover`, `--author`, `--domain`

```python
from css_builder import build_css, get_palette
css, name = build_css("corporate", "pdf")    # CSS ensamblado
palette = get_palette("corporate")           # {"primary": (0x1a,0x36,0x5d), "font_main": "Inter", ...}
```

## 5. Generacion por Formato

### 5.1 Documento (PDF + DOCX)
Si el usuario selecciono "Documento": ver [document-guide.md](document-guide.md) para el pipeline completo de PDFGenerator, DOCXGenerator y pitfalls.

### 5.2 Web (Dashboard Interactivo)
Si el usuario selecciono "Web": ver [web-guide.md](web-guide.md) para el pipeline completo de DashboardBuilder, capacidades, workflow y pitfalls.

### 5.3 PowerPoint
Si el usuario selecciono "PowerPoint": ver [powerpoint-guide.md](powerpoint-guide.md) para el pipeline completo de pptx_layout, diseño de slides y pitfalls.

### 5.4 Markdown (siempre generado)
Se genera automaticamente en todos los analisis, sin necesidad de que el usuario lo seleccione.
1. Escribir .md directo con:
   - Tablas markdown para datos tabulares
   - Bloques mermaid para diagramas de flujo o relaciones
   - Referencias a graficas en `output/[ANALISIS_DIR]/assets/`
2. Guardar en `output/[ANALISIS_DIR]/report.md`

## 6. Reasoning

Generar reasoning segun la profundidad seleccionada (ver sec "Reasoning" de AGENTS.md):

- **Rapido**: No generar fichero. Notas clave en el chat.
- **Estandar/Profundo**: Generar `output/[ANALISIS_DIR]/reasoning/reasoning.md`. Si el usuario solicito override a otros formatos (PDF, HTML, DOCX), convertir con `tools/md_to_report.py --style corporate` (anadir `--docx` si aplica).

Documentando:
- Formato(s) generado(s) y justificacion
- Estructura elegida y por que
- Datos utilizados y sus fuentes
- Decisiones de diseno
- Rutas de todos los archivos generados

## 7. Entrega

**Antes de reportar**, ejecutar verificación de existencia:
```bash
ls -lh output/[ANALISIS_DIR]/
```
Si algún fichero solicitado no aparece en el listado → volver al paso 5 (generación) y regenerarlo. Solo reportar al usuario cuando todos los ficheros estén confirmados en disco.

A continuación reportar en el chat:
- Formato(s) generado(s)
- Ruta(s) de los archivos
- Vista previa del contenido (resumen ejecutivo)
- Instrucciones para abrir/usar el deliverable
