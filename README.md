# 📝 Remarkable 2 naar Tekst Converter

Automatische conversie van handgeschreven Remarkable 2 notities naar doorzoekbare tekst via e-mail workflow.

## 🎯 Project Doel

Deze tool monitort een e-mailbox op PDF/PNG bijlagen van Remarkable 2 notities, voert OCR uit via OpenRouter API, en stuurt de geëxtraheerde tekst terug voor archivering en doorzoekbaarheid.

## ✨ Features

### ✅ Werkend (v0.1.0)
- **Email monitoring:** Automatische IMAP polling voor nieuwe berichten
- **Sender whitelist:** Alleen emails van toegestane afzenders
- **Attachment filtering:** PDF/PNG detectie en extractie
- **UI configuratie:** Web interface voor email setup
- **Real-time status:** Live polling controls en feedback

### 🚧 In ontwikkeling  
- **OCR processing:** Nederlandse tekst extractie via Google Gemini 2.5 Flash
- **Response workflow:** Geautomatiseerde terugkoppeling met geëxtraheerde tekst
- **Multi-user support:** Admin interface voor gebruikersbeheer
- **Privacy-first:** Lokale verwerking, veilige credential opslag

## 🚀 Quick Start

### Vereisten
- Python 3.12+
- E-mail account met IMAP/SMTP toegang
- OpenRouter API key

### Installatie
```bash
git clone https://github.com/mphagenaars/remarkable-ocr.git
cd remarkable-ocr
pip install -r requirements.txt
cp .env.example .env
# Bewerk .env met je configuratie
python app.py
```

**⚠️ LXC Container Users:** Bekijk [`docs/installation.md`](docs/installation.md) voor gedetailleerde installatie-instructies en troubleshooting.

Open `http://localhost:8000` in je browser.

## 📋 MVP Status

- [x] **Stap 0:** UI-stub & connectiviteit test
- [x] **Stap 1:** Mailbox polling
- [ ] **Stap 2:** OCR integratie
- [ ] **Stap 3:** Response workflow
- [ ] **Stap 4:** Database & persistence
- [ ] **Stap 5:** Multi-user & admin UI

## 🏗️ Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLite
- **Frontend:** HTML, vanilla JavaScript
- **OCR:** OpenRouter API (Google Gemini 2.5 Flash)
- **Email:** IMAP/SMTP (stdlib)

## 📁 Project Structuur

```
remarkable/
├── app.py                # FastAPI main application
├── core/                 # Core business logic
├── api/                  # API endpoints
├── templates/           # Jinja2 HTML templates
├── static/             # CSS/JS assets
├── tests/              # Unit tests
└── docs/               # Feature documentation
```

## 🔐 Security

- Email credentials: AES-256 encryptie
- User passwords: bcrypt hashing
- Temp files: Automatische cleanup
- Rate limiting: Bescherming tegen misbruik

## 📖 Documentatie

- [Implementation Plan](plan.md) - Volledige ontwikkelstrategie
- [Project Rules](.rules) - Development guardrails
- [API Documentation](docs/api.md) - API reference (TBD)

## 🤝 Contributing

Dit is een persoonlijk project, maar suggesties zijn welkom via issues.

## 📄 License

MIT License - zie [LICENSE](LICENSE) file.

---

**Status:** 🚧 In ontwikkeling - MVP fase
