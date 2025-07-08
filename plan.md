# Remarkable 2 naar Tekst Converter - Implementation Plan

## 🎯 Project Overview
**Goal:** Tool voor automatische conversie van handgeschreven Remarkable 2 notities naar doorzoekbare tekst via e-mail workflow.

**Impact Label:** **L** (> 300 regels, volledige architectuur)

## 📋 MVP Backlog (from spec)
Gebaseerd op de UI-first approach uit je specificatie:

### Stap 0: UI-stub & connectiviteit (**M**) ✅
- Minimale webpagina (FastAPI + HTML/JS)
- IMAP/SMTP configuratie formulier
- "Test verbinding" functionaliteit
- **Files:** `app.py`, `templates/index.html`, `requirements.txt`
- **~150 regels**

### Stap 1: Mailbox polling (**M**) ✅
- IMAP monitoring voor nieuwe emails
- Filter op bijlagen (PDF/PNG)
- Basis email parsing
- **Files:** `core/email_handler.py`, `core/models.py`
- **~200 regels**

### Stap 2: OCR integratie (**M**) ✅
- OpenRouter API (google/gemini-2.5-flash)
- PDF/PNG naar tekst conversie
- Nederlandse tekst optimalisatie
- **Files:** `core/ocr_processor.py`
- **~100 regels**

### Stap 3: Response workflow (**S**) ✅
- Email terugsturen met geëxtraheerde tekst
- Originele bijlage behouden
- Template voor response emails
- **Files:** `templates/email_response.py`
- **~80 regels**

### Stap 4: Database & persistence (**M**)
- SQLite setup voor gebruikersconfiguraties
- Wachtwoord encryptie (bcrypt)
- Email credentials veilig opslaan
- **Files:** `core/database.py`, `core/auth.py`
- **~150 regels**

### Stap 5: Multi-user & admin UI (**M**)
- Admin interface voor gebruikersbeheer
- Per-gebruiker configuratie
- Status dashboard
- **Files:** `templates/admin.html`, `api/admin.py`
- **~200 regels**

## 🎉 **MVP Core Complete!**
**Status:** Email → OCR → Response pipeline werkend  
**Datum:** Juli 8, 2025  
**Volgende:** Database & persistence (Stap 4)

### Bereikt:
- ✅ UI-stub met FastAPI
- ✅ Email polling & parsing
- ✅ OCR met Gemini 2.5 Flash
- ✅ Response email workflow

### Stap 4: Database & persistence (**M**) 🚧 NEXT

## 🏗️ Architecture Design

### Project Structure
```
remarkable/
├── .rules                 # Project guardrails
├── plan.md               # Dit document
├── progress.md           # Voortgang logging
├── TODO.txt              # Volgende acties
├── requirements.txt      # Dependencies
├── app.py                # FastAPI main application
├── core/
│   ├── __init__.py
│   ├── email_handler.py  # IMAP/SMTP logica
│   ├── ocr_processor.py  # OpenRouter OCR
│   ├── database.py       # SQLite operations
│   ├── auth.py          # Authenticatie & encryptie
│   └── models.py        # Data models
├── api/
│   ├── __init__.py
│   ├── main.py          # API endpoints
│   └── admin.py         # Admin routes
├── templates/           # Jinja2 HTML
│   ├── base.html
│   ├── index.html
│   └── admin.html
├── static/             # CSS/JS assets
│   ├── style.css
│   └── app.js
├── tests/              # Unit tests
│   ├── test_email.py
│   ├── test_ocr.py
│   └── test_api.py
└── docs/               # Feature documentation
    ├── email.md
    ├── ocr.md
    └── deployment.md
```

### Tech Stack Compliance
- ✅ **Backend:** Python 3.12 + FastAPI
- ✅ **Frontend:** HTML + vanilla JavaScript  
- ✅ **Data:** SQLite (prod-ready database)
- ✅ **Tests:** Python unittest + pytest

## 🔄 Implementation Strategy

### Phase 1: Core Foundation (Stappen 0-2)
**Goal:** Werkende email → OCR → response pipeline
**Duration:** ~3 checkpoints
**Risk:** Medium (nieuwe API integratie)

### Phase 2: Persistence & Security (Stap 4)
**Goal:** Veilige opslag van configuraties
**Duration:** ~2 checkpoints  
**Risk:** Medium (encryptie implementatie)

### Phase 3: Multi-user Features (Stappen 5)
**Goal:** Admin interface en gebruikersbeheer
**Duration:** ~2 checkpoints
**Risk:** Low (UI work)

## 🔐 Security Considerations

### Data Protection
- **Email credentials:** AES-256 encryptie in SQLite
- **User passwords:** bcrypt hashing
- **Temp files:** Auto-cleanup na verwerking
- **API keys:** Environment variables alleen

### Rate Limiting
- **Login attempts:** 5 per 15 minuten
- **Email processing:** 10 emails per minuut
- **OCR API calls:** Respect OpenRouter limits

## 🧪 Testing Strategy

### Unit Tests (per stap)
- **Email handler:** IMAP/SMTP mock tests
- **OCR processor:** API response mocking
- **Database:** SQLite in-memory tests
- **Auth:** Encryption/decryption tests

### Integration Tests
- **End-to-end email workflow**
- **API endpoint testing**
- **UI form submissions**

## 📦 Dependencies

### Core Requirements
```
fastapi==0.104.1
uvicorn==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
sqlite3  # stdlib
imaplib  # stdlib
smtplib  # stdlib
bcrypt==4.1.2
cryptography==41.0.8
httpx==0.25.2  # voor OpenRouter API
```

### Development
```
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
```

## 🚀 Deployment Considerations

### Environment Setup
- **Development:** `.env` file met dev credentials
- **Production:** System environment variables
- **Docker:** Optioneel voor latere iteratie

### Monitoring
- **Health check:** `/health` endpoint
- **Logging:** Structured logging naar file
- **Error tracking:** Console + file output

## 📊 Success Criteria

### MVP Completion
- [ ] Gebruiker kan email configuratie instellen via UI
- [ ] System monitort mailbox automatisch
- [ ] PDF/PNG bijlagen worden correct geOCR'd
- [ ] Geëxtraheerde tekst wordt teruggestuurd via email
- [ ] Configuraties worden veilig opgeslagen
- [ ] Admin kan meerdere gebruikers beheren

### Quality Gates
- [ ] >80% test coverage voor core modules
- [ ] Alle bestanden <300 regels
- [ ] Security review van credential handling
- [ ] Performance test met 10+ emails tegelijk

## 🔄 Checkpoint Strategy

### Per Stap Workflow
1. **Plan review** - implementatie details bespreken
2. **Code implementation** - volgens .rules principes
3. **Testing** - unit tests + manual verification
4. **Documentation** - update progress.md
5. **Review checkpoint** - wacht op feedback

### Risk Mitigation
- **OpenRouter API issues:** Fallback naar lokale OCR
- **Email provider blocking:** Rate limiting + retry logic
- **Storage encryption:** Gebruik proven libraries (cryptography)
- **UI complexity:** Start simpel, itereer op feedback

## 📝 Next Actions (TODO.txt preview)

1. **Review & approve** dit implementatieplan
2. **Stap 0 implementatie:** UI-stub & connectiviteit test
3. **Environment setup:** `.env` template + requirements.txt
4. **Basic project structure:** Directories + `__init__.py` files
5. **First checkpoint:** Test connectivity met dummy email account

---

**Vraag:** Akkoord met deze aanpak? Welke onderdelen wil je aanpassen voor we beginnen met Stap 0?
