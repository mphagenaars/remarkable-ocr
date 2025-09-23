# Remarkable OCR: .env Configuratie Implementatieplan

## Doel
Configuratie via .env files toevoegen aan de bestaande FastAPI email-OCR applicatie, zodat de app automatisch kan opstarten in LXC containers zonder GUI configuratie.

## Huidige Situatie (Geanalyseerd)
- ✅ **FastAPI** app met web GUI configuratie
- ✅ **In-memory config** via `user_configs` dict in `config/app_config.py`
- ✅ **Email polling systeem** met IMAP/SMTP
- ✅ **OCR integratie** met OpenRouter API
- ✅ **dotenv** al geïmporteerd in `app.py`
- ❌ **Geen .env ondersteuning** voor automatische configuratie

## Strategie
**Incrementele uitbreiding** van het bestaande systeem zonder breaking changes. Elke stap is testbaar en kan terug worden gedraaid.

---

## MICROSTAP 1: .env File Preparatie
**Duur:** 10 minuten  
**Risico:** Zeer laag  
**Doel:** Basis .env ondersteuning zonder functionaliteit te wijzigen

### Taken:
- [ ] 1.1 Controleer `python-dotenv` in `requirements.txt` ✅ (al aanwezig)
- [ ] 1.2 Test dat `.env.example` correct is
- [ ] 1.3 Maak test `.env` file aan
- [ ] 1.4 Verificeer dat `load_dotenv()` in `app.py` werkt

### Test:
```bash
# Maak test .env
cp .env.example .env
echo "TEST_VAR=hello" >> .env

# Test in Python
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f'TEST_VAR: {os.getenv(\"TEST_VAR\", \"not found\")}')
"
```

### Validatie:
- [ ] `load_dotenv()` laadt .env variabelen
- [ ] Bestaande app start nog steeds normaal
- [ ] Geen impact op huidige functionaliteit

### Rollback:
```bash
rm .env
```

---

## MICROSTAP 2: .env Defaults in Connection Route
**Duur:** 20 minuten  
**Risico:** Laag  
**Doel:** .env waarden als fallback in connection form

### Taken:
- [ ] 2.1 Backup maken van `routes/connection_routes.py`
- [ ] 2.2 Import `os` in connection_routes.py
- [ ] 2.3 Wijzig Form defaults om .env te lezen
- [ ] 2.4 Test met lege GUI + gevulde .env
- [ ] 2.5 Test met gevulde GUI (overschrijft .env)

### Code wijziging:
```python
# In routes/connection_routes.py
@router.post("/test-connection")
async def test_connection(
    email: str = Form(os.getenv("EMAIL", "")),
    password: str = Form(os.getenv("EMAIL_PASSWORD", "")),
    imap_server: str = Form(os.getenv("IMAP_SERVER", "imap.gmail.com")),
    imap_port: int = Form(int(os.getenv("IMAP_PORT", "993"))),
    smtp_server: str = Form(os.getenv("SMTP_SERVER", "smtp.gmail.com")),
    smtp_port: int = Form(int(os.getenv("SMTP_PORT", "587"))),
    allowed_senders: str = Form(os.getenv("ALLOWED_SENDERS", "")),
    openrouter_api_key: str = Form(os.getenv("OPENROUTER_API_KEY", "")),
    notification_email: str = Form(os.getenv("NOTIFICATION_EMAIL", ""))
):
```

### Test scenario's:
1. **Lege GUI + .env gevuld** → Gebruikt .env waarden
2. **GUI gevuld + .env gevuld** → GUI overschrijft .env
3. **Leeg alles** → Gebruikt hardcoded defaults

### Validatie:
- [ ] Form toont .env defaults bij eerste bezoek
- [ ] GUI input overschrijft nog steeds .env waarden
- [ ] Connection test werkt met .env waarden
- [ ] Bestaande workflow ongewijzigd

### Rollback:
```bash
git checkout routes/connection_routes.py
```

---

## MICROSTAP 3: UI Pre-fill met .env Waarden
**Duur:** 15 minuten  
**Risico:** Laag  
**Doel:** Browser form velden pre-invullen met .env waarden

### Taken:
- [ ] 3.1 Pas `/` route aan om .env waarden door te geven
- [ ] 3.2 Modificeer `index.html` template om defaults te tonen
- [ ] 3.3 Test pre-fill gedrag

### Code wijziging:
```python
# In app.py
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Hoofdpagina met email configuratie formulier"""
    env_defaults = {
        "email": os.getenv("EMAIL", ""),
        "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
        "imap_port": os.getenv("IMAP_PORT", "993"),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": os.getenv("SMTP_PORT", "587"),
        "allowed_senders": os.getenv("ALLOWED_SENDERS", ""),
        "notification_email": os.getenv("NOTIFICATION_EMAIL", "")
    }
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "defaults": env_defaults
    })
```

### Template wijziging:
```html
<!-- In templates/index.html -->
<input type="email" id="email" name="email" 
       value="{{ defaults.email }}" required>
```

### Test:
1. Vul .env met test waarden
2. Open browser naar `http://localhost:8000`
3. Controleer dat form velden pre-gevuld zijn

### Validatie:
- [ ] Form velden tonen .env waarden als placeholder
- [ ] Gebruiker kan waarden nog steeds overschrijven
- [ ] Lege .env → lege velden (geen impact)

### Rollback:
```bash
git checkout app.py templates/index.html
```

---

## MICROSTAP 4: CONFIG_MODE Basis Implementatie
**Duur:** 25 minuten  
**Risico:** Medium  
**Doel:** Schakelaar tussen GUI en ENV mode

### Taken:
- [ ] 4.1 Voeg CONFIG_MODE lezer toe aan `app_config.py`
- [ ] 4.2 Implementeer `is_env_mode()` functie
- [ ] 4.3 Test CONFIG_MODE detectie
- [ ] 4.4 Nog geen UI wijzigingen (alleen backend)

### Code wijziging:
```python
# In config/app_config.py
import os

def get_config_mode() -> str:
    """Get configuration mode from environment"""
    return os.getenv("CONFIG_MODE", "gui").lower()

def is_env_mode() -> bool:
    """Check if running in env-only mode"""
    return get_config_mode() == "env"

def is_hybrid_mode() -> bool:
    """Check if running in hybrid mode"""
    return get_config_mode() == "hybrid"

def is_gui_mode() -> bool:
    """Check if running in GUI mode"""
    return get_config_mode() == "gui"
```

### Test:
```python
# Test script
from config.app_config import get_config_mode, is_env_mode

# Test verschillende modes
os.environ["CONFIG_MODE"] = "env"
assert is_env_mode() == True
print("ENV mode: OK")

os.environ["CONFIG_MODE"] = "gui"  
assert is_env_mode() == False
print("GUI mode: OK")
```

### Validatie:
- [ ] `CONFIG_MODE=env` wordt correct gedetecteerd
- [ ] `CONFIG_MODE=gui` is default
- [ ] Geen impact op bestaande functionaliteit

---

## MICROSTAP 5: ENV Mode - Auto Configuration
**Duur:** 30 minuten  
**Risico:** Medium  
**Doel:** Automatische configuratie bij ENV mode

### Taken:
- [ ] 5.1 Implementeer `load_env_config()` in app_config.py
- [ ] 5.2 Auto-configureer user_config bij ENV mode
- [ ] 5.3 Test ENV mode configuration

### Code wijziging:
```python
# In config/app_config.py
def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    if not is_env_mode():
        return {}
    
    # Verplichte velden check
    email = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD") 
    allowed_senders = os.getenv("ALLOWED_SENDERS")
    
    if not all([email, password, allowed_senders]):
        raise ValueError("ENV mode requires EMAIL, EMAIL_PASSWORD, and ALLOWED_SENDERS")
    
    return {
        "email": email,
        "password": password,
        "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
        "imap_port": int(os.getenv("IMAP_PORT", "993")),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "allowed_senders": [s.strip() for s in allowed_senders.split(",")],
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "notification_email": os.getenv("NOTIFICATION_EMAIL"),
        "status": "env_configured"
    }

def auto_configure_env_user():
    """Auto-configure user from ENV if in env mode"""
    if is_env_mode():
        try:
            env_config = load_env_config()
            set_user_config(env_config["email"], env_config)
            print(f"Auto-configured user: {env_config['email']}")
        except ValueError as e:
            print(f"ENV configuration error: {e}")
```

### Test met .env:
```bash
CONFIG_MODE=env
EMAIL=test@example.com
EMAIL_PASSWORD=password123
ALLOWED_SENDERS=sender@remarkable.com
OPENROUTER_API_KEY=sk-test-123
```

### Validatie:
- [ ] ENV mode laadt configuratie automatisch
- [ ] Ontbrekende verplichte waarden geven error
- [ ] GUI mode blijft ongewijzigd

---

## MICROSTAP 6: Startup Auto-configuration
**Duur:** 20 minuten  
**Risico:** Medium  
**Doel:** Automatisch configureren bij app start

### Taken:
- [ ] 6.1 Voeg startup event toe aan FastAPI app
- [ ] 6.2 Roep auto-configure aan bij start
- [ ] 6.3 Test startup behavior

### Code wijziging:
```python
# In app.py
from config.app_config import auto_configure_env_user

@app.on_event("startup")
async def startup_event():
    """Configure application on startup"""
    auto_configure_env_user()
    logger.info("Application startup complete")
```

### Test:
1. Set CONFIG_MODE=env in .env
2. Start app: `python app.py`
3. Check logs voor auto-configuration

### Validatie:
- [ ] ENV mode configureert automatisch bij startup
- [ ] GUI mode start normaal (geen auto-config)
- [ ] Error handling werkt voor incomplete .env

---

## MICROSTAP 7: Auto-start Polling (ENV Mode)
**Duur:** 25 minuten  
**Risico:** Medium  
**Doel:** Automatisch starten van polling in ENV mode

### Taken:
- [ ] 7.1 Implementeer `auto_start_polling()` functie
- [ ] 7.2 Integreer in startup event
- [ ] 7.3 Test auto-polling gedrag

### Code wijziging:
```python
# In config/app_config.py
async def auto_start_polling():
    """Auto-start polling if configured in ENV mode"""
    if not is_env_mode():
        return
        
    if not os.getenv("AUTO_START_POLLING", "false").lower() == "true":
        return
        
    email = os.getenv("EMAIL")
    if not email or not is_user_configured(email):
        logger.warning("Cannot auto-start polling: user not configured")
        return
        
    # Start polling via existing route logic
    from routes.polling_routes import start_polling_internal
    try:
        await start_polling_internal(email)
        logger.info(f"Auto-started polling for {email}")
    except Exception as e:
        logger.error(f"Auto-start polling failed: {e}")

# In app.py startup event
@app.on_event("startup") 
async def startup_event():
    """Configure application on startup"""
    auto_configure_env_user()
    await auto_start_polling()
    logger.info("Application startup complete")
```

### Test:
```bash
# .env
CONFIG_MODE=env
AUTO_START_POLLING=true
EMAIL=test@example.com
# ... andere vereiste variabelen
```

### Validatie:
- [ ] ENV mode + AUTO_START_POLLING=true start polling automatisch
- [ ] GUI mode geen auto-polling
- [ ] Error handling voor mislukte auto-start

---

## MICROSTAP 8: GUI Disable in ENV Mode
**Duur:** 30 minuten  
**Risico:** Medium  
**Doel:** Configuratie form read-only maken in ENV mode

### Taken:
- [ ] 8.1 Pas template aan voor ENV mode detectie
- [ ] 8.2 Implementeer readonly form styling
- [ ] 8.3 Toon ENV mode indicator

### Code wijziging:
```python
# In app.py index route
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Hoofdpagina met email configuratie formulier"""
    from config.app_config import get_config_mode, is_env_mode
    
    env_defaults = {
        "email": os.getenv("EMAIL", ""),
        # ... andere defaults
    }
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "defaults": env_defaults,
        "config_mode": get_config_mode(),
        "is_env_mode": is_env_mode()
    })
```

### Template wijziging:
```html
<!-- In templates/index.html -->
{% if is_env_mode %}
<div class="alert alert-info">
    🔒 Configuratie modus: ENV - Instellingen zijn alleen-lezen
</div>
{% endif %}

<input type="email" id="email" name="email" 
       value="{{ defaults.email }}" 
       {% if is_env_mode %}readonly{% endif %} required>
```

### Validatie:
- [ ] ENV mode toont readonly form
- [ ] GUI mode blijft volledig functioneel
- [ ] Duidelijke indicator van actieve mode

---

## MICROSTAP 9: Error Handling & Validation
**Duur:** 20 minuten  
**Risico:** Laag  
**Doel:** Robuuste error handling voor ENV mode

### Taken:
- [ ] 9.1 Implementeer ENV validatie functie
- [ ] 9.2 Voeg startup error handling toe
- [ ] 9.3 Test error scenarios

### Code wijziging:
```python
# In config/app_config.py
def validate_env_config() -> tuple[bool, str]:
    """Validate environment configuration"""
    required_vars = ["EMAIL", "EMAIL_PASSWORD", "ALLOWED_SENDERS"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        return False, f"Missing required variables: {', '.join(missing)}"
    
    # Validate email format
    email = os.getenv("EMAIL")
    if "@" not in email:
        return False, f"Invalid email format: {email}"
    
    # Validate allowed senders
    senders = os.getenv("ALLOWED_SENDERS")
    if not any("@" in s for s in senders.split(",")):
        return False, "ALLOWED_SENDERS must contain valid email addresses"
    
    return True, "Configuration valid"
```

### Test error scenarios:
1. Missing EMAIL
2. Invalid email format  
3. Empty ALLOWED_SENDERS
4. Invalid CONFIG_MODE

### Validatie:
- [ ] Duidelijke error messages bij startup
- [ ] App start niet met ongeldige ENV config
- [ ] GUI mode blijft werken bij ENV errors

---

## MICROSTAP 10: Documentation & Testing
**Duur:** 30 minuten  
**Risico:** Laag  
**Doel:** Documentatie en final testing

### Taken:
- [ ] 10.1 Update README.md met .env instructies
- [ ] 10.2 Test alle scenarios end-to-end
- [ ] 10.3 Test LXC container deployment
- [ ] 10.4 Performance check

### Test matrix:
| CONFIG_MODE | GUI Werking | Auto-start | .env Required |
|-------------|-------------|------------|---------------|
| gui (default) | ✅ Volledig | ❌ Nee | ❌ Optioneel |
| env | 🔒 Readonly | ✅ Ja | ✅ Verplicht |
| hybrid | ✅ + defaults | ⚡ Configureerbaar | ⚡ Gedeeltelijk |

### LXC test scenario:
```bash
# Complete container restart test
1. Stop applicatie
2. Herstart LXC container  
3. Start applicatie
4. Verify: Auto-configuration + polling works
5. Send test email with PDF
6. Verify: OCR processing + notification
```

### Validatie:
- [ ] Alle modes werken correct
- [ ] LXC restart scenario succesvol
- [ ] Performance impact minimaal
- [ ] Documentatie compleet

---

## ROLLBACK STRATEGIE

Bij elke stap:
```bash
# Backup maken
git add -A && git commit -m "Backup before step X"

# Rollback bij problemen
git reset --hard HEAD~1
```

## SUCCESS CRITERIA

✅ **MVP Success:**
- CONFIG_MODE=env werkt volledig automatisch
- GUI mode blijft 100% functioneel  
- LXC container restart → werkende app
- Geen performance degradatie

✅ **Production Ready:**
- Error handling robuust
- Logging informatief
- Documentatie compleet
- Alle edge cases getest

## TIJDSINSCHATTING

**Totaal: ~4-5 uur**
- Microstappen 1-3: 45 minuten (low risk)
- Microstappen 4-6: 75 minuten (medium risk)  
- Microstappen 7-9: 75 minuten (medium risk)
- Microstap 10: 30 minuten (testing)
- Buffer: 30 minuten

**Per sessie: 1-2 microstappen** voor beheersbaarheid en testing.