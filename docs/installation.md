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
```bash
# Installeer dependencies uit requirements.txt
pip install -r requirements.txt
```

## Troubleshooting

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
