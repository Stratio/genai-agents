#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

echo "=== BI/BA Analytics Agent - Environment Setup ==="

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

# Verify Python runtime dependencies
echo ""
echo "=== Dependency Check ==="
python3 -c "import weasyprint; print('weasyprint: OK')" 2>/dev/null || {
    echo "WARNING: weasyprint failed to import — missing Cairo/Pango libs."
    echo "  Debian/Ubuntu: sudo apt install libcairo2 libpango-1.0-0 libpangoft2-1.0-0"
    echo "  macOS:         brew install cairo pango"
}
python3 -c "import reportlab, pypdf, pdfplumber, pypdfium2, pdf2image, svglib, PIL; print('pdf-reader/pdf-writer python stack: OK')" 2>/dev/null || echo "WARNING: pdf-reader/pdf-writer python libs not fully installed — rerun pip install -r requirements.txt"

# System binaries required by pdf-reader / pdf-writer / ocrmypdf
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
from importlib.metadata import version, PackageNotFoundError
def _v(pkg):
    try:
        return version(pkg)
    except PackageNotFoundError:
        return 'n/a'
print(f'pandas:       {_v(\"pandas\")}')
print(f'numpy:        {_v(\"numpy\")}')
print(f'scipy:        {_v(\"scipy\")}')
print(f'matplotlib:   {_v(\"matplotlib\")}')
print(f'seaborn:      {_v(\"seaborn\")}')
print(f'plotly:       {_v(\"plotly\")}')
print(f'scikit-learn: {_v(\"scikit-learn\")}')
print(f'jinja2:       {_v(\"Jinja2\")}')
print(f'nbformat:     {_v(\"nbformat\")}')
print(f'nbclient:     {_v(\"nbclient\")}')
print(f'openpyxl:     {_v(\"openpyxl\")}')
print(f'tabulate:     {_v(\"tabulate\")}')
print(f'python-pptx:  {_v(\"python-pptx\")}')
print(f'python-docx:  {_v(\"python-docx\")}')
print(f'reportlab:    {_v(\"reportlab\")}')
print(f'pypdf:        {_v(\"pypdf\")}')
print(f'pdfplumber:   {_v(\"pdfplumber\")}')
print(f'pypdfium2:    {_v(\"pypdfium2\")}')
print(f'pdf2image:    {_v(\"pdf2image\")}')
print(f'svglib:       {_v(\"svglib\")}')
print(f'pillow:       {_v(\"pillow\")}')
" || true

echo ""
echo "=== Environment ready ==="
echo "Activate with: source $VENV_DIR/bin/activate"
