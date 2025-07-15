# Installatie Documentatie - Remarkable OCR

## Overzicht
Deze documentatie beschrijft hoe je de Remarkable OCR app installeert, vooral in LXC containers waar vaak dependency problemen optreden.

## System Requirements
- Python 3.8 of hoger
- pip (Python package manager)
- System packages voor cryptography

## Installatie in LXC Container

### Stap 1: System Dependencies
```bash
# Update package lijst
sudo apt update

# Installeer Python en benodigde development tools
sudo apt install python3 python3-pip python3-venv -y

# Installeer system packages voor cryptography (belangrijk!)
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

### Stap 2: Python Environment
```bash
# Ga naar project directory
cd /path/to/remarkable

# Maak virtual environment (sterk aanbevolen)
python3 -m venv venv
source venv/bin/activate

# Upgrade pip en tools
pip install --upgrade pip setuptools wheel
```

### Stap 3: Dependencies Installeren

**Optie A: Normale installatie**
```bash
# Installeer dependencies uit requirements.txt
pip install -r requirements.txt
```

**Optie B: Minimale installatie (bij dependency problemen)**
```bash
# Installeer alleen essentiële dependencies
pip install -r requirements-minimal.txt
```

**Optie C: Handmatige installatie (laatste redmiddel)**
```bash
# Installeer packages één voor één
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install httpx==0.24.1
pip install jinja2==3.1.2
pip install python-multipart==0.0.6
pip install python-dotenv==1.0.0

# Optioneel (alleen als security features nodig zijn):
# pip install --only-binary=cryptography cryptography
```

## Quick Fix voor LXC Container Problemen

**Als je steeds dependency errors krijgt, probeer deze volgorde:**

```bash
# 1. Maak schone environment
cd /home/matthijs/remarkable
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade tools eerst
pip install --upgrade pip setuptools wheel

# 3. Installeer minimaal (ZONDER cryptography)
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install jinja2==3.1.2
pip install python-multipart==0.0.6
pip install httpx==0.24.1
pip install python-dotenv==1.0.0

# 4. Test of het werkt
python3 -c "import fastapi; print('FastAPI OK')"
python3 app.py
```

**Als je nog steeds `ModuleNotFoundError` krijgt:**
```bash
# Controleer virtual environment
echo $VIRTUAL_ENV  # Should show /home/matthijs/remarkable/venv

# Controleer pip locatie
which pip  # Should show venv/bin/pip

# Controleer installed packages
pip list | grep -E "(fastapi|uvicorn|httpx)"
```

### Cryptography Build Errors
Als je errors krijgt bij het installeren van `cryptography`:

```bash
# Installeer extra system dependencies
sudo apt install pkg-config libssl-dev libffi-dev

# Installeer cryptography expliciet met legacy build
pip install cryptography==41.0.8 --use-deprecated=legacy-resolver
```

### HTTPX SSL Errors
Als je SSL certificaat errors krijgt:

```bash
# Installeer CA certificates
sudo apt install ca-certificates

# Update certificate store
sudo update-ca-certificates
```

### Memory Issues in LXC
Voor kleine LXC containers (<512MB RAM):

```bash
# Installeer packages één voor één
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install httpx==0.25.2
# etc...
```

### FastAPI Import Errors
Als je `ModuleNotFoundError: No module named 'fastapi'` krijgt:

```bash
# Controleer of virtual environment actief is
source venv/bin/activate

# Controleer geïnstalleerde packages
pip list | grep fastapi

# Herinstalleer FastAPI expliciet
pip install --force-reinstall fastapi==0.104.1

# Test import
python3 -c "import fastapi; print('FastAPI OK')"
```

### Virtual Environment Issues (MEEST VOORKOMEND)
```bash
# Symptoom: ModuleNotFoundError ondanks installatie
# Oorzaak: Verkeerde Python interpreter of venv niet actief

# Fix 1: Controleer venv status
source venv/bin/activate
echo "Virtual env: $VIRTUAL_ENV"

# Fix 2: Als venv corrupt is - hermaak
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Fix 3: Installeer packages direct in venv
./venv/bin/pip install fastapi==0.104.1
./venv/bin/python app.py
```

### System vs Virtual Environment Conflict
```bash
# Probleem: Packages geïnstalleerd in system Python ipv venv
# Oplossing: Forceer venv gebruik

# Check waar packages zijn geïnstalleerd
pip show fastapi | grep Location

# Moet zijn: /home/matthijs/remarkable/venv/lib/python3.x/site-packages
# Als het /usr/lib/python3 toont, dan is venv niet actief!

# Fix:
source venv/bin/activate
pip install --force-reinstall fastapi==0.104.1
```

## Configuratie

### Environment Variables
Maak een `.env` bestand aan:

```bash
# OpenRouter API configuratie
OPENROUTER_API_KEY=your_api_key_here
OCR_MODEL=google/gemini-2.5-flash

# App configuratie
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Test de Installatie
```bash
# Start de app
python3 app.py

# Test API endpoint
curl http://localhost:8000/health
```

## Veelvoorkomende Problemen

### "No module named ..." errors
- Controleer of virtual environment geactiveerd is
- Installeer ontbrekende packages: `pip install <package>`

### Port binding errors
- Controleer of port 8000 vrij is: `netstat -tulpn | grep 8000`
- Gebruik andere port: `python3 app.py --port 8080`

### Permission errors
- Controleer file permissions: `ls -la`
- Run niet als root tenzij noodzakelijk

## Development Setup

Voor development environment:

```bash
# Installeer extra development tools
pip install pytest pytest-asyncio

# Run tests
python -m pytest test_*.py
```

## Diagnose Checklist

**Stap 1: Python Environment Check**
```bash
which python3        # Expected: /usr/bin/python3
python3 --version    # Expected: Python 3.8+
which pip           # Expected: /home/matthijs/remarkable/venv/bin/pip
echo $VIRTUAL_ENV   # Expected: /home/matthijs/remarkable/venv
```

**Stap 2: Package Installation Check**
```bash
pip list | grep fastapi     # Should show fastapi version
pip show fastapi           # Should show installation details
python3 -c "import sys; print(sys.path)"  # Check Python path
```

**Stap 3: Common LXC Container Issues**
```bash
# Check available disk space
df -h

# Check available memory
free -h

# Check if system packages are installed
dpkg -l | grep -E "(python3-dev|build-essential|libssl-dev)"
```

## Troubleshooting
