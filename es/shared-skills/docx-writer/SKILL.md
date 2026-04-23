---
name: docx-writer
description: "Crea documentos Word (.docx) con diseño intencional y realiza operaciones estructurales sobre los existentes. Usa esta skill siempre que necesites producir un documento Word pulido (carta, memo, contrato, nota de política, informe multipágina) o manipular DOCX existentes (fusionar, dividir, buscar-y-reemplazar, convertir .doc heredados, renderizar una previsualización visual). NO la uses para: salidas PDF o data-light (pdf-writer), piezas visuales de una sola página (canvas-craft), web interactiva (web-craft), ni informes analíticos generados dentro de /analyze (que tiene su propio DOCXGenerator)."
argument-hint: "[brief describiendo qué DOCX construir o modificar]"
---

# Skill: DOCX Writer

Word es lo que muchos destinatarios abren por defecto. Un DOCX generado sin atención al diseño parece un accidente de procesador de texto: Calibri por todas partes, sin jerarquía, bordes grises sobre grises. Esta skill trata el DOCX como una superficie de salida que merece la misma deliberación que un PDF.

## 1. Flujo design-first

Toma cinco decisiones antes de tocar el builder:

1. **¿Qué tipo de documento es?** Carta, memo, contrato, nota de política, newsletter, informe multipágina, plantilla. La respuesta decide tono, ritmo y peso.
2. **¿Qué tono?** Editorial-serio, técnico-minimalista, cálido-revista, sobrio-legal, amable-moderno. Comprométete con uno. Un tono sin compromiso es la mayor causa de salidas genéricas.
3. **¿Qué par tipográfico?** Cuerpo que lea bien a 10–11 pt, fuente de display que se gane la atención en la página 1. Como las fuentes DOCX no viajan salvo que se embeban (§2), elige pares que se degraden bien: Calibri / Aptos / Arial son valores seguros; Crimson Pro + Instrument Sans o IBM Plex Serif + IBM Plex Mono exigen un paso de embedding.
4. **Paleta.** Un acento dominante (5–15% de la superficie), un neutro profundo para cuerpo, un neutro claro para fondos y colores de estado (éxito / warning / peligro) usados con parsimonia. Declarados en los presets de `palette.py` o sobrescritos vía `aesthetic_direction.palette_override`.
5. **Ritmo.** Márgenes (2.5 cm es el ISO por defecto), separación entre secciones, cuánto respira el blanco entre bloques. Un DOCX apretado se lee como un borrador; márgenes generosos, como el producto final.

## 2. Fuentes

DOCX usa las fuentes instaladas en el lector salvo que las embebas dentro de `word/fontTable.xml`. Consecuencias:

- **Camino por defecto**: usa tipografías instaladas de forma amplia (Calibri, Aptos, Arial, Times New Roman, Georgia, Cambria). Funciona en todas partes sin pasos extra.
- **Camino embedding**: elige cualquier display o cuerpo OFL y embébela vía python-docx o editando `fontTable.xml` tras construir. Aumenta el tamaño (~80–150 KB por familia) y solo se honra plenamente en Word 2016+ de Windows/macOS. LibreOffice y Word Online pueden sustituir.

`DOCXBuilder` conecta la clave `font_main` de la paleta al estilo `Normal` y usa `aesthetic_direction.font_pair[0]` (cuando se provee) para encabezados. Ese es el contrato mínimo.

## 3. Plantilla de arranque

```python
import sys
sys.path.insert(0, "shared-skills/docx-writer/scripts")

from docx_builder import DOCXBuilder

b = DOCXBuilder(
    page_size="A4",
    aesthetic_direction={
        "tone": "corporate",
        "font_pair": ["Instrument Serif", "Crimson Pro"],  # display, body
        "palette_override": {"primary": "#0a2540"},
    },
    author="Equipo de Cumplimiento",
)

b.add_cover(
    title="Política de retención de datos",
    subtitle="Regulación de los registros de cliente bajo el marco 2026",
    metadata={"Ref": "POL-042", "Versión": "1.0"},
)

b.add_heading("Alcance", level=1)
b.add_paragraph(
    "Este documento define cómo se retienen, archivan y eliminan los registros "
    "de cliente en los dominios de datos gobernados."
)

b.add_heading("Dimensiones", level=2)
b.add_table(
    headers=["Dimensión", "Compromiso"],
    rows=[
        ["Ventana de retención", "36 meses móviles"],
        ["Cifrado en reposo", "AES-256"],
        ["Auditoría de acceso", "Revisión trimestral"],
    ],
    caption="Resumen de los compromisos de alto nivel.",
)

b.add_callout(
    "Todas las cláusulas requieren aprobación legal explícita.",
    kind="warning",
)

b.set_footer_page_numbers(lang="es")
b.save("output/politica_retencion.docx")
```

## 4. Tablas que no parecen Excel

Una tabla DOCX sin decisiones de diseño se lee como un pantallazo de hoja de cálculo. El estilo `shaded-header` por defecto aplica:

- Fila de cabecera rellena con el color primario, texto en blanco, negrita, 10 pt.
- Filas del cuerpo con un fondo muy claro alternando.
- Un único filete inferior por fila en un color de borde sutil.
- Contenido monoespaciado en columnas numéricas (el llamante controla el formato de las cadenas).
- `cantSplit` en cada fila para evitar saltos de página en medio.
- La fila de cabecera marcada para repetirse al cambiar de página (`<w:tblHeader>`).

Prefiere `style="minimal"` cuando una cabecera rellena sea demasiado ruidosa (contextos legal / académico).

## 5. Trampas y reglas críticas

Verificadas contra `python-docx` y la spec ECMA-376:

- **Define explícitamente el tamaño de página** — el builder lo expone como primer argumento del constructor. A4 y Letter no son intercambiables; produce para el destino.
- **La paginación la decide el visor**. No intentes forzar saltos pixel-perfectos. Usa `cantSplit` en filas atómicas y `keep_with_next` / `keep_together` en pares figura + caption (el builder ya lo hace con figuras).
- **Repite la fila de cabecera en tablas largas**: el builder lo hace por defecto con `<w:tblHeader>`. Si lo desactivas, los lectores pierden contexto en la página dos.
- **Solo PNG para imágenes embebidas**: `python-docx` no acepta SVG. Convierte con `cairosvg` o `pillow` antes de `add_figure`.
- **Nunca insertes caracteres bullet Unicode manualmente** (`•`, `\u2022`). Usa `add_list(..., ordered=False)` que emplea la numeración nativa de Word — los bullets sobreviven al viaje a Google Docs y Word Online.
- **Los saltos de página deben vivir dentro de un párrafo**. `add_page_break()` emite un párrafo con `<w:br w:type="page"/>`.
- **Usa `ShadingType.CLEAR` para fondos de celda**. `SOLID` se renderiza como relleno negro en algunos visores (origen del bug "¿por qué mi celda es negra?"). El builder siempre usa `CLEAR`.
- **No uses tablas como reglas horizontales**. Las celdas tienen altura mínima y aparecen como cajas vacías en cabeceras / pies. Llama a `add_horizontal_rule()`, que emite un borde inferior a nivel de párrafo.
- **Override de estilos heading built-in con sus IDs exactos** (`Heading 1`, `Heading 2`, `Heading 3`, `Normal`, `Caption`). Nombres alternativos rompen la generación automática de TOC y la interoperabilidad.
- **Incluye `outlineLevel`** en cada estilo de heading si quieres TOC automático. El builder lo emite para H1-H3 (niveles 0-2).
- **Las figuras necesitan `keep_with_next`** para que el caption no quede huérfano. El builder lo activa automáticamente en `add_figure`.
- **`xml:space="preserve"` en `<w:t>` con espacios iniciales/finales**: relevante al usar `find_replace_docx` con cadenas que empiezan o acaban en espacio. El builder lo fija cuando hace falta dentro de la rutina de replace.

## 6. Operaciones estructurales

Fusionar varios DOCX, dividir uno por sección, find-replace con regex, convertir `.doc` binario heredado. Ver `STRUCTURAL_OPS.md` para comandos y ejemplos.

## 7. Cabeceras, pies y numeración de página

```python
b.set_footer_page_numbers(lang="es")  # "Página N" centrado en el pie
```

Para cabeceras más ricas (logos, títulos corrientes), accede a la sección subyacente:

```python
section = b.document.sections[0]
header = section.header
header.paragraphs[0].text = "Política de retención — Confidencial"
```

## 8. A4 vs Letter, apaisado

Argumentos del constructor:

```python
DOCXBuilder(page_size="A4")              # por defecto
DOCXBuilder(page_size="Letter")          # EE. UU.
DOCXBuilder(page_size="A4", orientation="landscape")
```

El builder no intercambia `page_width` / `page_height` en silencio en apaisado — los asigna explícitamente para que `python-docx` emita el XML correcto sea cual sea la resolución del visor.

## 9. Cuándo NO usar esta skill

- **DOCX de informe analítico dentro de `/analyze`**: usa el `DOCXGenerator` propio de la skill analyze — tiene un esqueleto opinado (resumen ejecutivo → metodología → análisis → conclusiones) que este builder no reproduce.
- **PDF tipográfico multipágina** (factura, contrato, informe largo en prosa): `pdf-writer` es la superficie correcta. El PDF preserva fuentes y layout exactamente; DOCX no puede igualar esa fidelidad.
- **Pieza visual de una sola página** (póster, portada, certificado): `canvas-craft`.
- **Frontend interactivo**: `web-craft`.
- **Informe de cobertura de calidad**: la skill `quality-report` tiene un generador de layout fijo afinado para ese contenido.

## 10. Validación visual

Tras construir, renderiza una previsualización PNG por página e inspecciónala multimodalmente:

```bash
python3 shared-skills/docx-writer/scripts/visual_validate.py \
  output/politica_retencion.docx \
  --out /tmp/preview --dpi 150
# stdout: lista de rutas de PNG
```

Si la salida se ve mal (desborde, márgenes apretados, acento escapado), ajusta `aesthetic_direction` y regenera. Itera hasta que la preview coincida con la intención declarada en las cinco decisiones de diseño.
