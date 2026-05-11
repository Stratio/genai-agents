# pdf-reader

Shared skill that extracts text, tables, forms, metadata, images and OCR'd content from user-provided PDF files. Used by agents that need to ingest PDF inputs as part of an analysis, a quality assessment, or a governance workflow.

Designed as a three-phase flow: quick mode (structural diagnosis), deep mode (per-tool deterministic extraction), and OCR mode (for scanned or image-only PDFs). The skill chooses the phase based on what the PDF actually contains, never up-front.

The companion skill `pdf-writer` covers ad-hoc PDF authoring and structural operations (merge, split, watermark, encrypt, forms).

## What it does

- Structural diagnosis (encryption, corruption, page layout, text-layer presence)
- Text extraction (multi-engine fallback: `pypdf`, `pdfplumber`, `pdfminer.six`, `pypdfium2`)
- Table extraction with layout preservation (`pdfplumber`)
- Form-field inspection and dump (`pdftk` CLI)
- Image extraction and rasterization (`pdf2image` + Poppler)
- OCR for scanned PDFs (`pytesseract`, `ocrmypdf` with Tesseract)
- Last-resort repair of corrupted PDFs (`ghostscript`)

## Python dependencies

- `pypdf>=5.0`
- `pdfplumber>=0.11`
- `pdfminer.six>=20250000`
- `pypdfium2>=5.0`
- `pdf2image>=1.17` (requires `poppler-utils`)
- `pytesseract>=0.3.10` (requires `tesseract-ocr`)
- `ocrmypdf>=17.0` (requires `ghostscript` + `tesseract-ocr` + `poppler-utils`)

Digital-signature inspection uses `pyhanko` on demand (`pip install pyhanko`); it is intentionally not part of the baseline so the sandbox image stays lean.

## System dependencies (apt)

- `poppler-utils` — `pdfinfo`, `pdftotext`, `pdftoppm`, `pdfimages`, `pdfdetach`, `pdffonts`
- `qpdf` — structural operations, repair of corrupted PDFs
- `pdftk-java` — form-field inspection via `pdftk dump_data_fields`
- `tesseract-ocr` + `tesseract-ocr-eng` + `tesseract-ocr-spa` — OCR engine and language data
- `ghostscript` — last-resort PDF repair and rasterization fallback

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section for install commands.

## Shared guides

None.

## MCPs

None — the skill operates purely on user-provided PDF files.
