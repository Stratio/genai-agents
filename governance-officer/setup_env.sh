#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

echo "=== Governance Officer Agent - Environment Setup ==="

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created at $VENV_DIR"
else
    echo "Virtual environment already exists at $VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Install/update dependencies
echo "Installing dependencies from requirements.txt..."
pip install --quiet --upgrade pip
pip install --quiet -r "$REQ_FILE"

# Verify PDF-related python and system deps
python3 -c "import reportlab, pypdf, pdfplumber, pypdfium2, pdf2image, svglib, PIL; print('pdf-reader/pdf-writer python stack: OK')" 2>/dev/null || echo "WARNING: pdf-reader/pdf-writer python libs not fully installed — rerun pip install -r requirements.txt"

missing_bin=()
for bin in qpdf pdftk tesseract pdfinfo gs; do
    command -v "$bin" >/dev/null 2>&1 || missing_bin+=("$bin")
done
if [ "${#missing_bin[@]}" -gt 0 ]; then
    echo "WARNING: missing system tools for PDF skills: ${missing_bin[*]}"
    echo "  Debian/Ubuntu: sudo apt install poppler-utils qpdf pdftk tesseract-ocr tesseract-ocr-spa ghostscript"
    echo "  macOS:         brew install poppler qpdf pdftk-java tesseract tesseract-lang ghostscript"
else
    echo "pdf system tools (qpdf, pdftk, tesseract, pdfinfo, gs): OK"
fi

# Report versions
echo ""
echo "=== Installed Versions ==="
python3 -c "
import weasyprint, docx, jinja2, markdown
import reportlab, pypdf, pdfplumber, pypdfium2, pdf2image, svglib, PIL
print(f'weasyprint:    {weasyprint.__version__}')
print(f'python-docx:   {docx.__version__}')
print(f'Jinja2:        {jinja2.__version__}')
print(f'markdown:      {markdown.__version__}')
print(f'reportlab:     {reportlab.__version__}')
print(f'pypdf:         {pypdf.__version__}')
print(f'pdfplumber:    {pdfplumber.__version__}')
print(f'pypdfium2:     {pypdfium2.__version__}')
print(f'pdf2image:     {pdf2image.__version__}')
print(f'svglib:        {svglib.__version__ if hasattr(svglib, \"__version__\") else \"n/a\"}')
print(f'pillow:        {PIL.__version__}')
"

echo ""
echo "=== Environment ready ==="
echo "Activate with: source $VENV_DIR/bin/activate"
