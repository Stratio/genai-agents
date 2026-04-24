# xlsx-reader

Shared skill that extracts cell values, tables, formulas, images, metadata and sheet structure from user-provided Excel workbooks (`.xlsx`, `.xlsm`, and legacy `.xls` via LibreOffice conversion). Used by agents that need to ingest spreadsheet inputs as part of an analysis, a governance workflow, or when reading specifications in tabular form.

Designed as a two-phase flow: quick mode (single-shot extraction with a multi-engine fallback chain) and deep mode (per-engine deterministic extraction with diagnostics first). The skill picks the phase based on what the workbook actually contains, never up-front.

## What it does

- Structural diagnosis (part inventory via `unzip -l`, sheet listing with visibility state, defined names inventory)
- Cell and table extraction with multi-engine fallback: `openpyxl` (read-only) → `pandas` (openpyxl backend) → raw-XML walk over `zipfile`
- Formula inspection (`data_only=False`) and cached-value inspection (`data_only=True`) as two distinct passes
- Column-selective and row-capped reading for large datasets (`usecols`, `nrows`, `--max-rows`)
- Image extraction (ZIP walk into `xl/media/*`)
- Core and extended metadata (author, title, created/modified dates, defined names, active sheet, sheet visibility)
- Legacy `.xls` → `.xlsx` conversion (`soffice --headless --convert-to xlsx`)
- `.xlsb` → `.xlsx` conversion via the same LibreOffice pass
- CSV/TSV fallback when the "Excel file" a user attached is actually plain text

## Python dependencies

- `openpyxl>=3.1`
- `pandas>=2.0` (uses openpyxl as the XLSX engine)
- `lxml` (transitive from openpyxl)

Optional:

- `xlrd<2` — read-only legacy `.xls` support when LibreOffice is unavailable

All dependencies listed above are already part of the baseline `requirements.txt` of the Python agents that load this skill.

## System dependencies (apt)

- `libreoffice` (or `libreoffice-calc`) — legacy `.xls` and `.xlsb` conversion. Only needed when the input is a pre-2007 binary `.xls` or a `.xlsb` binary 2007+.

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section for install commands.

## Graceful degradation

The skill works with just `openpyxl` + `pandas` + `lxml` for modern `.xlsx` and `.xlsm`. LibreOffice unlocks legacy `.xls` and `.xlsb`. Without LibreOffice and without `xlrd<2`, legacy binaries cannot be opened — the skill reports a clear diagnostic instead of silently failing.
