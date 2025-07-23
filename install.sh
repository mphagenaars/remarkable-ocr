#!/bin/bash
# Remarkable OCR - Auto-installer voor LXC containers
# Gebruik: bash install.sh

set -e  # Exit on any error

echo "🚀 Remarkable OCR - LXC Container Installer"
echo "============================================"

# Check if running in correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Niet in de juiste directory. Ga naar /home/matthijs/remarkable"
    exit 1
fi

echo "📦 Stap 1: System dependencies installeren..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv build-essential

echo "🐍 Stap 2: Python virtual environment maken..."
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

echo "⬆️ Stap 3: Pip upgraden..."
pip install --upgrade pip setuptools wheel

echo "📚 Stap 4: Python packages installeren..."
pip install -r requirements.txt

echo "✅ Stap 5: Installatie testen..."
python3 -c "import fastapi; print('FastAPI: OK')"
python3 -c "import uvicorn; print('Uvicorn: OK')"
python3 -c "import httpx; print('HTTPX: OK')"

echo ""
echo "🎉 Installatie succesvol!"
echo ""
echo "Volgende stappen:"
echo "1. source .venv/bin/activate"
echo "2. python3 app.py"
echo "3. Open http://localhost:8000"
echo ""
echo "Bij problemen: zie docs/installation.md"
