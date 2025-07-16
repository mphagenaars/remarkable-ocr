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

echo "📚 Stap 4: Python packages installeren (minimaal)..."
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install jinja2==3.1.2
pip install python-multipart==0.0.6
pip install httpx==0.24.1
pip install python-dotenv==1.0.0

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
