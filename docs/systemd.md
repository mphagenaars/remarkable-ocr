# Systemd Service Troubleshooting

## Doel
Automatische start van remarkable-ocr tool als systemd service bij LXC container boot.

## Probleem
Service krijgt consistent `status=203/EXEC` fout - systemd kan het ExecStart commando niet uitvoeren.

## Chronologie van pogingen

### Poging 1: Statisch service bestand
**Aanpak:** Hardcoded `remarkable-ocr.service` bestand
```
ExecStart=/home/matthijs/remarkable/venv/bin/python app.py
```
**Probleem:** Hardcoded user paths - werkt niet voor andere gebruikers

### Poging 2: Dynamische service generatie
**Aanpak:** Service file genereren tijdens installatie met variabelen
```bash
CURRENT_USER=$(whoami)
WORKING_DIR="$CURRENT_HOME/remarkable"
ExecStart=$WORKING_DIR/venv/bin/python $WORKING_DIR/app.py
```
**Probleem:** Nog steeds status=203/EXEC

### Poging 3: Uvicorn string import fix
**Aanpak:** app.py wijzigen van `app` object naar `"app:app"` string
**Reden:** uvicorn reload mode vereist import string
**Probleem:** Nog steeds service failures

### Poging 4: Direct uvicorn aanroep
**Aanpak:** Service roept uvicorn direct aan ipv python app.py
```
ExecStart=$WORKING_DIR/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
```
**Probleem:** Nog steeds status=203/EXEC

### Poging 5: Virtual environment path mismatch
**Root cause gevonden:** 
- Lokaal gebruikt `.venv` (met punt)
- Installer maakte `venv` (zonder punt)  
- Service zocht naar niet-bestaand pad

**Fix:** Installer aangepast naar `.venv`
```bash
python3 -m venv .venv
ExecStart=$WORKING_DIR/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
```
**Probleem:** Nog steeds failures

### Poging 6: Simpele python aanroep
**Aanpak:** Terug naar eenvoudige `python app.py` met fixed app.py
```python
uvicorn.run("app:app", reload=False)  # Voor service compatibility
```
**Probleem:** Nog steeds status=203/EXEC

## Root causes geïdentificeerd

### 1. Virtual environment mismatch
- **Probleem:** Inconsistentie tussen lokale setup (`.venv`) en installer (`venv`)
- **Impact:** Service kon uvicorn/python executable niet vinden
- **Status:** Opgelost

### 2. Uvicorn reload mode incompatibiliteit  
- **Probleem:** `reload=True` vereist import string, niet app object
- **Impact:** App crashte bij direct object gebruik
- **Status:** Opgelost

### 3. Onbekende systemd issue
- **Probleem:** Ondanks correcte paths blijft status=203/EXEC
- **Mogelijke oorzaken:**
  - Systemd security restricties (`ProtectSystem=strict`)
  - Permission issues met virtual environment
  - Missing environment variables
  - Working directory toegang
- **Status:** Onopgelost

## Lessons learned

### ✅ Wat werkte
- Dynamische service file generatie
- Virtual environment path consistency
- Proper error diagnostics workflow

### ❌ Wat niet werkte
- Complexe systemd security configuratie
- Uvicorn direct via service
- Meerdere iteratieve fixes zonder grondige diagnose

### 🔍 Diagnose approach
- **Goed:** Stap-voor-stap path verificatie
- **Slecht:** Te veel assumptions, niet genoeg logging

## Alternatieve aanpakken voor toekomst

### 1. Minimale systemd service
```ini
[Unit]
Description=Remarkable OCR Service
After=network.target

[Service]
Type=simple
User=remarkable
WorkingDirectory=/opt/remarkable-ocr
ExecStart=/opt/remarkable-ocr/.venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Docker container
- Elimineer systemd complexiteit
- Consistent environment
- Betere isolatie

### 3. Manual startup script
- Simpele `start.sh` script
- Cron job voor auto-start
- Minder systemd dependencies

### 4. Process manager (supervisor)
- Alternatief voor systemd
- Betere process management
- Eenvoudigere configuratie

## Conclusie
Status=203/EXEC blijft onopgelost ondanks correcte pad configuratie. Voor productie gebruik: overweeg alternatieve deployment methoden.

**Aanbeveling:** Manual start of Docker deployment voor betrouwbaarheid.
