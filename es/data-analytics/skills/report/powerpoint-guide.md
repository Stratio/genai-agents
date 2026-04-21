# Guía de Generación PowerPoint

Referencia operativa para el pipeline de PowerPoint dentro de `/report`.

## Pipeline

1. Los scripts generados DEBEN importar helpers de `tools/pptx_layout.py`. NUNCA definir `add_slide_header`, `add_text`, `add_kpi_box`, `add_paragraph`, `fill_shape`, `add_rect`, etc. inline — importarlos del módulo
2. NUNCA hardcodear posiciones de contenido — usar `content_area()`, `chart_area()`, `footer_area()` para obtener coordenadas seguras
3. Para gráficas: usar `add_image_safe()` que calcula posición automáticamente dentro del safe área
4. Para notas al pie: usar `add_footer_note()` que posiciona en zona segura
5. Inicialización: usar `create_presentation(style)` que devuelve `(prs, palette)` con dimensiones estándar (10x7.5")
6. Headers: `add_slide_header(slide, title, subtitle, palette)` retorna `CONTENT_TOP` — usar ese valor como punto de partida para el contenido
7. Colores: usar `rgb_color(palette["primary"])` para convertir tuplas RGB a `RGBColor`
8. Diseño de slides:
   - Portada: título del análisis, fecha, dominio
   - Resumen ejecutivo: 3-5 bullets con hallazgos clave (números grandes 60-72pt para KPIs vía `add_kpi_box`)
   - Slides de datos: una gráfica principal por slide (de `output/[ANALISIS_DIR]/assets/`), con título como insight
   - Tablas: datos clave en formato tabular cuando las gráficas no sean suficientes
   - Conclusiones y recomendaciones: bullets accionables
9. Principios de diseño:
   - Paleta de color del tema elegido (vía `get_palette`), no colores hardcodeados
   - Variedad de layouts: no repetir el mismo layout en slides consecutivos
   - Cada slide necesita al menos un elemento visual (gráfica, tabla, diagrama, número destacado)
   - Tipografia: títulos 36-44pt bold, cuerpo 14-16pt
   - Número orientativo de slides: 8-12 para ejecutiva, 15-20 para detallada
10. Generar script: `output/[ANALISIS_DIR]/scripts/generate_pptx.py --style corporate`
11. Guardar en `output/[ANALISIS_DIR]/<slug>-presentation.pptx` (el `<slug>` es la parte descriptiva de `[ANALISIS_DIR]` tras el timestamp — ver `SKILL.md` §1.1)

## Slides con Imagen + Panel Lateral

- Usar `add_image_with_aspect(slide, img_path, left, top, max_width, max_height)` que retorna `(actual_w, actual_h)` reales tras preservar aspect ratio
- Usar la constante `PANEL_GAP` (0.3") como separacion estándar entre imagen y panel lateral
- Calcular posición del panel: `panel_left = left + actual_w + PANEL_GAP`

## Pitfalls Comunes

- **Aspect ratio**: NUNCA pasar width Y height a `slide.shapes.add_picture()` directamente — siempre usar `add_image_with_aspect()` o `add_image_safe()` que preservan proporciones. Las gráficas matplotlib landscape (18x7) se distorsionan si se fuerzan a areas cuadradas
- Las imágenes deben ser **PNG** (no SVG) — python-pptx no soporta SVG. Guardar gráficas como PNG en `output/[ANALISIS_DIR]/assets/`
- python-pptx no soporta markdown — el texto debe formatearse con `runs` (negrita, cursiva, color vía `run.font`)
- Usar `get_palette(style)` para colores de shapes y fonts, nunca hardcodear valores RGB
- Overflow: NUNCA colocar elementos debajo de CONTENT_BOTTOM (7.3"). Usar `check_bounds()` para validar posiciones custom. Para gráficas usar `add_image_safe()` que calcula automáticamente
- Clearance header: El contenido SIEMPRE empieza en CONTENT_TOP (1.3"), nunca más arriba. `add_slide_header()` retorna este valor
- Helpers inline: NUNCA redefinir `add_slide_header`, `add_text`, `add_kpi_box`, etc. en el script. Importar de `tools/pptx_layout`
