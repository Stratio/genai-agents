# docx-writer — Structural operations

Operations that take one or more existing `.docx` files as input and produce a new `.docx` as output. All three are implemented in `scripts/structural_ops.py`, using only `zipfile` + `lxml` so the skill ships no transitive dependencies beyond the baseline.

Inputs are opened read-only. Outputs are written to the path you specify.

## Merge

Concatenate several DOCX bodies into a single document. The first input is used as the skeleton (its styles, numbering, default section properties are preserved); subsequent inputs contribute their body paragraphs and tables. A page break is inserted between each document.

```python
import sys
sys.path.insert(0, "shared-skills/docx-writer/scripts")

from structural_ops import merge_docx

merge_docx(
    paths=["cover.docx", "body.docx", "appendix.docx"],
    output="final.docx",
)
```

Notes:
- Final section properties (page size, margins, headers / footers) are inherited from the last input that declares them. Align orientations before merging if mixing portrait / landscape.
- Numbered lists may restart between documents because the source files have independent numbering definitions. Merging advanced numbering sequences with full continuity requires `docxcompose`; add it to requirements if you hit this case.
- Images embedded in subsequent documents are preserved (they live under `word/media/` with unique names that are already disjoint across files in practice; if you produce the inputs with `DOCXBuilder`, the IDs are stable).

## Split

Break one DOCX into multiple smaller DOCX files by a marker.

```python
from structural_ops import split_docx

parts = split_docx(
    path="long_report.docx",
    output_dir="parts/",
    by="heading-level",
    level=1,
    stem="chapter",
)
# parts == [Path("parts/chapter-01.docx"), Path("parts/chapter-02.docx"), ...]
```

Supported strategies:

- `by="heading-level"` with `level=N` — every paragraph styled `Heading N` starts a new part.
- `by="page-break"` — every explicit page break (`<w:br w:type="page"/>`) starts a new part.

Each produced part inherits the skeleton's styles, numbering and final section properties. Content before the first marker becomes the first part (useful when the source starts with a preamble).

## Find-replace

Literal or regular-expression find-replace inside `word/document.xml`, `word/header*.xml`, `word/footer*.xml`. The replacement preserves the formatting of the first run participating in each match; runs entirely inside the match range are wiped.

```python
from structural_ops import find_replace_docx

find_replace_docx(
    path="draft.docx",
    output="final.docx",
    mapping={
        "30 days": "60 days",
        "John Doe": "Jane Roe",
    },
)
```

Regex mode:

```python
find_replace_docx(
    path="source.docx",
    output="redacted.docx",
    mapping={r"[A-Z]{2}-\d{3,5}": "[REDACTED]"},
    use_regex=True,
)
```

Scope control — limit to the main body, or include headers / footers:

```python
find_replace_docx(
    path="in.docx", output="out.docx",
    mapping={"FY2025": "FY2026"},
    scope=["document", "headers", "footers"],  # default
)
```

Caveats:
- Text split across multiple runs (for example a word that the editor partially reformatted) is matched correctly because all `<w:t>` nodes of a paragraph are joined before matching.
- Rich inline formatting that varies across the matched range is collapsed to the first run's formatting. For surgical replacements inside heavily formatted prose, work at the XML level yourself — `python-docx` gives you the hooks.

## Convert legacy `.doc` to `.docx`

Binary Word 97–2003 files are not `.docx`. Convert first, then apply any of the operations above.

```python
from structural_ops import convert_doc_to_docx

new_path = convert_doc_to_docx("legacy_policy.doc", output_dir="/tmp/converted/")
```

Requires `libreoffice` / `libreoffice-writer` on `$PATH` (`soffice` must be callable headlessly). Raises `RuntimeError` otherwise.

CLI equivalent (for ad-hoc use):

```bash
python3 shared-skills/docx-writer/scripts/convert_doc_to_docx.py legacy_policy.doc --out-dir /tmp/converted
```

## Visual preview (not strictly structural)

Render the DOCX to per-page PNGs for layout inspection. Useful after a merge / split / replace to confirm nothing visually broke:

```bash
python3 shared-skills/docx-writer/scripts/visual_validate.py final.docx \
  --out /tmp/final_preview --dpi 150
# one PNG per page is printed to stdout
```

Pipeline under the hood: `soffice --convert-to pdf` then `pdftoppm -png -r <dpi>`. Both system tools must be installed; on the sandbox image they already are.

## Content controls (Word "form" templates)

Filling `<w:sdt>` content controls in DOCX templates is on-demand — not part of this skill's default API. Open an issue if you need it; the implementation path is a dedicated script that walks `document.xml` for `<w:sdt>` elements and rewrites their `<w:sdtContent>` bodies while preserving the `<w:sdtPr>` binding.
