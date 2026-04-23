# docx-writer — Operaciones estructurales

Snippets copy-paste para operaciones que toman uno o más `.docx`
existentes como entrada y producen un `.docx` nuevo como salida.
Todas están implementadas sobre `zipfile` + `lxml` así que no
necesitas dependencias de compose/merge más allá de la baseline.

Las entradas se abren en solo-lectura. Las salidas se escriben en la
ruta que indiques — los inputs nunca se modifican in-place.

Todos los snippets comparten este preámbulo:

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
    """Copia ``source_zip`` a ``output`` reemplazando entradas de
    ``overrides`` y opcionalmente añadiendo entradas de ``extra`` que
    no estuvieran ya en el origen.
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

## Fusionar

Concatena varios cuerpos DOCX en un único documento. El primer input
se usa como esqueleto (sus estilos, numeración y propiedades por
defecto de sección se preservan); los inputs siguientes aportan sus
párrafos y tablas de cuerpo. Se inserta un salto de página entre
cada documento.

```python
def merge_docx(paths: Sequence[str | Path], output: str | Path) -> Path:
    inputs = [Path(p) for p in paths]
    if not inputs:
        raise ValueError("merge_docx: al menos un input es requerido")
    output_path = Path(output)

    with zipfile.ZipFile(inputs[0]) as z0:
        base_doc = _read_xml(z0, "word/document.xml")
    base_body = base_doc.find("w:body", NS)
    if base_body is None:
        raise RuntimeError("el esqueleto no tiene <w:body>")

    # Las propiedades de sección viven al final del cuerpo. Guárdalas
    # aparte; reasocia solo en el último cuerpo fusionado.
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

        # Salto de página antes del contenido del siguiente documento.
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


# Uso
merge_docx(
    paths=["portada.docx", "cuerpo.docx", "apendice.docx"],
    output="final.docx",
)
```

Caveats:
- Las propiedades finales de sección (tamaño, márgenes, cabeceras /
  pies) se heredan del último input que las declare. Alinea las
  orientaciones antes de fusionar si mezclas vertical y apaisado.
- Las listas numeradas pueden reiniciarse entre documentos porque
  cada fuente tiene definiciones de numeración independientes. Si
  necesitas numeración continua entre partes fusionadas, usa
  `docxcompose` en su lugar.
- Las imágenes embebidas dentro de documentos posteriores se
  preservan porque viven bajo `word/media/` con nombres que en la
  práctica son disjuntos; si generaste los inputs tú mismo los IDs
  son estables.

---

## Dividir

Divide un DOCX en varios DOCX más pequeños por un marcador.
Estrategias soportadas:

- `by="heading-level"` con `level=N` — cada párrafo con estilo
  `Heading N` inicia una nueva parte.
- `by="page-break"` — cada salto de página explícito
  (`<w:br w:type="page"/>`) inicia una nueva parte.

Cada parte producida hereda los estilos, numeración y propiedades
finales de sección del esqueleto. El contenido antes del primer
marcador se convierte en la primera parte.

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
        raise RuntimeError("input no tiene <w:body>")

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
        raise ValueError(f"estrategia de split desconocida: {by}")

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


# Uso
parts = split_docx(
    path="informe_largo.docx",
    output_dir="partes/",
    by="heading-level",
    level=1,
    stem="capitulo",
)
```

---

## Buscar-reemplazar

Buscar-reemplazar literal o regex dentro de `word/document.xml`,
`word/header*.xml`, `word/footer*.xml`. El reemplazo preserva el
formato del primer run que participa en cada coincidencia; los runs
íntegramente dentro del rango se vacían.

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

    # Preserva el formato del primer run; vierte el string reemplazado
    # completo en él y vacía el resto. Pierde formato granular a lo
    # largo del rango pero es determinista.
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


# Uso literal
find_replace_docx(
    path="borrador.docx", output="final.docx",
    mapping={"30 días": "60 días", "Juan Pérez": "Ana García"},
)

# Uso regex
find_replace_docx(
    path="fuente.docx", output="redactado.docx",
    mapping={r"[A-Z]{2}-\d{3,5}": "[REDACTADO]"},
    use_regex=True,
)

# Control de scope — solo el cuerpo, saltar cabeceras y pies
find_replace_docx(
    path="in.docx", output="out.docx",
    mapping={"FY2025": "FY2026"},
    scope=["document"],
)
```

Caveats:
- El texto repartido entre múltiples runs (por ejemplo una palabra
  que el editor reformateó parcialmente) se casa correctamente porque
  todos los nodos `<w:t>` de un párrafo se unen antes de buscar.
- El formato inline rico que varía a lo largo del rango coincidente
  se colapsa al formato del primer run. Para reemplazos quirúrgicos
  en prosa fuertemente formateada, trabaja a nivel XML tú mismo — el
  snippet arriba es un punto de partida legible.

---

## Convertir `.doc` heredado a `.docx`

Los archivos Word 97–2003 binarios no son `.docx`. Conviértelos
primero y luego aplica cualquiera de las operaciones anteriores.

```python
def convert_doc_to_docx(input_path, output_dir=None) -> Path:
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(src)
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "LibreOffice headless (soffice) no encontrado en PATH. "
            "Instala libreoffice o libreoffice-writer."
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
        raise RuntimeError(f"LibreOffice no produjo salida para {src}")
    return produced


# Uso
new_path = convert_doc_to_docx("politica_heredada.doc",
                               output_dir="/tmp/convertidos/")
```

Equivalente CLI:

```bash
soffice --headless --convert-to docx politica_heredada.doc --outdir /tmp/convertidos
```

---

## Preview visual

Renderiza el DOCX a PNGs por página para inspección de layout. Útil
tras un merge / split / replace para confirmar que nada se rompió
visualmente. El snippet vive en `REFERENCE.md` §Pipeline de
validación visual.

```bash
soffice --headless --convert-to pdf --outdir /tmp/preview final.docx
pdftoppm -r 150 -png /tmp/preview/final.pdf /tmp/preview/page
```

---

## Content controls (plantillas de formulario de Word)

Rellenar content controls `<w:sdt>` en plantillas DOCX no es parte de
la superficie por defecto de esta skill. El snippet de inspección
read-only vive en `REFERENCE.md` §Content controls. Para escritura,
recorre `document.xml` buscando elementos `<w:sdt>` y reescribe sus
cuerpos `<w:sdtContent>` preservando el binding `<w:sdtPr>`.
