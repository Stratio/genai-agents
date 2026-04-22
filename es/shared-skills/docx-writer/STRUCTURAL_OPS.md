# docx-writer — Operaciones estructurales

Operaciones que toman uno o más `.docx` existentes como entrada y producen un `.docx` nuevo como salida. Las tres están implementadas en `scripts/structural_ops.py`, usando solo `zipfile` + `lxml` para que la skill no añada dependencias transitivas más allá de la línea base.

Las entradas se abren en solo-lectura. Las salidas se escriben en la ruta que indiques.

## Fusionar (merge)

Concatena los cuerpos de varios DOCX en un único documento. La primera entrada se usa como esqueleto (sus estilos, numeración y propiedades por defecto de sección se preservan); las entradas posteriores aportan sus párrafos y tablas. Se inserta un salto de página entre cada documento.

```python
import sys
sys.path.insert(0, "shared-skills/docx-writer/scripts")

from structural_ops import merge_docx

merge_docx(
    paths=["portada.docx", "cuerpo.docx", "anexo.docx"],
    output="final.docx",
)
```

Notas:
- Las propiedades finales de sección (tamaño de página, márgenes, cabeceras / pies) se heredan de la última entrada que las declare. Alinea orientaciones antes de fusionar si mezclas retrato / apaisado.
- Las listas numeradas pueden reiniciarse entre documentos porque los ficheros fuente tienen definiciones de numeración independientes. Fusionar secuencias avanzadas con continuidad total exige `docxcompose`; añádelo a requirements si te toca ese caso.
- Las imágenes embebidas en documentos posteriores se preservan (viven en `word/media/` con nombres únicos que ya son disjuntos entre ficheros en la práctica; si produces las entradas con `DOCXBuilder`, los IDs son estables).

## Dividir (split)

Parte un DOCX en varios más pequeños según un marcador.

```python
from structural_ops import split_docx

partes = split_docx(
    path="informe_largo.docx",
    output_dir="partes/",
    by="heading-level",
    level=1,
    stem="capitulo",
)
# partes == [Path("partes/capitulo-01.docx"), Path("partes/capitulo-02.docx"), ...]
```

Estrategias soportadas:

- `by="heading-level"` con `level=N` — cada párrafo con estilo `Heading N` inicia una parte nueva.
- `by="page-break"` — cada salto de página explícito (`<w:br w:type="page"/>`) inicia una parte nueva.

Cada parte hereda los estilos, numeración y propiedades finales de sección del esqueleto. El contenido previo al primer marcador se convierte en la primera parte (útil cuando la fuente empieza con un preámbulo).

## Buscar y reemplazar

Find-replace literal o con expresiones regulares sobre `word/document.xml`, `word/header*.xml`, `word/footer*.xml`. El reemplazo preserva el formato del primer run participante en cada match; los runs enteramente dentro del rango del match se vacían.

```python
from structural_ops import find_replace_docx

find_replace_docx(
    path="borrador.docx",
    output="final.docx",
    mapping={
        "30 días": "60 días",
        "Juan Pérez": "Ana García",
    },
)
```

Modo regex:

```python
find_replace_docx(
    path="fuente.docx",
    output="redactado.docx",
    mapping={r"[A-Z]{2}-\d{3,5}": "[REDACTADO]"},
    use_regex=True,
)
```

Control de ámbito — limitar al cuerpo principal o incluir cabeceras / pies:

```python
find_replace_docx(
    path="in.docx", output="out.docx",
    mapping={"FY2025": "FY2026"},
    scope=["document", "headers", "footers"],  # valor por defecto
)
```

Cautelas:
- El texto partido entre varios runs (por ejemplo una palabra que el editor reformateó parcialmente) se detecta correctamente porque todos los nodos `<w:t>` de un párrafo se unen antes del match.
- El formato inline rico que varía a lo largo del rango del match se colapsa al formato del primer run. Para reemplazos quirúrgicos dentro de prosa muy formateada, trabaja directamente a nivel XML — `python-docx` da los ganchos.

## Convertir `.doc` heredado a `.docx`

Los ficheros Word 97–2003 binarios no son `.docx`. Conviértelos antes de aplicar cualquiera de las operaciones anteriores.

```python
from structural_ops import convert_doc_to_docx

nueva_ruta = convert_doc_to_docx("politica_heredada.doc", output_dir="/tmp/convertido/")
```

Exige `libreoffice` / `libreoffice-writer` en `$PATH` (`soffice` debe poder invocarse en modo headless). Lanza `RuntimeError` si no.

Equivalente CLI (uso puntual):

```bash
python3 shared-skills/docx-writer/scripts/convert_doc_to_docx.py politica_heredada.doc --out-dir /tmp/convertido
```

## Previsualización visual (no estrictamente estructural)

Renderiza el DOCX a PNGs por página para inspeccionar el layout. Útil después de un merge / split / replace para confirmar que nada se rompió visualmente:

```bash
python3 shared-skills/docx-writer/scripts/visual_validate.py final.docx \
  --out /tmp/final_preview --dpi 150
# un PNG por página impreso por stdout
```

Pipeline interno: `soffice --convert-to pdf` luego `pdftoppm -png -r <dpi>`. Ambas herramientas del sistema deben estar instaladas; en la imagen del sandbox ya lo están.

## Controles de contenido (plantillas "form" de Word)

Rellenar `<w:sdt>` en plantillas DOCX está fuera del API por defecto — bajo demanda. Si lo necesitas, abre un issue; el camino de implementación es un script dedicado que recorre `document.xml` buscando elementos `<w:sdt>` y reescribe sus cuerpos `<w:sdtContent>` preservando el `<w:sdtPr>` de enlace.
