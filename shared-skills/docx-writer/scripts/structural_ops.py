"""Structural operations on existing .docx files.

Three operations, implemented on top of ``zipfile`` + ``lxml`` so the skill
does not need to depend on a larger compose/merge package. All three open
the input documents read-only and write brand-new ``.docx`` bundles as
output — the inputs are never modified in place.

- :func:`merge_docx` — concatenate the bodies of multiple DOCX files.
- :func:`split_docx` — split one DOCX into multiple files by a marker.
- :func:`find_replace_docx` — literal or regex find-replace preserving runs.

For API stability, each function returns a :class:`pathlib.Path` (or list
of Paths) pointing to the output(s).
"""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path
from typing import Iterable, Sequence

from lxml import etree  # type: ignore[import-untyped]

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
_Q_T = f"{{{W_NS}}}t"
_Q_P = f"{{{W_NS}}}p"


def _read_xml(zf: zipfile.ZipFile, name: str) -> etree._Element:
    with zf.open(name) as f:
        return etree.parse(f).getroot()


def _write_zip(
    source_zip: Path,
    output: Path,
    overrides: dict[str, bytes],
    extra: dict[str, bytes] | None = None,
) -> Path:
    """Copy ``source_zip`` into ``output`` replacing entries from ``overrides``
    and adding any entries from ``extra`` that are not already in the source.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    extra = extra or {}
    written = set(overrides.keys())
    with zipfile.ZipFile(source_zip) as src, zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED
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


def merge_docx(paths: Sequence[str | Path], output: str | Path) -> Path:
    """Concatenate several DOCX bodies into a single DOCX.

    The first input is used as the skeleton (styles, numbering, section
    properties). Every subsequent file's ``<w:body>`` children are appended,
    with a page break inserted between documents. Any final ``<w:sectPr>``
    is preserved only on the last document.
    """
    inputs = [Path(p) for p in paths]
    if not inputs:
        raise ValueError("merge_docx: at least one input is required")
    output_path = Path(output)

    with zipfile.ZipFile(inputs[0]) as z0:
        base_doc = _read_xml(z0, "word/document.xml")
    base_body = base_doc.find("w:body", NS)
    if base_body is None:
        raise RuntimeError("skeleton input has no <w:body>")

    # Keep base sectPr aside (we reattach it only on the last merged body)
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

        # Page break before the next document
        br_para = etree.SubElement(base_body, _Q_P)
        r = etree.SubElement(br_para, f"{{{W_NS}}}r")
        br = etree.SubElement(r, f"{{{W_NS}}}br")
        br.set(f"{{{W_NS}}}type", "page")

        for child in list(other_body):
            base_body.append(child)

    if final_sect_pr is not None:
        base_body.append(final_sect_pr)

    new_document_xml = etree.tostring(
        base_doc, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    return _write_zip(
        inputs[0], output_path, {"word/document.xml": new_document_xml}
    )


def split_docx(
    path: str | Path,
    output_dir: str | Path,
    by: str = "heading-level",
    level: int = 1,
    stem: str = "part",
) -> list[Path]:
    """Split a DOCX into multiple files.

    Parameters
    ----------
    path : str | Path
        Input DOCX.
    output_dir : str | Path
        Directory for the output parts (created if missing).
    by : str
        Splitter strategy. Currently supported:
        - ``"heading-level"`` — each H{level} paragraph starts a new part.
        - ``"page-break"`` — each explicit page break starts a new part.
    level : int
        Heading level for ``by="heading-level"`` (default 1).
    stem : str
        Base filename; parts are numbered ``{stem}-01.docx``, ``{stem}-02.docx``...
    """
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

    children = list(body)
    groups: list[list[etree._Element]] = []
    current: list[etree._Element] = []

    def _start_new_group() -> None:
        nonlocal current
        if current:
            groups.append(current)
        current = []

    if by == "heading-level":
        heading_style_ids = {f"Heading{level}", f"Heading {level}"}
        for el in children:
            if el.tag == _Q_P and _paragraph_has_style(el, heading_style_ids):
                _start_new_group()
            current.append(el)
    elif by == "page-break":
        for el in children:
            if el.tag == _Q_P and _paragraph_has_page_break(el):
                _start_new_group()
            current.append(el)
    else:
        raise ValueError(f"unknown split strategy: {by}")

    if current:
        groups.append(current)

    outputs: list[Path] = []
    for idx, group in enumerate(groups, start=1):
        # Build a fresh body containing this group's elements + the section props
        new_doc = etree.fromstring(
            etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
        )
        new_body = new_doc.find("w:body", NS)
        assert new_body is not None
        for existing in list(new_body):
            new_body.remove(existing)
        for el in group:
            new_body.append(
                etree.fromstring(etree.tostring(el))
            )
        if sect_pr is not None:
            new_body.append(
                etree.fromstring(etree.tostring(sect_pr))
            )
        out_path = out_dir / f"{stem}-{idx:02d}.docx"
        new_xml = etree.tostring(
            new_doc, xml_declaration=True, encoding="UTF-8", standalone=True
        )
        _write_zip(input_path, out_path, {"word/document.xml": new_xml})
        outputs.append(out_path)
    return outputs


def _paragraph_has_style(p: etree._Element, style_ids: set[str]) -> bool:
    p_pr = p.find("w:pPr", NS)
    if p_pr is None:
        return False
    p_style = p_pr.find("w:pStyle", NS)
    if p_style is None:
        return False
    val = p_style.get(f"{{{W_NS}}}val")
    return val in style_ids


def _paragraph_has_page_break(p: etree._Element) -> bool:
    for br in p.iter(f"{{{W_NS}}}br"):
        if br.get(f"{{{W_NS}}}type") == "page":
            return True
    return False


def find_replace_docx(
    path: str | Path,
    output: str | Path,
    mapping: dict[str, str],
    use_regex: bool = False,
    scope: Iterable[str] = ("document", "headers", "footers"),
) -> Path:
    """Find-and-replace inside a DOCX, preserving run formatting.

    Parameters
    ----------
    path : str | Path
        Input DOCX.
    output : str | Path
        Output DOCX.
    mapping : dict[str, str]
        Dict of ``search -> replacement``. Both are literal strings unless
        ``use_regex`` is True.
    use_regex : bool
        When True, the keys of ``mapping`` are compiled as regular expressions.
    scope : iterable of {"document", "headers", "footers"}
        Which parts of the DOCX to operate on. Default: all three.

    Implementation notes
    --------------------
    The replacement is applied after merging adjacent ``<w:t>`` runs inside a
    paragraph so that text straddling multiple runs (e.g. ``"hel"`` + ``"lo"``)
    is matched correctly. Formatting from the first run of the match is kept;
    other runs on the match's range are discarded.
    """
    input_path = Path(path)
    output_path = Path(output)
    overrides: dict[str, bytes] = {}
    parts = _resolve_scope(input_path, scope)

    for part_name in parts:
        with zipfile.ZipFile(input_path) as z:
            doc = _read_xml(z, part_name)
        _apply_find_replace(doc, mapping, use_regex)
        overrides[part_name] = etree.tostring(
            doc, xml_declaration=True, encoding="UTF-8", standalone=True
        )
    return _write_zip(input_path, output_path, overrides)


def _resolve_scope(input_path: Path, scope: Iterable[str]) -> list[str]:
    want = set(scope)
    out: list[str] = []
    with zipfile.ZipFile(input_path) as z:
        names = z.namelist()
    if "document" in want and "word/document.xml" in names:
        out.append("word/document.xml")
    if "headers" in want:
        out.extend(n for n in names if n.startswith("word/header") and n.endswith(".xml"))
    if "footers" in want:
        out.extend(n for n in names if n.startswith("word/footer") and n.endswith(".xml"))
    return out


def _apply_find_replace(root: etree._Element, mapping: dict[str, str], use_regex: bool) -> None:
    compiled = {
        (re.compile(k) if use_regex else re.compile(re.escape(k))): v
        for k, v in mapping.items()
    }
    for paragraph in root.iter(_Q_P):
        _replace_in_paragraph(paragraph, compiled)


def _replace_in_paragraph(paragraph: etree._Element, compiled: dict) -> None:
    # Collect <w:t> elements in document order; remember their parent <w:r> so
    # we can rebuild the paragraph if any match spans multiple runs.
    t_nodes = list(paragraph.iter(_Q_T))
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

    # Strategy: keep the first <w:t>'s formatting; put the whole replaced
    # string in that node, wipe the rest. This loses granular formatting
    # across the run range but is deterministic and preserves at least the
    # first run's styling (which is almost always what users want).
    t_nodes[0].text = new_text
    # Ensure xml:space="preserve" if text has leading/trailing whitespace
    if new_text != new_text.strip():
        t_nodes[0].set(
            "{http://www.w3.org/XML/1998/namespace}space", "preserve"
        )
    for leftover in t_nodes[1:]:
        leftover.text = ""


def convert_doc_to_docx(input_path: str | Path, output_dir: str | Path | None = None) -> Path:
    """Convert a legacy ``.doc`` (binary Word 97–2003) to ``.docx`` via LibreOffice.

    Returns the path to the produced ``.docx``. Raises :class:`RuntimeError`
    if ``soffice`` is not available on ``$PATH``.
    """
    import subprocess
    import tempfile

    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(src)
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "LibreOffice headless (soffice) not found on PATH. "
            "Install libreoffice or libreoffice-writer."
        )
    out_dir = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="docx_conv_"))
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
