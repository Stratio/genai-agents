# xlsx-writer

Shared skill that creates Excel workbooks (`.xlsx`) with intentional structure, and performs structural operations on existing ones. Covers three audiences: (1) analytical workbooks driven by `/analyze` (cover/KPI + parameters + detail + appendix), (2) quality-coverage workbooks driven by `quality-report` (multi-sheet audit structure per `quality-report-layout.md §6.6`), and (3) ad-hoc workbooks invoked directly by the user (tabular exports, catalogs, quantitative models, reference tables).

The companion skill `xlsx-reader` covers ingestion of XLSX inputs.

## What it does

- Design-first XLSX authoring via `openpyxl` (no builder class): KPI bands, native Table objects, conditional formatting, freeze panes, column widths, print area and page setup
- Taxonomy of 6 workbook categories (cover/KPI analytical, pivot, coverage matrix, tabular export, catalog, quantitative model) as starting points — not enum-constrained
- Theming via generic "centralized theming skill" reference: palette, typography, sizes are fed from a theme token bundle; falls back to `visual-craftsmanship.md` when no theme is available
- Structural operations on existing XLSX files: merge hoja-a-hoja preserving styles, split per sheet, find-replace in cell text, extract a sheet to CSV, convert legacy binary `.xls` to `.xlsx`
- Formula refresh helper (`scripts/refresh_formulas.py`) that forces a headless LibreOffice recalc pass so cached values are written for viewers that do not auto-recalculate
- Post-build validation pipeline (structural sanity + formula refresh + visual PDF export) for pre-delivery inspection

## Python dependencies

- `openpyxl>=3.1`
- `pandas>=2.0` — optional, used by some structural-op snippets for bulk reshapes
- `pillow>=11.0` — image embedding and size inspection when the workbook includes logos or figures

All already part of the baseline `requirements.txt` of the Python agents that load this skill.

## System dependencies (apt)

- `libreoffice` (or `libreoffice-calc`) — legacy `.xls` → `.xlsx` conversion, formula refresh pass, visual preview rendering. Without it, authoring still works; only legacy conversion, formula refresh and PDF preview are disabled.
- `poppler-utils` — `pdftoppm` rasterises the visual preview PDF to per-page PNGs. Already part of `pdf-reader`'s system deps.

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section.

## Companion skills

- `xlsx-reader` — the ingestion counterpart (cell values / tables / formulas / images / metadata). Shares the `openpyxl` + `pandas` stack.
- `quality-report` — the skill that drives the "Excel" output format, materialising the multi-sheet coverage workbook described in `quality-report-layout.md §6.6`.

## MCPs

None — the skill operates purely on local files.

## Shared guides

- `visual-craftsmanship.md` (via `skill-guides`) — tonal palette roles and typography pairings used as fallback when no centralized theming skill resolved a theme.

## Bundled assets

- `assets/blank.xlsx` — empty workbook with one unstyled sheet, used as a minimal scaffold when the skill needs to bootstrap a file from nothing rather than building from `openpyxl.Workbook()`.
