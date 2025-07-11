# Verzendadres Bug Fix - Samenvatting

## Probleem
Het verzendadres dat door de gebruiker werd ingesteld in de UI werd niet gebruikt bij OCR notificaties. Emails werden verzonden vanaf het hoofdaccount-adres in plaats van het ingestelde verzendadres.

## Root Cause
- Bij wijzigen van notificatie-emailadres werd nieuwe NotificationHandler aangemaakt zonder sender_email
- Bij instellen sender_email werd geen NotificationHandler aangemaakt als deze nog niet bestond

## Oplossing
**2 minimale fixes in routes/notification_routes.py:**

### Fix 1: set-notification-email endpoint
```python
# Include sender_email from config if available
sender_email = config.get("sender_email")
new_handler = NotificationHandler(smtp_config, notification_email, sender_email)
```

### Fix 2: set-sender-email endpoint
```python
# Create notification handler with current config if notification_email is set
notification_email = config.get("notification_email")
if notification_email:
    # ... create handler with both notification_email and sender_email
```

## Impact
- **S** (< 50 LOC) - Minimale wijzigingen aan bestaande code
- Geen breaking changes
- Bestaande functionaliteit intact
- DRY principe gerespecteerd door hergebruik bestaande configuratie

## Wat is er gedaan?
• Bug geïdentificeerd in NotificationHandler initialisatie
• Minimale fix toegepast die sender_email uit user config haalt
• Beide endpoints maken nu correct gebruik van opgeslagen verzendadres
• Bestaande functionaliteit blijft volledig intact
• Code getest en gevalideerd
