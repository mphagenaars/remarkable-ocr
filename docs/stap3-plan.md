# Stap 3: Response Workflow - Implementatieplan

## 🎯 Doel
Implementeren van de resultaatverwerking en notificatie workflow voor het automatisch terugkoppelen van OCR resultaten naar de gebruiker via e-mail.

## 📊 Impact Label
**M** (50-300 regels code, meerdere bestanden)

## 🗂️ Bestanden
- `core/notification_handler.py` - Email notificatie logica
- `templates/email_response.html` - Email template voor OCR resultaten
- `app.py` - API endpoints uitbreiding
- `docs/notification-feature.md` - Documentatie

## 📋 Feature Breakdown

### 1. OCR Resultaatverwerking (30%)
- **Functionaliteit:** Verwerking van ruwe OCR output naar gestructureerd formaat
- **Technische details:**
  - Text clean-up en formattering
  - Metadata extractie (titel, datum, lengte)
  - Error handling voor mislukte OCR pogingen
- **Bestanden:** `core/notification_handler.py`

### 2. Email Notificatie Systeem (40%)
- **Functionaliteit:** Automatisch verzenden van emails met OCR resultaten
- **Technische details:**
  - SMTP client integratie (hergebruik bestaande code)
  - Jinja2 templates voor resultaat emails
  - Optie voor bijlage van originele documenten
  - Error logging en retry mechanisme
- **Bestanden:** `core/notification_handler.py`, `templates/email_response.html`

### 3. API Endpoints (20%)
- **Functionaliteit:** API endpoints voor notificatie configuratie en status
- **Technische details:**
  - Configuratie endpoints voor notificatie instellingen
  - Status endpoint voor verzonden notificaties
  - Integratie met bestaande API structuur
- **Bestanden:** `app.py`

### 4. Gebruikersinterface Aanpassingen (10%)
- **Functionaliteit:** UI updates voor notificatie configuratie
- **Technische details:**
  - Formulier elementen voor notificatie instellingen
  - Status indicators voor verwerkte documenten
  - JavaScript voor async status updates
- **Bestanden:** `templates/index.html`, `static/app.js`

## 🧪 Testing Strategie
- **Unit tests:** Voor email formattering en verzending
- **Integration tests:** End-to-end flow van OCR naar notificatie
- **Edge cases:** Foutafhandeling bij mislukte verzendingen
- **Security tests:** Validatie van email templates tegen XSS

## 🔄 Implementatie Aanpak

### Checkpoint 1: Core Notificatie Handler
- `notification_handler.py` basis implementatie
- Unit tests voor notificatie functies
- Email template structuur

### Checkpoint 2: Email Templates & SMTP Integratie
- Email template implementatie
- SMTP verzending logica
- Error handling & retry mechanisme

### Checkpoint 3: API & UI Integratie
- API endpoints voor configuratie
- UI aanpassingen voor notificatie instellingen
- End-to-end test van OCR naar notificatie

## 💻 Code Voorbeelden

### NotificationHandler Interface
```python
class NotificationHandler:
    """Handles OCR result notifications via email."""
    
    def __init__(self, smtp_config):
        """Initialize with SMTP configuration."""
        self.smtp_config = smtp_config
        
    async def send_ocr_result(self, recipient, ocr_result, original_attachment=None):
        """Send OCR results to recipient."""
        # Format and send email with results
        pass
        
    def format_ocr_result(self, ocr_result):
        """Format OCR result for email."""
        # Format text for better readability
        pass
```

### Email Template Structure
```html
<h2>OCR Resultaat - {{ document_title }}</h2>

<div class="metadata">
  <p>Verwerkt op: {{ timestamp }}</p>
  <p>Document: {{ filename }}</p>
  <p>Aantal woorden: {{ word_count }}</p>
</div>

<div class="ocr-text">
  {{ formatted_text }}
</div>
```

## 🚀 Success Criteria
- OCR resultaten worden correct verwerkt en geformatteerd
- Notificatie emails worden betrouwbaar verzonden
- De gebruiker kan notificatie-instellingen configureren
- Verwerking is foutbestendig met goede error handling
- Code voldoet aan SOLID principes en blijft onder 300 regels per bestand

## 📝 Follow-up Acties voor Stap 4
- Database integratie voor resultaatopslag
- Historisch overzicht van verwerkte documenten
- Uitgebreidere configuratie-opties per gebruiker
