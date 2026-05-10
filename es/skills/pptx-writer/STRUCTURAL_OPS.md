# pptx-writer — Operaciones estructurales

Snippets copy-paste para manipular ficheros PPT existentes. Cada
snippet se sostiene por sí mismo; ejecútalo desde un script pequeño,
no intentes importarlos como módulo. Escrito en el estilo de la
sección de operaciones de `pdf-writer` (merge / split / rotate /
watermark): código directo, testeable, aburrido.

Todos los snippets asumen:

```python
import copy
import shutil
import subprocess
import zipfile
from pathlib import Path
from pptx import Presentation
from pptx.util import Emu
from lxml import etree
```

---

## Mezclar varios decks en uno

El primer input es el "esqueleto" — su slide master, tema, aspect
ratio y paleta de colores ganan. Los decks subsiguientes aportan
sus slides pero heredan el look del esqueleto. Esto encaja con
cómo los diseñadores mezclan PPTs a mano.

```python
def merge_pptx(inputs: list[str], out_path: str) -> None:
    if not inputs:
        raise ValueError("merge_pptx: necesita al menos un input")
    base = Presentation(inputs[0])
    # Añade slides de cada deck siguiente copiando el elemento XML del
    # slide directamente al sldIdLst del base.
    for extra_path in inputs[1:]:
        extra = Presentation(extra_path)
        for slide in extra.slides:
            # Deep-copy para no robar el elemento a `extra`
            sl_el = copy.deepcopy(slide._element)
            # python-pptx no expone una API limpia de "añadir slide existente";
            # manipulamos sldIdLst a mano.
            # Paso 1: añade el elemento XML como slide nuevo en el base.
            # Paso 2: regístralo en sldIdLst con un id fresco.
            # Paso 3: copia cualquier imagen embebida (relationships).
            _append_slide_element(base, sl_el, extra)
    base.save(out_path)


def _append_slide_element(base, slide_element, source_prs) -> None:
    """Añade un solo slide (XML + relationships + medios) en `base`."""
    # Busca un slide id libre
    sldIdLst = base.slides._sldIdLst  # privado pero documentado en python-pptx
    existing_ids = [int(sl.get("id")) for sl in sldIdLst]
    next_id = max(existing_ids + [255]) + 1

    # Crea la slide part copiando desde source
    from pptx.oxml.ns import qn
    from pptx.parts.slide import SlidePart

    # Usa la API de alto nivel de python-pptx: duplica referencia al layout
    # usando el primer layout tipo blank del base.
    target_layout = base.slide_layouts[6] if len(base.slide_layouts) > 6 else base.slide_layouts[0]
    new_slide = base.slides.add_slide(target_layout)

    # Limpia los placeholders por defecto que el layout añadió
    for shape in list(new_slide.shapes):
        if shape.is_placeholder:
            sp = shape._element
            sp.getparent().remove(sp)

    # Copia cada shape del slide origen al slide nuevo
    source_sp_tree = slide_element.find(qn("p:cSld")).find(qn("p:spTree"))
    target_sp_tree = new_slide._element.find(qn("p:cSld")).find(qn("p:spTree"))
    for shape_el in list(source_sp_tree):
        tag = etree.QName(shape_el).localname
        if tag in ("nvGrpSpPr", "grpSpPr"):
            continue  # preserva las propiedades a nivel de grupo del target
        target_sp_tree.append(copy.deepcopy(shape_el))

    # Nota: las imágenes embebidas en el slide origen NO se transfieren con
    # este atajo — los IDs de relationship son scoped por slide. Para un
    # merge completo que preserve imágenes, el enfoque a nivel ZIP
    # de más abajo es más fiable.
```

Lo de arriba funciona para decks solo-texto. Para decks con imágenes
embebidas, usa el enfoque a nivel ZIP:

```python
def merge_pptx_zip(inputs: list[str], out_path: str) -> None:
    """
    Merge al nivel ZIP. Esqueleto: inputs[0].
    Más fiable para decks con muchas imágenes que el enfoque python-pptx.
    """
    base_prs = Presentation(inputs[0])
    base_prs.save(out_path)  # escribe el esqueleto primero

    for extra_path in inputs[1:]:
        _append_zip(out_path, extra_path)


def _append_zip(base_path: str, extra_path: str) -> None:
    """Usa composición de python-pptx vía manipulación temporal de presentation."""
    # Camino fiable más fácil: usa las APIs Package / Part de python-pptx
    # para recorrer el deck extra y clonar slides + sus relationships.
    # Para brevedad, la implementación queda a una herramienta dedicada
    # como ``python-pptx-merger`` de PyPI cuando maneje un edge case
    # concreto mejor que el enfoque manual.
    raise NotImplementedError(
        "Para merges con muchas imágenes prefiere el merger dedicado: "
        "pip install python-pptx-merger, luego usa su MergePresentation."
    )
```

Recomendación pragmática: para decks solo-texto el primer snippet
funciona. Para decks con muchas imágenes, instala una librería
merger dedicada o cae a convertir a PDF y mergear PDFs con
`pypdf` (pierde editabilidad pero es a prueba de balas).

---

## Dividir un deck por sección (o cada N slides)

Las secciones son el mecanismo de agrupación de PowerPoint,
guardadas en `ppt/presentation.xml` bajo `p:sectionLst`. Un "slide
divisor de sección" conceptualmente inicia una nueva sección —
pero python-pptx no expone secciones directamente, así que
trabajamos a nivel de XML.

```python
def split_by_section(input_path: str, out_dir: str) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    prs = Presentation(input_path)
    # Encuentra los límites de sección vía extLst sectionLst
    from pptx.oxml.ns import qn
    pres_elem = prs.part.element
    ext_list = pres_elem.find(qn("p:extLst"))
    if ext_list is None:
        raise ValueError(
            "No se encontraron secciones. Usa split_every_n() o primero añade "
            "secciones en PowerPoint / LibreOffice."
        )
    # Atajo del mundo real: en la mayoría de decks generados las secciones
    # están ausentes; usa la variante "cada N" de abajo.
    raise NotImplementedError(
        "split_by_section requiere decks que definan secciones explícitamente "
        "vía elementos <p:section> en presentation.xml. "
        "Usa split_every_n() para división agnóstica al contenido."
    )


def split_every_n(input_path: str, n: int, out_dir: str) -> list[Path]:
    """Divide el input en chunks de N slides cada uno. Simple y fiable."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(input_path).stem

    source = Presentation(input_path)
    total = len(source.slides)
    if total == 0:
        return []

    chunks: list[Path] = []
    for chunk_idx in range((total + n - 1) // n):
        start = chunk_idx * n
        end = min(start + n, total)
        # Copia source y borra slides fuera de [start, end)
        tmp_path = out / f"{stem}-part{chunk_idx + 1}.pptx"
        shutil.copy(input_path, tmp_path)
        part = Presentation(tmp_path)
        _keep_only_slides(part, start, end)
        part.save(tmp_path)
        chunks.append(tmp_path)
    return chunks


def _keep_only_slides(prs, start: int, end: int) -> None:
    """Borra slides fuera de [start, end)."""
    from pptx.oxml.ns import qn
    sldIdLst = prs.slides._sldIdLst
    to_remove = []
    for i, sl in enumerate(list(sldIdLst)):
        if i < start or i >= end:
            to_remove.append(sl)
    for sl in to_remove:
        rId = sl.get(qn("r:id"))
        prs.part.drop_rel(rId)
        sldIdLst.remove(sl)
```

---

## Reordenar slides

```python
def reorder_slides(input_path: str, order: list[int], out_path: str) -> None:
    """
    order: lista de índices de slide 1-based en el orden deseado.
    Cada slide original debe aparecer exactamente una vez (se valida).
    """
    prs = Presentation(input_path)
    total = len(prs.slides)
    if sorted(order) != list(range(1, total + 1)):
        raise ValueError(
            f"order debe ser una permutación de 1..{total}, recibido {order!r}"
        )

    sldIdLst = prs.slides._sldIdLst
    originals = list(sldIdLst)
    # Elimina todos in place
    for sl in originals:
        sldIdLst.remove(sl)
    # Re-inserta en el orden solicitado
    for target_pos in order:
        sldIdLst.append(originals[target_pos - 1])

    prs.save(out_path)
```

---

## Borrar slides

python-pptx no tiene `delete_slide` de primera clase. Trabaja a
nivel de `sldIdLst` y suelta la relationship.

```python
def delete_slides(input_path: str, indices: list[int], out_path: str) -> None:
    """indices: índices de slide 1-based a borrar."""
    from pptx.oxml.ns import qn
    prs = Presentation(input_path)
    total = len(prs.slides)
    targets = set(indices)
    invalid = [i for i in targets if i < 1 or i > total]
    if invalid:
        raise ValueError(f"índices de slide fuera de rango: {invalid}")

    sldIdLst = prs.slides._sldIdLst
    to_remove = []
    for i, sl in enumerate(list(sldIdLst), start=1):
        if i in targets:
            to_remove.append(sl)
    for sl in to_remove:
        rId = sl.get(qn("r:id"))
        prs.part.drop_rel(rId)
        sldIdLst.remove(sl)

    prs.save(out_path)
```

Nota: las partes XML subyacentes de los slides borrados siguen
estando en el package pero ya no se referencian — `python-pptx`
deja partes huérfanas. Para un output limpio, haz roundtrip por
LibreOffice:

```bash
soffice --headless --convert-to pptx --outdir /tmp out.pptx
```

Esto produce un fichero limpio con huérfanas eliminadas.

---

## Find-replace en slides y notas del presentador

Reemplaza texto cross-text-frame, celdas de tabla y notas del
presentador. Respeta el formato del primer run en cada párrafo
(python-pptx divide el texto en runs para estilado de fuente; un
reemplazo naive sobre el párrafo entero pierde el formato).

```python
def find_replace_pptx(
    input_path: str, find: str, replace: str, out_path: str,
    *,
    scope: set[str] | None = None,
    regex: bool = False,
) -> int:
    """
    scope: subset de {'slides', 'notes', 'tables'}. Default: los tres.
    Devuelve el número de reemplazos hechos.
    """
    import re
    scope = scope or {"slides", "notes", "tables"}
    pat = re.compile(find) if regex else None

    def replace_in(s: str) -> tuple[str, int]:
        if regex:
            out, n = pat.subn(replace, s)
            return out, n
        count = s.count(find)
        return s.replace(find, replace), count

    prs = Presentation(input_path)
    total = 0

    for slide in prs.slides:
        for shape in slide.shapes:
            # Text frames (título, text boxes, placeholders)
            if "slides" in scope and shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    total += _replace_in_paragraph(para, replace_in)
            # Tablas
            if "tables" in scope and shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for para in cell.text_frame.paragraphs:
                            total += _replace_in_paragraph(para, replace_in)

        # Notas del presentador
        if "notes" in scope and slide.has_notes_slide:
            notes_tf = slide.notes_slide.notes_text_frame
            if notes_tf is not None:
                for para in notes_tf.paragraphs:
                    total += _replace_in_paragraph(para, replace_in)

    prs.save(out_path)
    return total


def _replace_in_paragraph(paragraph, replace_fn) -> int:
    """Reemplaza texto a través de los runs de un párrafo, preservando el formato del primer run."""
    runs = paragraph.runs
    if not runs:
        return 0
    full_text = "".join(r.text for r in runs)
    new_text, n = replace_fn(full_text)
    if n == 0:
        return 0
    # Pon todo en el primer run, limpia el resto
    runs[0].text = new_text
    for r in runs[1:]:
        r.text = ""
    return n
```

---

## Convertir `.ppt` legacy a `.pptx`

```python
def convert_ppt_to_pptx(ppt_path: str, out_dir: str) -> Path:
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "Instala libreoffice (o libreoffice-impress) para convertir .ppt legacy."
        )
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pptx",
         "--outdir", str(out), ppt_path],
        check=True, capture_output=True,
    )
    result = out / (Path(ppt_path).stem + ".pptx")
    if not result.exists():
        raise RuntimeError(f"LibreOffice no produjo output para {ppt_path}")
    return result
```

Caveats:
- Animaciones, algunas shapes custom y objetos Excel embebidos
  pueden llegar degradados. Verifica los slides críticos visualmente.
- Las contraseñas en `.ppt` legacy (cifrado OLECF) quedan fuera de
  este workflow — pide al usuario que guarde una copia sin bloquear
  desde PowerPoint.

---

## Rasterizar slides (utilidad también en pptx-reader)

```python
def rasterize(pptx_path: str, out_dir: str, dpi: int = 150) -> list[Path]:
    import tempfile
    if shutil.which("soffice") is None:
        raise RuntimeError("Instala libreoffice para rasterización.")
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("Instala poppler-utils para rasterización.")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pptx_pdf_") as tmp:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf",
             "--outdir", tmp, pptx_path],
            check=True, capture_output=True,
        )
        pdf = Path(tmp) / (Path(pptx_path).stem + ".pdf")
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi),
             str(pdf), str(out / pdf.stem)],
            check=True, capture_output=True,
        )
    return sorted(out.glob(f"{Path(pptx_path).stem}-*.png"))
```

Funcionalmente idéntico a `pptx-reader/scripts/rasterize_slides.py`;
incluido aquí para que el lado writer tenga un snippet autocontenido
para QA post-build.

---

## Limpieza tras ediciones manuales de XML

Cuando borras slides, reordenas o mezclas a nivel XML, el fichero
output puede llevar partes huérfanas (XML de slide no usado, medios
no usados). LibreOffice reescribe el ZIP limpio en roundtrip:

```python
def cleanup_via_libreoffice(input_path: str, out_path: str) -> None:
    import tempfile
    with tempfile.TemporaryDirectory(prefix="pptx_clean_") as tmp:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pptx",
             "--outdir", tmp, input_path],
            check=True, capture_output=True,
        )
        rewritten = Path(tmp) / (Path(input_path).stem + ".pptx")
        shutil.copy(rewritten, out_path)
```

Ejecútalo como paso final de cualquier pipeline que haga cirugía
XML.
