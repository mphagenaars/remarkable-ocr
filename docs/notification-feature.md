# Stap 3 - Response Workflow: Implementatie Plan

## Overzicht
Deze feature zorgt ervoor dat OCR resultaten automatisch worden teruggestuurd naar de gebruiker via e-mail. Het systeem verwerkt de ruwe OCR uitvoer, formatteert deze en stelt een nette notificatie e-mail samen die naar de gebruiker wordt verzonden.

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
# Initialisatie met notificatie-emailadres
notification = NotificationHandler(smtp_config, notification_email="user@example.com")

# Basis gebruik
success = await notification.send_ocr_result(ocr_result)

# Notificatie-emailadres aanpassen
notification.set_notification_email("new_address@example.com")

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

## Toekomstige Uitbreidingen
- Database-opslag van verzonden notificaties
- Geavanceerde template aanpassingen
- Alternatieve notificatiekanalen (Slack, MS Teams)
