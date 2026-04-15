---
name: report
description: "Generación de informes profesionales en múltiples formatos (PDF, DOCX, web interactiva con Plotly, PowerPoint). Usar cuando el usuario necesite generar informes, dashboards, resúmenes ejecutivos, presentaciones o cualquier entregable formal a partir de análisis de datos o exploración conversacional."
argument-hint: "[formato: pdf|web|pptx] [tema (opcional)]"
---

# Skill: Generación de Informes

Guía para generar informes profesionales en múltiples formatos a partir de datos y análisis.

## 1. Determinar Formato, Estructura y Estilo

Parsear argumento: $ARGUMENTS

Si el formato no está especificado, preguntar al usuario las 3 preguntas siguientes en una sola interacción, siguiendo la convención de preguntas (sec "Interacción con el Usuario" de AGENTS.md) (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no). Las opciones son literales — no inventar, no omitir, no sustituir:

| # | Pregunta | Opciones (literales) | Selección |
|---|----------|---------------------|-----------|
| 1 | ¿En que formatos quieres los deliverables? | **Documento** (PDF + DOCX) · **Web** (HTML interactivo con Plotly) · **PowerPoint** (.pptx) | Múltiple |
| 2 | ¿Qué estructura prefieres para el reporte? | **Scaffold base** (Recomendado): resumen ejecutivo → metodología → datos → análisis → conclusiones · **Al vuelo**: estructura libre según contexto | Única |
| 3 | ¿Qué estilo visual prefieres? | **Corporativo** (`corporate.css`, Recomendado): limpio, profesional · **Formal/académico** (`academic.css`): serif, márgenes amplios, estilo paper · **Moderno/creativo** (`modern.css`): colores, gradientes, visualmente atractivo | Única |

- La pregunta 1 SIEMPRE permite selección múltiple (el usuario puede querer varios formatos)
- Si no selecciona ningún formato, solo se da respuesta textual en el chat
- Siempre se genera `output/[ANALISIS_DIR]/report.md` automáticamente como documentación interna (no necesita opción)
- Si el formato viene en el argumento ($ARGUMENTS), saltar directamente a preguntar estructura y estilo (preguntas 2 y 3)

## 2. Verificar Datos Disponibles

- Comprobar si existen datos previos en `output/[ANALISIS_DIR]/data/` (CSVs, DataFrames)
- Comprobar si existen gráficas en `output/[ANALISIS_DIR]/assets/`
- Si no hay datos: informar al usuario que primero necesita ejecutar un análisis
- Si hay datos parciales: preguntar si reutilizar o regenerar

### 2.1 Visualización y storytelling

Leer y seguir `skills-guides/visualization.md` para:
- Selección de tipo de gráfica según pregunta analítica (sec 1)
- Principios de visualización y accesibilidad (sec 2)
- Data storytelling: estructura narrativa Hook→Contexto→Hallazgos→Tensión→Resolución (sec 3)
- Mapping hallazgos analíticos → rol narrativo (sec 4)

**Específico de report — Layout anti-solapamiento**: Título como insight arriba, contexto como subtítulo, leyenda posicionada debajo del gráfico o a la derecha exterior. Usar `tools/chart_layout.py` para layout estándar.

## 3. Setup del Entorno

```bash
bash setup_env.sh
```
Verificar que las dependencias del formato están disponibles (weasyprint para PDF, python-pptx para PowerPoint, etc.).

## 3.1 Idioma de los Deliverables Generados

Todos los generadores (`DOCXGenerator`, `PDFGenerator`, `DashboardBuilder`, `md_to_report.py`) usan un catálogo i18n compartido en `tools/i18n.py` para sus labels estáticos (títulos del scaffold "Resumen Ejecutivo" / "Metodología" / …, labels de cover "Autor:" / "Dominio:" / "Fecha:", chrome del dashboard "Filtros" / "Limpiar filtros" / "KPIs", el atributo HTML `lang`, el título por defecto del informe, etc.).

**Pasar el idioma del usuario explícitamente al invocar cualquier generador** para que el chrome estático coincida con el idioma del chat:

- API Python (`DOCXGenerator`, `PDFGenerator`, `DashboardBuilder`): pasar `lang="<código>"` a `render_scaffold` / `render_from_markdown` / `render_from_html` / el constructor (según aplique). Opcionalmente pasar `labels={...}` para sobrescribir claves concretas.
- CLI (`md_to_report.py`): pasar `--lang <código>` (y opcionalmente `--labels-json '{...}'`).

Orden de resolución cuando no se pasa `lang`: fichero `.agent_lang` escrito al empaquetar → `"en"`. Así un paquete hecho con `--lang es` usa español por defecto aunque no se pase `lang` explícito. Idiomas del catálogo hoy: `en`, `es`. Códigos desconocidos hacen fallback a inglés por clave; pasar `labels={...}` para inyectar traducciones a otros idiomas.

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

## 5. Generación por Formato

### 5.1 Documento (PDF + DOCX)
Si el usuario seleccionó "Documento": ver [document-guide.md](document-guide.md) para el pipeline completo de PDFGenerator, DOCXGenerator y pitfalls.

### 5.2 Web (Dashboard Interactivo)
Si el usuario seleccionó "Web": ver [web-guide.md](web-guide.md) para el pipeline completo de DashboardBuilder, capacidades, workflow y pitfalls.

### 5.3 PowerPoint
Si el usuario seleccionó "PowerPoint": ver [powerpoint-guide.md](powerpoint-guide.md) para el pipeline completo de pptx_layout, diseño de slides y pitfalls.

### 5.4 Markdown (siempre generado)
Se genera automáticamente en todos los análisis, sin necesidad de que el usuario lo seleccione.
1. Escribir .md directo con:
   - Tablas markdown para datos tabulares
   - Bloques mermaid para diagramas de flujo o relaciones
   - Referencias a gráficas en `output/[ANALISIS_DIR]/assets/`
2. Guardar en `output/[ANALISIS_DIR]/report.md`

## 6. Reasoning

Generar reasoning según la profundidad seleccionada (ver sec "Reasoning" de AGENTS.md):

- **Rápido**: No generar fichero. Notas clave en el chat.
- **Estándar/Profundo**: Generar `output/[ANALISIS_DIR]/reasoning/reasoning.md`. Si el usuario solicitó override a otros formatos (PDF, HTML, DOCX), convertir con `tools/md_to_report.py --style corporate --lang <idioma_usuario>` (añadir `--docx` si aplica).

Documentando:
- Formato(s) generado(s) y justificación
- Estructura elegida y por que
- Datos utilizados y sus fuentes
- Decisiones de diseño
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
