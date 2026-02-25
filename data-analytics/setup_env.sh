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

# Verify weasyprint system dependencies
echo ""
echo "=== Dependency Check ==="
python3 -c "import weasyprint; print('weasyprint: OK')" 2>/dev/null || echo "WARNING: weasyprint may need system dependencies (cairo, pango). Install with: sudo apt-get install libcairo2-dev libpango1.0-dev"

# Report versions
echo ""
echo "=== Installed Versions ==="
python3 -c "
import pandas, numpy, scipy, matplotlib, seaborn, plotly
import sklearn, jinja2, nbformat, nbclient, openpyxl, tabulate, pptx, docx
print(f'pandas:       {pandas.__version__}')
print(f'numpy:        {numpy.__version__}')
print(f'scipy:        {scipy.__version__}')
print(f'matplotlib:   {matplotlib.__version__}')
print(f'seaborn:      {seaborn.__version__}')
print(f'plotly:       {plotly.__version__}')
print(f'scikit-learn: {sklearn.__version__}')
print(f'jinja2:       {jinja2.__version__}')
print(f'nbformat:     {nbformat.__version__}')
print(f'nbclient:     {nbclient.__version__}')
print(f'openpyxl:     {openpyxl.__version__}')
print(f'tabulate:     {tabulate.__version__}')
print(f'python-pptx:  {pptx.__version__}')
print(f'python-docx:  {docx.__version__}')
"

echo ""
echo "=== Environment ready ==="
echo "Activate with: source $VENV_DIR/bin/activate"
