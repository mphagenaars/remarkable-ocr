# Stap 3 - Response Workflow: Implementatie Plan

## Overzicht
Deze feature zorgt ervoor dat OCR resultaten automatisch worden teruggestuurd naar de gebruiker via e-mail. Het systeem verwerkt de ruwe OCR uitvoer, formatteert deze en stelt een nette notificatie e-mail samen die naar de gebruiker wordt verzonden.

## Belangrijkste Functionaliteiten
- Verzenden van geformatteerde OCR resultaten via e-mail
- Ondersteuning voor aangepaste notificatie-emailadressen
- Ondersteuning voor aparte verzendadressen (los van het account-emailadres)
- Responsive HTML templates met metadata en tekst
- Foutafhandeling en automatisch opnieuw proberen bij verzendfouten

## Componenten

### NotificationHandler
De centrale component die verantwoordelijk is voor:
- Formatteren van OCR resultaten
- Samenstellen van notificatie e-mails
- Verzenden via SMTP
- Error handling en retries

### Email Templates
- Responsive HTML templates voor e-mailnotificaties
- Ondersteuning voor zowel tekst als HTML e-mails
- Duidelijke weergave van OCR resultaten

### Configuratieopties
- Instellingen voor notificatievoorkeuren
- Template aanpassingen
- Verzendopties (bijlage, alleen tekst, etc.)

## API

```python
# Initialisatie met notificatie-emailadres en apart verzendadres
notification = NotificationHandler(
    smtp_config, 
    notification_email="user@example.com",
    sender_email="noreply@mycompany.com"
)

# Basis gebruik
success = await notification.send_ocr_result(ocr_result)

# Notificatie-emailadres aanpassen
notification.set_notification_email("new_address@example.com")

# Verzendadres aanpassen
notification.set_sender_email("different_sender@mycompany.com")

# Met originele bijlage
success = await notification.send_ocr_result(
    ocr_result,
    original_attachment=pdf_bytes
)

# Met specifieke ontvanger (override default)
success = await notification.send_ocr_result(
    ocr_result,
    recipient="specific_user@example.com"
)

# Configuratie-opties
notification.set_template("default")
notification.enable_attachments(True)
```

## Security Overwegingen
- SMTP authenticatie met veilige opslag van credentials
- Sanitization van OCR output in templates ter voorkoming van XSS
- Rate limiting om spam te voorkomen
- Logging van alle verzonden notificaties

## Integratie met Bestaande Componenten
- EmailHandler levert OCR resultaten aan NotificationHandler
- NotificationHandler gebruikt bestaande SMTP configuratie
- App.py biedt configuratie-endpoints voor notificatie-instellingen
- Notificatie-emailadres configuratie onafhankelijk van monitoring emailadres
- Verzendadres kan apart worden geconfigureerd (los van het account-emailadres)

## Toekomstige Uitbreidingen
- Database-opslag van verzonden notificaties
- Geavanceerde template aanpassingen
- Alternatieve notificatiekanalen (Slack, MS Teams)

## Implementatie Details

### Notification Handler Module
De `NotificationHandler` klasse is geïmplementeerd in `core/notification_handler.py` met de volgende functionaliteiten:

1. **Configuratie**
   - SMTP configuratie overerving van EmailHandler
   - Instelbaar notificatie-emailadres
   - Retry mechanisme met exponentiële backoff

2. **Text Formattering**
   - Behoudt paragrafen en witruimte in OCR tekst
   - Voegt metadata toe (vertrouwensscore, model, verwerkingstijd)

3. **Email Generatie**
   - Responsive HTML template met secties voor metadata en tekst
   - Plain text fallback voor email clients zonder HTML ondersteuning
   - Optionele bijlage van origineel document

4. **Error Handling**
   - Robuuste SMTP foutafhandeling
   - Automatische retry bij verbindingsproblemen
   - Gedetailleerde logging

### API Endpoints
De volgende endpoints zijn toegevoegd aan `app.py`:

- **POST /set-notification-email**: Stelt het notificatie-emailadres in voor een gebruiker
  - Parameters: `email` (gebruiker), `notification_email` (notificatie ontvanger)
  - Retourneert bevestiging of foutmelding

### Integratie
De NotificationHandler is geïntegreerd met de bestaande componenten:

1. EmailHandler gebruikt NotificationHandler om OCR resultaten te versturen
2. Configuratie gebeurt via app.py
3. SMTP instellingen worden hergebruikt
4. Notificatie-emailadres wordt opgeslagen in user_configs

### Testen
Unit tests zijn beschikbaar in `test_notification.py`:

- Tests voor formattering van OCR resultaten
- Tests voor email template rendering
- Tests voor SMTP verzending met mock

## Toekomstige Verbeteringen
- Database opslag van verzonden notificaties
- Template selectie mogelijkheid
- Instellingen voor verzenden van bijlages
- Alternatieve notificatiekanalen zoals Slack
