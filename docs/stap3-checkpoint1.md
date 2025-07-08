# Stap 3: Checkpoint 1 - Uitvoeringsplan

## 📝 Taken

### 1. Basis NotificationHandler Module
- [x] Creëer `core/notification_handler.py`
- [x] Implementeer `NotificationHandler` klasse met basis structuur
- [x] Voeg configuratie voor notificatie-emailadres toe
- [x] Implementeer `format_ocr_result()` functie voor tekstformattering
- [x] Implementeer `prepare_email()` voor email content generatie
- [x] Voeg apart verzendadres toe (apart van het account-emailadres)

### 2. Email Template
- [x] Creëer `templates/email_response.html` met responsive layout
- [x] Implementeer secties voor metagegevens, resultaattekst en footer
- [x] Voeg styling toe voor goede leesbaarheid op verschillende devices

### 3. SMTP Integratie
- [x] Hergebruik SMTP configuratie uit EmailHandler
- [x] Implementeer `send_ocr_result()` functie met error handling
- [x] Voeg retry mechanisme toe voor stabiele verzending

### 4. App.py Integratie
- [x] Update OCR verwerking in EmailHandler om NotificationHandler te gebruiken
- [x] Voeg configuratie-opties toe voor notificaties inclusief notificatie-emailadres
- [x] Voeg API endpoint toe voor het instellen van het notificatie-emailadres
- [x] Zorg voor juiste error handling en logging
- [x] Voeg API endpoint toe voor het instellen van een apart verzendadres

## 🧪 Unit Tests
- [x] Test voor formattering van OCR resultaten
- [x] Test voor email template rendering
- [x] Test voor SMTP verzending (met mock)

## 📋 Technische Details

### NotificationHandler API
```python
def __init__(self, smtp_config, notification_email=None, sender_email=None):
    """Initialize notification handler.
    
    Args:
        smtp_config (dict): SMTP server configuration
        notification_email (str, optional): Default notification email address
        sender_email (str, optional): Custom sender email (overrides smtp_config email)
    """
    # Implementatie...

def set_notification_email(self, email):
    """Set or update the notification email address.
    
    Args:
        email (str): Email address for notifications
    """
    # Implementatie...

def set_sender_email(self, email):
    """Set or update the sender email address.
    
    Args:
        email (str): Email address to send from
    """
    # Implementatie...

async def format_ocr_result(self, ocr_result):
    """Format OCR result text for better readability.
    
    Args:
        ocr_result (dict): OCR processor output
        
    Returns:
        dict: Formatted result with metadata
    """
    # Implementatie...

async def prepare_email(self, recipient, formatted_result, original_filename):
    """Prepare email content with OCR results.
    
    Args:
        recipient (str): Recipient email
        formatted_result (dict): Formatted OCR result
        original_filename (str): Original attachment filename
        
    Returns:
        MIMEMultipart: Prepared email message
    """
    # Implementatie...

async def send_ocr_result(self, ocr_result, original_attachment=None, recipient=None):
    """Send OCR results via email.
    
    Args:
        ocr_result (dict): OCR processor result
        original_attachment (bytes, optional): Original file
        recipient (str, optional): Custom recipient (overrides default notification_email)
        
    Returns:
        bool: Success status
    """
    # Use default notification_email if recipient not specified
    target_email = recipient or self.notification_email
    # Implementatie...
```

## 🎯 Acceptatiecriteria
1. OCR resultaten worden correct geformatteerd (paragrafen, witruimtes behouden)
2. Emails worden succesvol verzonden met OCR resultaten
3. Templates renderen correct op desktop en mobiel
4. Basis error handling werkt bij mislukte verzendingen

## ⏱️ Tijdsinschatting
- Notificatiehandler: ~2 uur
- Email template: ~1 uur
- SMTP integratie: ~1 uur
- App.py updates: ~1 uur
- Testen: ~1 uur

**Totaal: ~6 uur**
