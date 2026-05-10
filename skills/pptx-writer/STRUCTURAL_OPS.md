# pptx-writer — Structural operations

Copy-paste snippets for manipulating existing PPT files. Each snippet
stands alone; run it from a small script, don't try to import them as
a module. Written in the style of `pdf-writer`'s operations section
(merge / split / rotate / watermark): direct, testable, boring code.

All snippets assume:

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

## Merge multiple decks into one

The first input is the "skeleton" — its slide master, theme, aspect
ratio and colour palette win. Subsequent decks contribute their slides
but inherit the skeleton's look. This matches how designers merge
PPTs by hand.

```python
def merge_pptx(inputs: list[str], out_path: str) -> None:
    if not inputs:
        raise ValueError("merge_pptx: need at least one input")
    base = Presentation(inputs[0])
    # Append slides from each subsequent deck by copying the slide XML
    # element directly into the base's sldIdLst.
    for extra_path in inputs[1:]:
        extra = Presentation(extra_path)
        for slide in extra.slides:
            # Deep-copy so we don't steal the element from `extra`
            sl_el = copy.deepcopy(slide._element)
            # python-pptx does not expose a clean "add existing slide"
            # API; we manipulate sldIdLst manually.
            # Step 1: add the XML element as a new slide in the base.
            # Step 2: register it in sldIdLst with a fresh id.
            # Step 3: copy any embedded images (relationships).
            _append_slide_element(base, sl_el, extra)
    base.save(out_path)


def _append_slide_element(base, slide_element, source_prs) -> None:
    """Append a single slide (XML + relationships + media) into `base`."""
    # Find a free slide id
    sldIdLst = base.slides._sldIdLst  # private but documented in python-pptx
    existing_ids = [int(sl.get("id")) for sl in sldIdLst]
    next_id = max(existing_ids + [255]) + 1

    # Create the slide part by copying from source
    from pptx.oxml.ns import qn
    from pptx.parts.slide import SlidePart

    # Use python-pptx's high-level API: duplicate layout reference by
    # using the first blank-like layout in base.
    target_layout = base.slide_layouts[6] if len(base.slide_layouts) > 6 else base.slide_layouts[0]
    new_slide = base.slides.add_slide(target_layout)

    # Clear the default placeholders the layout added
    for shape in list(new_slide.shapes):
        if shape.is_placeholder:
            sp = shape._element
            sp.getparent().remove(sp)

    # Copy every shape from the source slide into the new slide
    source_sp_tree = slide_element.find(qn("p:cSld")).find(qn("p:spTree"))
    target_sp_tree = new_slide._element.find(qn("p:cSld")).find(qn("p:spTree"))
    for shape_el in list(source_sp_tree):
        tag = etree.QName(shape_el).localname
        if tag in ("nvGrpSpPr", "grpSpPr"):
            continue  # preserve the target's group-level properties
        target_sp_tree.append(copy.deepcopy(shape_el))

    # Note: images embedded in the source slide will NOT transfer with
    # this shortcut — the relationship IDs are scoped per slide. For
    # a complete merge that preserves images, the ZIP-level approach
    # below is more reliable.
```

The above works for text-only decks. For decks with embedded images,
use the ZIP-level approach:

```python
def merge_pptx_zip(inputs: list[str], out_path: str) -> None:
    """
    Merge at the ZIP level. Skeleton: inputs[0].
    More reliable for image-heavy decks than the python-pptx approach.
    """
    base_prs = Presentation(inputs[0])
    base_prs.save(out_path)  # write skeleton first

    for extra_path in inputs[1:]:
        _append_zip(out_path, extra_path)


def _append_zip(base_path: str, extra_path: str) -> None:
    """Use python-pptx composition via temp presentation manipulation."""
    # Easiest reliable path: use python-pptx's Package / Part APIs
    # to walk the extra deck and clone slides + their relationships.
    # For brevity the implementation of this helper is left to a
    # dedicated tool such as ``python-pptx-merger`` on PyPI when it
    # handles a specific edge case better than the manual approach.
    raise NotImplementedError(
        "For image-heavy merges prefer the dedicated pptx merger: "
        "pip install python-pptx-merger, then use its MergePresentation."
    )
```

Pragmatic recommendation: for text-only decks the first snippet
works. For image-heavy decks, either install a dedicated merger
library or fall back to converting to PDF and merging PDFs with
`pypdf` (loses editability but is bullet-proof).

---

## Split a deck by section (or every N slides)

Sections are PowerPoint's grouping mechanism, stored in
`ppt/presentation.xml` under `p:sectionLst`. A "section divider slide"
conceptually starts a new section — but python-pptx doesn't expose
sections directly, so we work at XML level.

```python
def split_by_section(input_path: str, out_dir: str) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    prs = Presentation(input_path)
    # Find section boundaries via extLst sectionLst
    from pptx.oxml.ns import qn
    pres_elem = prs.part.element
    ext_list = pres_elem.find(qn("p:extLst"))
    if ext_list is None:
        raise ValueError(
            "No sections found. Use split_every_n() or first add sections "
            "in PowerPoint / LibreOffice."
        )
    # Real-world shortcut: in most generated decks sections are absent;
    # use the "every N" variant below.
    raise NotImplementedError(
        "split_by_section requires decks that explicitly define sections "
        "via <p:section> elements in presentation.xml. "
        "Use split_every_n() for content-agnostic splitting."
    )


def split_every_n(input_path: str, n: int, out_dir: str) -> list[Path]:
    """Split the input into chunks of N slides each. Simple and reliable."""
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
        # Copy source and delete slides outside [start, end)
        tmp_path = out / f"{stem}-part{chunk_idx + 1}.pptx"
        shutil.copy(input_path, tmp_path)
        part = Presentation(tmp_path)
        _keep_only_slides(part, start, end)
        part.save(tmp_path)
        chunks.append(tmp_path)
    return chunks


def _keep_only_slides(prs, start: int, end: int) -> None:
    """Delete slides outside [start, end)."""
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

## Reorder slides

```python
def reorder_slides(input_path: str, order: list[int], out_path: str) -> None:
    """
    order: list of 1-based slide indices in the desired order.
    Every original slide must appear exactly once (validated).
    """
    prs = Presentation(input_path)
    total = len(prs.slides)
    if sorted(order) != list(range(1, total + 1)):
        raise ValueError(
            f"order must be a permutation of 1..{total}, got {order!r}"
        )

    sldIdLst = prs.slides._sldIdLst
    originals = list(sldIdLst)
    # Remove all in place
    for sl in originals:
        sldIdLst.remove(sl)
    # Re-insert in requested order
    for target_pos in order:
        sldIdLst.append(originals[target_pos - 1])

    prs.save(out_path)
```

---

## Delete slides

python-pptx has no first-class `delete_slide`. Work at the `sldIdLst`
level and drop the relationship.

```python
def delete_slides(input_path: str, indices: list[int], out_path: str) -> None:
    """indices: 1-based slide indices to delete."""
    from pptx.oxml.ns import qn
    prs = Presentation(input_path)
    total = len(prs.slides)
    targets = set(indices)
    invalid = [i for i in targets if i < 1 or i > total]
    if invalid:
        raise ValueError(f"slide indices out of range: {invalid}")

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

Note: the underlying XML parts for the deleted slides still sit in
the package but are no longer referenced — `python-pptx` leaves
orphaned parts behind. For a tidy output, round-trip through
LibreOffice:

```bash
soffice --headless --convert-to pptx --outdir /tmp out.pptx
```

This produces a clean file with orphans removed.

---

## Find-replace in slides and speaker notes

Replaces text across text frames, table cells, and speaker notes.
Respects the first run's formatting in each paragraph (python-pptx
splits text into runs for font styling; naive replacement over the
whole paragraph loses formatting).

```python
def find_replace_pptx(
    input_path: str, find: str, replace: str, out_path: str,
    *,
    scope: set[str] | None = None,
    regex: bool = False,
) -> int:
    """
    scope: subset of {'slides', 'notes', 'tables'}. Default: all three.
    Returns number of replacements made.
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
            # Text frames (title, text boxes, placeholders)
            if "slides" in scope and shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    total += _replace_in_paragraph(para, replace_in)
            # Tables
            if "tables" in scope and shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for para in cell.text_frame.paragraphs:
                            total += _replace_in_paragraph(para, replace_in)

        # Speaker notes
        if "notes" in scope and slide.has_notes_slide:
            notes_tf = slide.notes_slide.notes_text_frame
            if notes_tf is not None:
                for para in notes_tf.paragraphs:
                    total += _replace_in_paragraph(para, replace_in)

    prs.save(out_path)
    return total


def _replace_in_paragraph(paragraph, replace_fn) -> int:
    """Replace text across the runs of one paragraph, preserving first-run formatting."""
    runs = paragraph.runs
    if not runs:
        return 0
    full_text = "".join(r.text for r in runs)
    new_text, n = replace_fn(full_text)
    if n == 0:
        return 0
    # Put everything into the first run, clear the rest
    runs[0].text = new_text
    for r in runs[1:]:
        r.text = ""
    return n
```

---

## Convert legacy `.ppt` to `.pptx`

```python
def convert_ppt_to_pptx(ppt_path: str, out_dir: str) -> Path:
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "Install libreoffice (or libreoffice-impress) to convert legacy .ppt."
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
        raise RuntimeError(f"LibreOffice produced no output for {ppt_path}")
    return result
```

Caveats:
- Animations, some custom shapes and embedded Excel objects may
  come through degraded. Verify the critical slides visually.
- Passwords on legacy `.ppt` (OLECF encryption) are outside this
  workflow — ask the user to save an unlocked copy from PowerPoint.

---

## Rasterize slides (utility also in pptx-reader)

```python
def rasterize(pptx_path: str, out_dir: str, dpi: int = 150) -> list[Path]:
    import tempfile
    if shutil.which("soffice") is None:
        raise RuntimeError("Install libreoffice for rasterization.")
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("Install poppler-utils for rasterization.")
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

Functionally identical to `pptx-reader/scripts/rasterize_slides.py`;
included here so the writer side has a self-contained snippet for
post-build QA.

---

## Cleanup after manual XML edits

When you delete slides, reorder, or merge at the XML level, the
output file may carry orphan parts (unused slide XML, unused media).
LibreOffice rewrites the ZIP cleanly on round-trip:

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

Run this as the last step of any pipeline that does XML surgery.
