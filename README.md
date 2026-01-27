# 📝 Remarkable 2 naar Tekst Converter

Automatische conversie van handgeschreven Remarkable 2 notities naar doorzoekbare tekst via een e-mail workflow.

## 🎯 Project Doel

Deze tool monitort een e-mailbox op PDF/PNG bijlagen van Remarkable 2 notities, voert OCR uit via een AI-model (zoals die beschikbaar zijn via OpenRouter), en stuurt de geëxtraheerde tekst terug voor archivering en doorzoekbaarheid.

## ✨ Features

-   **Flexibele Configuratie:**
    -   **GUI-modus:** Eenvoudige webinterface voor snelle setup.
    -   **Headless/ENV-modus:** Volledig te configureren via `.env` bestand voor gebruik in servers en containers.
    -   **Hybride-modus:** Vooraf ingevulde GUI met waarden uit `.env`, maar nog steeds aanpasbaar.
-   **Email Monitoring:** Automatische IMAP polling voor nieuwe berichten.
-   **Sender Whitelist:** Verwerkt alleen e-mails van toegestane afzenders.
-   **Attachment Filtering:** Detecteert en extraheert automatisch PDF- en PNG-bestanden.
-   **Real-time Status:** Live polling controls en feedback in de webinterface.
-   **OCR Integratie (Optioneel):** Extraheert tekst uit afbeeldingen via OpenRouter API.

## 🚀 Quick Start

### Vereisten
-   Python 3.10+
-   Een e-mailaccount met IMAP/SMTP toegang (een app-specifiek wachtwoord wordt aanbevolen).
-   (Optioneel) Een OpenRouter API key voor OCR.

### Installatie & Configuratie

1.  **Clone de repository:**
    ```bash
    git clone https://github.com/mphagenaars/remarkable-ocr.git
    cd remarkable-ocr
    ```

2.  **Installeer de dependencies:**
    *   **Aanbevolen (met virtual environment):**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        ```
    *   **Voor LXC containers is er een `install.sh` script.**

3.  **Configureer de applicatie:**
    ```bash
    # Maak een .env bestand aan vanuit het voorbeeld
    cp .env.example .env
    ```
    Open het `.env` bestand en vul de vereiste variabelen in, zoals `EMAIL`, `EMAIL_PASSWORD`, en `ALLOWED_SENDERS`.

4.  **Start de applicatie:**
    ```bash
    python3 app.py
    ```

5.  Open je browser en ga naar `http://localhost:8000`.

## ⚙️ Configuratie Modi

Je kunt de applicatie in verschillende modi draaien door de `CONFIG_MODE` variabele in je `.env` bestand aan te passen:

-   `CONFIG_MODE=gui` (standaard): De applicatie wordt volledig via de webinterface geconfigureerd. Waarden uit `.env` worden gebruikt om de velden vooraf in te vullen.
-   `CONFIG_MODE=env`: De applicatie gebruikt uitsluitend de configuratie uit het `.env` bestand. De webinterface wordt 'read-only' en toont de actieve instellingen. Dit is ideaal voor servers en headless deployments.
-   `CONFIG_MODE=hybrid`: Combineert beide. De GUI is vooraf ingevuld met `.env` waarden, maar je kunt ze via de interface overschrijven.

Voor headless gebruik (`CONFIG_MODE=env`), kun je de e-mail polling automatisch laten starten door `AUTO_START_POLLING=true` in te stellen in je `.env` bestand.


### 💾 Persistente opslag (SQLite)
De app gebruikt nu een SQLite database om configuratie en verwerkte berichten te bewaren tussen restarts.

- **Default pad:** `./data/remarkable.db`
- **Override:** zet `DB_PATH` in je `.env`

Voorbeeld:
```bash
DB_PATH=/var/lib/remarkable/remarkable.db
```

**Let op:** zorg dat de map bestaat of dat de app rechten heeft om deze aan te maken.

## 🏗️ Tech Stack

-   **Backend:** Python 3.12, FastAPI
-   **Frontend:** HTML, vanilla JavaScript
-   **OCR:** OpenRouter API (bijv. Google Gemini, Claude)
-   **Email:** IMAP/SMTP (Python stdlib)

## 📁 Project Structuur

```
remarkable/
├── app.py                # FastAPI hoofapplicatie
├── core/                 # Core business logica (email, ocr, notificaties)
├── routes/               # API endpoints voor de web-interface
├── config/               # Applicatieconfiguratie en state management
├── templates/            # Jinja2 HTML templates
├── static/               # CSS/JS assets
├── .env.example          # Voorbeeld voor configuratie
└── requirements.txt      # Python dependencies
```

## 🔐 Security

-   Gebruik altijd app-specifieke wachtwoorden voor je e-mailaccount.
-   Sla gevoelige informatie zoals API keys en wachtwoorden nooit op in je code; gebruik het `.env` bestand.
-   Zet `.env` permissies op `600` (alleen lees/schrijf voor jezelf): `chmod 600 .env`.

## 📄 License

MIT License - zie [LICENSE](LICENSE) file.

---

**Status:** ✅ Basisfunctionaliteit geïmplementeerd, inclusief headless configuratie.
