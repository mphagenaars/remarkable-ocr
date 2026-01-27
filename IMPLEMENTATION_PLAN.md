# Remarkable OCR: .env Configuratie & Production-Ready Plan

## Doel
De .env-configuratie afronden en het project production-ready maken: stabiel, herstartbaar en betrouwbaar zonder GUI-configuratie.

## Huidige Situatie (Geanalyseerd)
- ✅ **FastAPI** app met web GUI configuratie
- ✅ **In-memory config** via `user_configs` dict in `config/app_config.py`
- ✅ **Email polling systeem** met IMAP/SMTP
- ✅ **OCR integratie** met OpenRouter API
- ✅ **dotenv** is actief en `.env` wordt geladen
- ✅ **CONFIG_MODE** (`gui`, `env`, `hybrid`) is aanwezig
- ✅ **ENV auto-config** en optionele auto-start polling
- ✅ **GUI read-only in env-mode**
- ⚠️ **Persistente opslag ontbreekt** (herstart verliest state)
- ⚠️ **Startup validatie logt alleen** (stopt de app niet)
- ⚠️ **Polling/processing state is in-memory** (geen IMAP flagging)

## Strategie
**Incrementeel afronden** zonder breaking changes. Eerst de .env flow formaliseren en documenteren, daarna production-hardening.

---

## MICROSTAP 1: .env File Preparatie (AFGEROND)
**Duur:** 10 minuten  
**Risico:** Zeer laag  
**Doel:** Basis .env ondersteuning zonder functionaliteit te wijzigen

### Taken:
- [x] 1.1 Controleer `python-dotenv` in `requirements.txt`
- [x] 1.2 Test dat `.env.example` correct is
- [x] 1.3 Maak test `.env` file aan
- [x] 1.4 Verificeer dat `load_dotenv()` in `app.py` werkt

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
- [x] `load_dotenv()` laadt .env variabelen
- [x] Bestaande app start nog steeds normaal
- [x] Geen impact op huidige functionaliteit

### Rollback:
```bash
rm .env
```

---

## MICROSTAP 2: .env Defaults in Connection Route (AFGEROND)
**Duur:** 20 minuten  
**Risico:** Laag  
**Doel:** .env waarden als fallback in connection form

### Taken:
- [x] 2.1 Backup maken van `routes/connection_routes.py`
- [x] 2.2 Import `os` in `routes/connection_routes.py`
- [x] 2.3 Wijzig Form defaults om .env te lezen
- [x] 2.4 Test met lege GUI + gevulde .env
- [x] 2.5 Test met gevulde GUI (overschrijft .env)

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
- [x] Form toont .env defaults bij eerste bezoek
- [x] GUI input overschrijft nog steeds .env waarden
- [x] Connection test werkt met .env waarden
- [x] Bestaande workflow ongewijzigd

### Rollback:
```bash
git checkout routes/connection_routes.py
```

---

## MICROSTAP 3: UI Pre-fill met .env Waarden (AFGEROND)
**Duur:** 15 minuten  
**Risico:** Laag  
**Doel:** Browser form velden pre-invullen met .env waarden

### Taken:
- [x] 3.1 Pas `/` route aan om .env waarden door te geven
- [x] 3.2 Modificeer `index.html` template om defaults te tonen
- [x] 3.3 Test pre-fill gedrag

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
- [x] Form velden tonen .env waarden als placeholder
- [x] Gebruiker kan waarden nog steeds overschrijven
- [x] Lege .env → lege velden (geen impact)

### Rollback:
```bash
git checkout app.py templates/index.html
```

---

## MICROSTAP 4: CONFIG_MODE Basis Implementatie (AFGEROND)
**Duur:** 25 minuten  
**Risico:** Medium  
**Doel:** Schakelaar tussen GUI en ENV mode

### Taken:
- [x] 4.1 Voeg CONFIG_MODE lezer toe aan `app_config.py`
- [x] 4.2 Implementeer `is_env_mode()` functie
- [x] 4.3 Test CONFIG_MODE detectie
- [x] 4.4 Nog geen UI wijzigingen (alleen backend)

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
- [x] `CONFIG_MODE=env` wordt correct gedetecteerd
- [x] `CONFIG_MODE=gui` is default
- [x] Geen impact op bestaande functionaliteit

---

## MICROSTAP 5: ENV Mode - Auto Configuration (AFGEROND)
**Duur:** 30 minuten  
**Risico:** Medium  
**Doel:** Automatische configuratie bij ENV mode

### Taken:
- [x] 5.1 Implementeer `load_env_config()` in `app_config.py`
- [x] 5.2 Auto-configureer user_config bij ENV mode
- [x] 5.3 Test ENV mode configuration

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
- [x] ENV mode laadt configuratie automatisch
- [x] Ontbrekende verplichte waarden geven error
- [x] GUI mode blijft ongewijzigd

---

## MICROSTAP 6: Startup Auto-configuration (AFGEROND)
**Duur:** 20 minuten  
**Risico:** Medium  
**Doel:** Automatisch configureren bij app start

### Taken:
- [x] 6.1 Voeg startup event toe aan FastAPI app
- [x] 6.2 Roep auto-configure aan bij start
- [x] 6.3 Test startup behavior

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
- [x] ENV mode configureert automatisch bij startup
- [x] GUI mode start normaal (geen auto-config)
- [x] Error handling werkt voor incomplete .env

---

## MICROSTAP 7: Auto-start Polling (ENV Mode) (AFGEROND)
**Duur:** 25 minuten  
**Risico:** Medium  
**Doel:** Automatisch starten van polling in ENV mode

### Taken:
- [x] 7.1 Implementeer `auto_start_polling()` functie
- [x] 7.2 Integreer in startup event
- [x] 7.3 Test auto-polling gedrag

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
- [x] ENV mode + AUTO_START_POLLING=true start polling automatisch
- [x] GUI mode geen auto-polling
- [x] Error handling voor mislukte auto-start

---

## MICROSTAP 8: GUI Disable in ENV Mode (AFGEROND)
**Duur:** 30 minuten  
**Risico:** Medium  
**Doel:** Configuratie form read-only maken in ENV mode

### Taken:
- [x] 8.1 Pas template aan voor ENV mode detectie
- [x] 8.2 Implementeer readonly form styling
- [x] 8.3 Toon ENV mode indicator

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
- [x] ENV mode toont readonly form
- [x] GUI mode blijft volledig functioneel
- [x] Duidelijke indicator van actieve mode

---

## MICROSTAP 9: Error Handling & Validation (AFGEROND, maar verfijning nodig)
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
- [x] Duidelijke error messages bij startup
- [ ] App start niet met ongeldige ENV config (nog soft-fail)
- [x] GUI mode blijft werken bij ENV errors

---

## MICROSTAP 10: Documentation & Testing (DEELS)
**Duur:** 30 minuten  
**Risico:** Laag  
**Doel:** Documentatie en final testing

### Taken:
- [x] 10.1 Update README.md met .env instructies
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
- Persistente config & state (geen dataverlies bij restart)
- Strict startup validation (fail fast met exit code)
- Betrouwbare polling + IMAP flagging voor processed items
- Retries + backoff voor OCR en SMTP
- Monitoring/metrics/logging geschikt voor productie
- Documentatie + tests + deployment scripts afgerond

---

## AANVULLENDE ACTIELIJST: PRODUCTION-HARDENING

### P0 (moet voor "af")
- [ ] **Persistente opslag** (SQLite/Postgres) voor user config + polling state
- [x] **Fail-fast startup** bij ongeldige ENV (exit code + duidelijke fout)
- [x] **IMAP flagging/labeling** voor verwerkte berichten (i.p.v. in-memory set)
- [x] **Robuuste polling** (scheduler/worker i.p.v. ad-hoc asyncio tasks)

## MICROSTAPPEN P0.1: Persistente opslag (SQLite-first)
**Doel:** Configuratie en polling state overleven herstarten.
**Scope:** Vervang in-memory `user_configs`/`active_handlers` voor persistente opslag van config + processing state. Active handlers blijven runtime‑only.

### Architectuurkeuze (v1)
- **SQLite** als default (geen externe dependency).
- **Opslaglaag** in `config/storage.py` of `core/storage.py` met simpele CRUD.
- **Migratiepad**: later switch naar Postgres viazelfde interface.

### Datamodel (voorstel)
1) `users`  
   - `email` (PK)  
   - `config_json` (JSON)  
   - `status` (string)  
   - `updated_at`  
2) `processed_messages`  
   - `email`  
   - `message_id`  
   - `processed_at`  
   - UNIQUE(`email`, `message_id`)

### MICROSTAP 1: Storage laag opzetten
**Duur:** 45–60 min  
**Risico:** Medium  
**Taken:**
- [x] 1.1 Voeg `config/storage.py` toe met SQLite connect + init schema
- [x] 1.2 CRUD helpers: `get_user_config`, `set_user_config`, `list_users`
- [x] 1.3 CRUD helpers: `is_message_processed`, `mark_message_processed`
- [x] 1.4 Env var `DB_PATH` (default `./data/remarkable.db`)

**Validatie:**
- [x] DB file wordt aangemaakt
- [x] Basis CRUD werkt via kleine local test

### MICROSTAP 2: App-config redirect naar storage
**Duur:** 45 min  
**Risico:** Medium  
**Taken:**
- [x] 2.1 Pas `config/app_config.py` aan om storage helpers te gebruiken
- [x] 2.2 Houd `active_handlers` runtime‑only
- [x] 2.3 Update `get_stats()` zodat gebruikers uit DB komen

**Validatie:**
- [x] GUI config opslaan → herstart → config blijft aanwezig

### MICROSTAP 3: Email handler state persistent maken
**Duur:** 45–60 min  
**Risico:** Medium  
**Taken:**
- [x] 3.1 Gebruik `processed_messages` tabel i.p.v. in‑memory `processed_messages` set
- [x] 3.2 Update `EmailHandler._check_new_emails()` en `_process_email()`
- [ ] 3.3 Voeg fallback toe voor lege DB (no-op)

**Validatie:**
- [ ] Email wordt na herstart niet dubbel verwerkt

### MICROSTAP 4: Datamigratie + compat
**Duur:** 30–45 min  
**Risico:** Laag  
**Taken:**
- [ ] 4.1 Bij startup: indien DB leeg en ENV mode actief → auto‑seed user config
- [ ] 4.2 Legacy in-memory data (indien aanwezig) migreert naar DB

**Validatie:**
- [ ] ENV mode blijft werken zonder GUI‑config

### MICROSTAP 5: Documentatie + test checklist
**Duur:** 30 min  
**Risico:** Laag  
**Taken:**
 - [x] 5.1 README: DB_PATH en data directory
 - [ ] 5.2 Test matrix aanvullen (restart + duplicate processing)
