# docx-writer — Structural operations

Copy-paste snippets for operations that take one or more existing
`.docx` files as input and produce a new `.docx` as output. All are
implemented on top of `zipfile` + `lxml` so you don't need any
compose/merge dependency beyond the baseline.

Inputs are opened read-only. Outputs are written to the path you
specify — the inputs are never modified in place.

All snippets share this preamble:

```python
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable, Sequence

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
Q_T = f"{{{W_NS}}}t"
Q_P = f"{{{W_NS}}}p"


def _read_xml(zf: zipfile.ZipFile, name: str):
    with zf.open(name) as f:
        return etree.parse(f).getroot()


def _write_zip(source_zip, output, overrides, extra=None):
    """Copy ``source_zip`` into ``output`` replacing entries from
    ``overrides`` and optionally adding any entries from ``extra``
    that are not already in the source.
    """
    source_zip = Path(source_zip)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    extra = extra or {}
    written = set(overrides.keys())
    with zipfile.ZipFile(source_zip) as src, zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED,
    ) as dst:
        for item in src.infolist():
            if item.filename in overrides:
                dst.writestr(item, overrides[item.filename])
            else:
                dst.writestr(item, src.read(item.filename))
        for name, data in extra.items():
            if name in written or name in src.namelist():
                continue
            dst.writestr(name, data)
    return output
```

---

## Merge

Concatenate several DOCX bodies into a single document. The first
input is used as the skeleton (its styles, numbering, default section
properties are preserved); subsequent inputs contribute their body
paragraphs and tables. A page break is inserted between each
document.

```python
def merge_docx(paths: Sequence[str | Path], output: str | Path) -> Path:
    inputs = [Path(p) for p in paths]
    if not inputs:
        raise ValueError("merge_docx: at least one input is required")
    output_path = Path(output)

    with zipfile.ZipFile(inputs[0]) as z0:
        base_doc = _read_xml(z0, "word/document.xml")
    base_body = base_doc.find("w:body", NS)
    if base_body is None:
        raise RuntimeError("skeleton input has no <w:body>")

    # Section properties live at the end of the body. Move them aside;
    # reattach only on the last merged body.
    base_sect_pr = base_body.find("w:sectPr", NS)
    if base_sect_pr is not None:
        base_body.remove(base_sect_pr)

    final_sect_pr = base_sect_pr

    for other in inputs[1:]:
        with zipfile.ZipFile(other) as zn:
            other_doc = _read_xml(zn, "word/document.xml")
        other_body = other_doc.find("w:body", NS)
        if other_body is None:
            continue
        other_sect = other_body.find("w:sectPr", NS)
        if other_sect is not None:
            other_body.remove(other_sect)
            final_sect_pr = other_sect

        # Page break before the next document's content.
        br_para = etree.SubElement(base_body, Q_P)
        r = etree.SubElement(br_para, f"{{{W_NS}}}r")
        br = etree.SubElement(r, f"{{{W_NS}}}br")
        br.set(f"{{{W_NS}}}type", "page")

        for child in list(other_body):
            base_body.append(child)

    if final_sect_pr is not None:
        base_body.append(final_sect_pr)

    new_document_xml = etree.tostring(
        base_doc, xml_declaration=True, encoding="UTF-8", standalone=True,
    )
    return _write_zip(
        inputs[0], output_path, {"word/document.xml": new_document_xml},
    )


# Usage
merge_docx(
    paths=["cover.docx", "body.docx", "appendix.docx"],
    output="final.docx",
)
```

Caveats:
- Final section properties (page size, margins, headers / footers)
  are inherited from the last input that declares them. Align
  orientations before merging if you're mixing portrait and landscape.
- Numbered lists may restart between documents because each source
  has independent numbering definitions. If you need continuous
  numbering across merged parts, reach for `docxcompose` instead.
- Images embedded inside subsequent documents are preserved because
  they live under `word/media/` with names that are disjoint in
  practice; if you generated the inputs yourself the IDs are stable.

---

## Split

Break one DOCX into multiple smaller DOCX files by a marker.
Supported strategies:

- `by="heading-level"` with `level=N` — every paragraph styled
  `Heading N` starts a new part.
- `by="page-break"` — every explicit page break
  (`<w:br w:type="page"/>`) starts a new part.

Each produced part inherits the skeleton's styles, numbering and
final section properties. Content before the first marker becomes
the first part.

```python
def _paragraph_has_style(p, style_ids: set[str]) -> bool:
    p_pr = p.find("w:pPr", NS)
    if p_pr is None:
        return False
    p_style = p_pr.find("w:pStyle", NS)
    if p_style is None:
        return False
    val = p_style.get(f"{{{W_NS}}}val")
    return val in style_ids


def _paragraph_has_page_break(p) -> bool:
    for br in p.iter(f"{{{W_NS}}}br"):
        if br.get(f"{{{W_NS}}}type") == "page":
            return True
    return False


def split_docx(path, output_dir, by: str = "heading-level",
               level: int = 1, stem: str = "part") -> list[Path]:
    input_path = Path(path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(input_path) as z:
        doc = _read_xml(z, "word/document.xml")
    body = doc.find("w:body", NS)
    if body is None:
        raise RuntimeError("input has no <w:body>")

    sect_pr = body.find("w:sectPr", NS)
    if sect_pr is not None:
        body.remove(sect_pr)

    groups: list[list] = []
    current: list = []

    def _start_new_group():
        nonlocal current
        if current:
            groups.append(current)
        current = []

    if by == "heading-level":
        style_ids = {f"Heading{level}", f"Heading {level}"}
        for el in list(body):
            if el.tag == Q_P and _paragraph_has_style(el, style_ids):
                _start_new_group()
            current.append(el)
    elif by == "page-break":
        for el in list(body):
            if el.tag == Q_P and _paragraph_has_page_break(el):
                _start_new_group()
            current.append(el)
    else:
        raise ValueError(f"unknown split strategy: {by}")

    if current:
        groups.append(current)

    outputs: list[Path] = []
    for idx, group in enumerate(groups, start=1):
        new_doc = etree.fromstring(etree.tostring(doc))
        new_body = new_doc.find("w:body", NS)
        for existing in list(new_body):
            new_body.remove(existing)
        for el in group:
            new_body.append(etree.fromstring(etree.tostring(el)))
        if sect_pr is not None:
            new_body.append(etree.fromstring(etree.tostring(sect_pr)))
        out_path = out_dir / f"{stem}-{idx:02d}.docx"
        new_xml = etree.tostring(
            new_doc, xml_declaration=True, encoding="UTF-8", standalone=True,
        )
        _write_zip(input_path, out_path, {"word/document.xml": new_xml})
        outputs.append(out_path)
    return outputs


# Usage
parts = split_docx(
    path="long_report.docx",
    output_dir="parts/",
    by="heading-level",
    level=1,
    stem="chapter",
)
# parts == [Path("parts/chapter-01.docx"), Path("parts/chapter-02.docx"), ...]
```

---

## Find-replace

Literal or regex find-replace inside `word/document.xml`,
`word/header*.xml`, `word/footer*.xml`. The replacement preserves
the formatting of the first run participating in each match; runs
entirely inside the match range are wiped.

```python
def _resolve_scope(input_path: Path, scope: Iterable[str]) -> list[str]:
    want = set(scope)
    out: list[str] = []
    with zipfile.ZipFile(input_path) as z:
        names = z.namelist()
    if "document" in want and "word/document.xml" in names:
        out.append("word/document.xml")
    if "headers" in want:
        out.extend(
            n for n in names
            if n.startswith("word/header") and n.endswith(".xml")
        )
    if "footers" in want:
        out.extend(
            n for n in names
            if n.startswith("word/footer") and n.endswith(".xml")
        )
    return out


def _replace_in_paragraph(paragraph, compiled: dict) -> None:
    t_nodes = list(paragraph.iter(Q_T))
    if not t_nodes:
        return
    full_text = "".join(t.text or "" for t in t_nodes)
    new_text = full_text
    hit = False
    for pattern, replacement in compiled.items():
        candidate = pattern.sub(replacement, new_text)
        if candidate != new_text:
            hit = True
        new_text = candidate
    if not hit or new_text == full_text:
        return

    # Keep the first run's formatting; fold the whole replaced string
    # into it and wipe the rest. Loses granular formatting across the
    # run range but is deterministic.
    t_nodes[0].text = new_text
    if new_text != new_text.strip():
        t_nodes[0].set(
            "{http://www.w3.org/XML/1998/namespace}space", "preserve",
        )
    for leftover in t_nodes[1:]:
        leftover.text = ""


def find_replace_docx(
    path, output, mapping: dict,
    use_regex: bool = False,
    scope: Iterable[str] = ("document", "headers", "footers"),
) -> Path:
    input_path = Path(path)
    output_path = Path(output)
    parts = _resolve_scope(input_path, scope)
    compiled = {
        (re.compile(k) if use_regex else re.compile(re.escape(k))): v
        for k, v in mapping.items()
    }
    overrides: dict = {}
    for part_name in parts:
        with zipfile.ZipFile(input_path) as z:
            doc = _read_xml(z, part_name)
        for paragraph in doc.iter(Q_P):
            _replace_in_paragraph(paragraph, compiled)
        overrides[part_name] = etree.tostring(
            doc, xml_declaration=True, encoding="UTF-8", standalone=True,
        )
    return _write_zip(input_path, output_path, overrides)


# Literal usage
find_replace_docx(
    path="draft.docx", output="final.docx",
    mapping={"30 days": "60 days", "John Doe": "Jane Roe"},
)

# Regex usage
find_replace_docx(
    path="source.docx", output="redacted.docx",
    mapping={r"[A-Z]{2}-\d{3,5}": "[REDACTED]"},
    use_regex=True,
)

# Scope control — only the main body, skip headers and footers
find_replace_docx(
    path="in.docx", output="out.docx",
    mapping={"FY2025": "FY2026"},
    scope=["document"],
)
```

Caveats:
- Text split across multiple runs (for example a word that the
  editor partially reformatted) is matched correctly because all
  `<w:t>` nodes of a paragraph are joined before matching.
- Rich inline formatting that varies across the matched range is
  collapsed to the first run's formatting. For surgical replacements
  inside heavily formatted prose, work at the XML level yourself —
  the snippet above is a readable starting point.

---

## Convert legacy `.doc` to `.docx`

Binary Word 97–2003 files are not `.docx`. Convert first, then apply
any of the operations above.

```python
def convert_doc_to_docx(input_path, output_dir=None) -> Path:
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(src)
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "LibreOffice headless (soffice) not found on PATH. "
            "Install libreoffice or libreoffice-writer."
        )
    out_dir = Path(output_dir) if output_dir else Path(
        tempfile.mkdtemp(prefix="docx_conv_")
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "docx",
         "--outdir", str(out_dir), str(src)],
        check=True, capture_output=True,
    )
    produced = out_dir / (src.stem + ".docx")
    if not produced.exists():
        raise RuntimeError(f"LibreOffice produced no output for {src}")
    return produced


# Usage
new_path = convert_doc_to_docx("legacy_policy.doc",
                               output_dir="/tmp/converted/")
```

CLI equivalent:

```bash
soffice --headless --convert-to docx legacy_policy.doc --outdir /tmp/converted
```

---

## Visual preview

Render the DOCX to per-page PNGs for layout inspection. Useful after
a merge / split / replace to confirm nothing visually broke. The
snippet lives in `REFERENCE.md` §Visual validation pipeline.

```bash
soffice --headless --convert-to pdf --outdir /tmp/preview final.docx
pdftoppm -r 150 -png /tmp/preview/final.pdf /tmp/preview/page
```

---

## Content controls (Word form templates)

Filling `<w:sdt>` content controls in DOCX templates is not part of
this skill's default surface. The read-only inspection snippet lives
in `REFERENCE.md` §Content controls. For writing, walk `document.xml`
for `<w:sdt>` elements and rewrite their `<w:sdtContent>` bodies
while preserving the `<w:sdtPr>` binding.
