# pdf-writer — Rellenado de formularios PDF

Carga este archivo cuando necesites rellenar campos de formulario interactivos dentro
de un PDF existente (AcroForms). La creación de formularios nuevos desde cero es un
tema separado que se aborda brevemente al final.

## Qué es realmente un AcroForm

Un PDF con AcroForm contiene un diccionario especial de campos con nombre
junto al contenido visual. Cada campo tiene:

- Un **nombre** (p. ej. `"applicant_first_name"`)
- Un **tipo** — entrada de texto (`/Tx`), botón / casilla / radio (`/Btn`),
  selección / desplegable (`/Ch`), o firma (`/Sig`)
- Un **valor actual** (opcional)
- Un **flujo de apariencia** que renderiza el valor en la página

Rellenar un formulario consiste en escribir valores en esos campos y regenerar
los flujos de apariencia para que los valores se muestren correctamente al
visualizar o imprimir el PDF.

## Preflight: inspeccionar el formulario

Antes de escribir código de relleno, lista todos los campos del formulario para
saber con qué estás trabajando:

```python
from pypdf import PdfReader

reader = PdfReader("application.pdf")
fields = reader.get_fields() or {}

for name, field in fields.items():
    print(f"{name}")
    print(f"  type     : {field.get('/FT')}")
    print(f"  value    : {field.get('/V')!r}")
    print(f"  default  : {field.get('/DV')!r}")
    print(f"  options  : {field.get('/Opt')}")  # for dropdowns / radios
    print()
```

Tabla de referencia rápida de tipos de campo:

| Valor `/FT` | Significado | Valores aceptados al rellenar |
|---|---|---|
| `/Tx` | Entrada de texto | Cualquier cadena |
| `/Btn` (checkbox) | Casilla de verificación | `"/Yes"` / `"/Off"`, o el valor de exportación exacto |
| `/Btn` (radio) | Grupo de radio | El valor de exportación exacto del botón seleccionado |
| `/Ch` | Desplegable / lista | Una de las cadenas de opción |
| `/Sig` | Firma | Requiere una librería de firma separada |

Para obtener detalles completos (incluidos los valores de exportación de los botones), usa
la CLI `pdftk` cuando esté disponible:

```bash
pdftk application.pdf dump_data_fields > /tmp/field_report.txt
```

Esto te proporciona el tipo, los flags, los valores de exportación y los tooltips de cada campo.

## Rellenar campos de texto con `pypdf`

El caso básico — un formulario con solo entradas de texto:

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("application.pdf")
writer = PdfWriter(clone_from=reader)

values = {
    "applicant_first_name": "Ana",
    "applicant_last_name":  "García",
    "applicant_dni":        "12345678X",
    "applicant_email":      "ana.garcia@example.com",
    "submission_date":      "2026-04-20",
}

for page in writer.pages:
    writer.update_page_form_field_values(page, values)

with open("/tmp/application_filled.pdf", "wb") as f:
    writer.write(f)
```

### ¿Por qué `clone_from=reader`?

La clonación copia las anotaciones, fuentes y objetos estructurales del origen
al writer. Sin ella, los valores rellenados a menudo no se renderizan correctamente
porque se pierden los recursos de apariencia del formulario.

### ¿Por qué iterar sobre las páginas?

Los campos de formulario pueden estar distribuidos en varias páginas. La llamada
de actualización debe tocar cada página que contenga un campo referenciado en `values`.
Iterar todas las páginas es el comportamiento seguro por defecto.

## Casillas de verificación

Las casillas de verificación son campos `/Btn`. Los valores aceptados dependen de cómo
fue creado el formulario. La mayoría acepta `/Yes` o `/Off`, pero algunos usan
valores de exportación personalizados como `/On`, `/1`, o `/Checked`.

```python
# Caso más común
values = {
    "agrees_to_terms":         "/Yes",
    "subscribes_to_newsletter": "/Off",
}

for page in writer.pages:
    writer.update_page_form_field_values(page, values)
```

Para descubrir el valor de exportación correcto, inspecciona el campo:

```python
fields = reader.get_fields() or {}
checkbox = fields.get("agrees_to_terms", {})
print(checkbox.get("/_States_"))  # pypdf exposes the valid states
```

O usa `pdftk dump_data_fields` y busca las líneas `FieldStateOption`.

## Botones de radio

Un grupo de radio es un único campo lógico con múltiples botones visuales.
Para seleccionar un botón, escribe el nombre del grupo y el valor de exportación
del botón elegido:

```python
# El campo es "shipping_method"; los botones exportan como "/Standard",
# "/Express", "/Overnight"
values = {
    "shipping_method": "/Express",
}
```

## Desplegables y listas

Escribe el valor mostrado de la opción elegida:

```python
fields = reader.get_fields() or {}
dropdown = fields["country"]
print(dropdown.get("/Opt"))   # discover available options

values = {"country": "Spain"}
```

Algunos formularios usan `/Opt` como una lista de pares `[export_value, display_value]`
— en ese caso escribe el valor de exportación, no el valor mostrado.

## Asegurar que los valores rellenados sean visibles

Por defecto, algunos visores de PDF muestran los valores solo cuando se hace clic
interactivamente en el formulario. Para insertar los valores en el contenido visual
de modo que todos los visores los muestren, establece el flag `NeedAppearances`:

```python
from pypdf.generic import BooleanObject, NameObject

# After cloning and before writing:
if "/AcroForm" in writer._root_object:
    writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
```

Esto indica al visor que regenere los flujos de apariencia al abrir el documento.
Es el enfoque más fiable entre distintos visores.

## Aplanar un formulario (hacer los valores permanentes)

Tras rellenar, normalmente querrás **aplanar** el formulario para que:

- Los valores pasen a formar parte del contenido de la página (ya no editables)
- El resultado se muestre de forma idéntica en todos los visores
- El archivo sea más pequeño y sencillo

### Aplanar con `pypdf`

```python
from pypdf import PdfReader, PdfWriter

writer = PdfWriter(clone_from=PdfReader("/tmp/application_filled.pdf"))

# Flatten the entire form
writer.remove_annotations(subtypes=["/Widget"])
# Also remove the AcroForm root so no residual form data remains
if "/AcroForm" in writer._root_object:
    del writer._root_object["/AcroForm"]

with open("/tmp/application_flattened.pdf", "wb") as f:
    writer.write(f)
```

### Aplanar con `pdftk` (más fiable)

```bash
pdftk application_filled.pdf output application_flattened.pdf flatten
```

`pdftk` gestiona casos extremos (campos rotados, firmas estampadas) que el
aplanado en Python puro puede pasar por alto. Cuando la calidad del aplanado
importa, prefiere `pdftk`.

### Aplanar con Ghostscript (el más pesado, el más completo)

```bash
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
   -dNOPAUSE -dBATCH \
   -sOutputFile=application_flattened.pdf application_filled.pdf
```

Esto re-renderiza el PDF completo y siempre produce un archivo aplanado.

## Rellenar PDFs con `pdf-lib` (cuando no puedes usar Python)

Para entornos JavaScript / Node.js:

```javascript
import { PDFDocument } from 'pdf-lib';
import fs from 'fs/promises';

const bytes = await fs.readFile('application.pdf');
const pdf = await PDFDocument.load(bytes);
const form = pdf.getForm();

form.getTextField('applicant_first_name').setText('Ana');
form.getTextField('applicant_last_name').setText('García');
form.getCheckBox('agrees_to_terms').check();
form.getDropdown('country').select('Spain');

form.flatten();  // optional — bakes values into the page

const out = await pdf.save();
await fs.writeFile('application_filled.pdf', out);
```

Útil cuando el paso de relleno vive dentro de un servicio web y quieres
evitar una dependencia de Python.

## Relleno masivo de una plantilla con muchos registros

Un caso de uso clásico: misma plantilla, N filas de datos, N archivos de salida.

```python
import csv
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject

TEMPLATE = Path("contract_template.pdf")
OUT_DIR  = Path("/tmp/contracts")
OUT_DIR.mkdir(exist_ok=True)

def fill_one(record, out_path):
    reader = PdfReader(TEMPLATE)
    writer = PdfWriter(clone_from=reader)

    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)

    for page in writer.pages:
        writer.update_page_form_field_values(page, record)

    with open(out_path, "wb") as f:
        writer.write(f)

with open("contracts.csv", newline="") as f:
    for row in csv.DictReader(f):
        fill_one(row, OUT_DIR / f"contract_{row['id']}.pdf")
```

Para miles de registros, paraleliza con `ProcessPoolExecutor` (véase
`REFERENCE.md`, sección de generación por lotes).

## Crear un AcroForm desde cero (brevemente)

Si necesitas producir un formulario *nuevo* (no rellenar uno existente),
reportlab tiene primitivas para ello:

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

c = canvas.Canvas("/tmp/new_form.pdf", pagesize=A4)
form = c.acroForm

# Text field
c.drawString(50, 700, "Full name:")
form.textfield(
    name="full_name",
    x=140, y=690, width=300, height=20,
    borderStyle="underlined", borderWidth=1,
    fontName="Helvetica", fontSize=11,
)

# Checkbox
c.drawString(50, 650, "I agree to the terms:")
form.checkbox(
    name="agrees_to_terms",
    x=200, y=648, size=15,
    buttonStyle="check",
    borderColor=(0, 0, 0),
    fillColor=(1, 1, 1),
)

# Dropdown
c.drawString(50, 600, "Country:")
form.choice(
    name="country",
    value="Spain",
    x=140, y=590, width=150, height=22,
    options=[("Spain", "ES"), ("France", "FR"), ("Italy", "IT")],
)

c.save()
```

Para un diseño de formularios serio, considera crearlo visualmente en Adobe Acrobat,
Foxit o Scribus, y luego rellenarlo programáticamente — eso suele ser más rápido
que codificar cada widget a mano.

## Resolución de problemas

**Síntoma: los valores se rellenan pero no se muestran en Acrobat.**
→ Establece `/NeedAppearances` a `True`. Si ya está establecido, aplana con `pdftk`.

**Síntoma: al rellenar una casilla con `"/Off"` se renderiza como marcada.**
→ El valor de exportación del formulario no es `/Yes`. Ejecuta `pdftk dump_data_fields`
para encontrar el valor correcto del estado activo de esa casilla.

**Síntoma: PyPDF lanza `KeyError` al rellenar.**
→ El nombre del campo es incorrecto. Los nombres distinguen mayúsculas y minúsculas
y a menudo contienen puntos o corchetes (`applicant[0].firstName`). Cópialo desde
la salida de la inspección, no lo reescribas a mano.

**Síntoma: el PDF rellenado se ve bien en Acrobat pero aparece en blanco en Preview
o Chrome.**
→ Problema clásico de `/NeedAppearances`. Establece el flag o aplana el documento.

**Síntoma: las fechas aparecen en el formato incorrecto.**
→ La mayoría de los campos de formulario son texto plano; formatea la cadena antes
de rellenar (`"20/04/2026"` vs `"2026-04-20"`). Si el campo tiene JavaScript de
formato asociado, no puedes anularlo desde el exterior — escribe directamente
en el formato esperado.

**Síntoma: el envío del formulario falla o el validador oficial lo rechaza.**
→ Los formularios gubernamentales suelen requerir un orden de campos específico,
una codificación específica o un aplanado con firma digital. Esos casos de uso
pueden necesitar `pyhanko` (para firmas) y un aplanado cuidadoso. Lee la
especificación técnica del organismo correspondiente.
