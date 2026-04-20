# pdf-writer — PDF Form Filling

Load this file when you need to fill interactive form fields inside an
existing PDF (AcroForms). Creating new forms from scratch is a separate
topic, briefly covered at the end.

## What an AcroForm actually is

An AcroForm-enabled PDF contains a special dictionary of named fields
alongside the visual content. Each field has:

- A **name** (e.g. `"applicant_first_name"`)
- A **type** — text input (`/Tx`), button / checkbox / radio (`/Btn`),
  choice / dropdown (`/Ch`), or signature (`/Sig`)
- A **current value** (optional)
- An **appearance stream** that renders the value into the page

Filling a form means writing values into those fields and regenerating
the appearance streams so the values actually show up when the PDF is
viewed or printed.

## Preflight: inspect the form

Before writing filling code, list every field in the form so you know
what you're dealing with:

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

Field type cheat sheet:

| `/FT` value | Meaning | Accepted values when filling |
|---|---|---|
| `/Tx` | Text input | Any string |
| `/Btn` (checkbox) | Checkbox | `"/Yes"` / `"/Off"`, or the exact export value |
| `/Btn` (radio) | Radio group | The exact export value of the chosen button |
| `/Ch` | Dropdown / list | One of the option strings |
| `/Sig` | Signature | Needs a separate signing library |

For comprehensive details (including export values of buttons), use the
`pdftk` CLI when available:

```bash
pdftk application.pdf dump_data_fields > /tmp/field_report.txt
```

This gives you every field's type, flags, export values, and tooltips.

## Filling text fields with `pypdf`

The basic case — a form with text inputs only:

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

### Why `clone_from=reader`?

Cloning copies the source's annotations, fonts, and structural objects
into the writer. Without it, filled values often don't render correctly
because the form's appearance resources are lost.

### Why loop over pages?

Form fields can be scattered across multiple pages. The update call
needs to touch every page that holds a field referenced in `values`.
Iterating all pages is the safe default.

## Checkboxes

Checkboxes are `/Btn` fields. The accepted values depend on how the
form was authored. Most forms accept `/Yes` or `/Off`, but some use
custom export values like `/On`, `/1`, or `/Checked`.

```python
# Most common case
values = {
    "agrees_to_terms":         "/Yes",
    "subscribes_to_newsletter": "/Off",
}

for page in writer.pages:
    writer.update_page_form_field_values(page, values)
```

To discover the correct export value, inspect the field:

```python
fields = reader.get_fields() or {}
checkbox = fields.get("agrees_to_terms", {})
print(checkbox.get("/_States_"))  # pypdf exposes the valid states
```

Or use `pdftk dump_data_fields` and look at the `FieldStateOption`
lines.

## Radio buttons

A radio group is a single logical field with multiple visual buttons.
To select a button, write the group's name and the chosen button's
export value:

```python
# The field is "shipping_method"; buttons export as "/Standard",
# "/Express", "/Overnight"
values = {
    "shipping_method": "/Express",
}
```

## Dropdowns and list boxes

Write the chosen option's display value:

```python
fields = reader.get_fields() or {}
dropdown = fields["country"]
print(dropdown.get("/Opt"))   # discover available options

values = {"country": "Spain"}
```

Some forms use `/Opt` as a list of `[export_value, display_value]`
pairs — in that case write the export value, not the display one.

## Ensuring filled values are visible

By default, some PDF viewers show the values only when the form is
interactively clicked. To bake values into the visual content so every
viewer shows them, set the `NeedAppearances` flag:

```python
from pypdf.generic import BooleanObject, NameObject

# After cloning and before writing:
if "/AcroForm" in writer._root_object:
    writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
```

This tells the viewer to regenerate appearance streams when opening.
It's the most reliable cross-viewer approach.

## Flattening a form (making values permanent)

After filling, you usually want to **flatten** the form so:

- The values become part of the page content (not editable anymore)
- The result displays identically in every viewer
- The file is smaller and simpler

### Flattening with `pypdf`

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

### Flattening with `pdftk` (more reliable)

```bash
pdftk application_filled.pdf output application_flattened.pdf flatten
```

`pdftk` handles edge cases (rotated fields, stamped signatures) that
pure-Python flattening can miss. When flattening quality matters, prefer
`pdftk`.

### Flattening with Ghostscript (heaviest, most thorough)

```bash
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
   -dNOPAUSE -dBATCH \
   -sOutputFile=application_flattened.pdf application_filled.pdf
```

This re-renders the entire PDF and always produces a flat file.

## Filling fillable PDFs with `pdf-lib` (when you can't use Python)

For JavaScript / Node.js environments:

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

Useful when the filling step lives inside a web service and you want
to avoid a Python dependency.

## Batch-filling a template with many records

A classic use case: same template, N rows of data, N output files.

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

For thousands of records, parallelize with `ProcessPoolExecutor` (see
`REFERENCE.md`, batch generation section).

## Creating an AcroForm from scratch (briefly)

If you need to produce a *new* form (not fill an existing one),
reportlab has primitives:

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

For serious form design, consider authoring visually in Adobe Acrobat,
Foxit, or Scribus, and then filling programmatically — that's usually
faster than coding every widget by hand.

## Troubleshooting

**Symptom: values fill but don't display in Acrobat.**
→ Set `/NeedAppearances` to `True`. If already set, flatten with `pdftk`.

**Symptom: filling a checkbox writes `"/Off"` but it renders as ticked.**
→ The form's export value isn't `/Yes`. Run `pdftk dump_data_fields`
to find the correct on-state value for that checkbox.

**Symptom: PyPDF raises `KeyError` when filling.**
→ The field name is wrong. Names are case-sensitive and often contain
dots or brackets (`applicant[0].firstName`). Copy-paste from the
inspection output, don't retype.

**Symptom: the filled PDF looks fine in Acrobat but is blank in Preview
or Chrome.**
→ Classic `/NeedAppearances` issue. Set the flag, or flatten.

**Symptom: dates appear in the wrong format.**
→ Most form fields are plain text; format the string before filling
(`"20/04/2026"` vs `"2026-04-20"`). If the field has JavaScript
formatting attached, you can't override it from the outside — just
write in the expected format.

**Symptom: form submission fails or the government validator rejects it.**
→ Government forms often require specific field order, specific
encoding, or digitally signed flattening. Those use cases may need
`pyhanko` (for signatures) and careful flattening. Read the agency's
technical specification.
