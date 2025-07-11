# Verzendadres Functionaliteit - Verwijdering

## Probleemanalyse

Onderzoek naar waarom het opgegeven verzendadres ("sender_email") niet als afzender werd gebruikt bij OCR notificaties toonde aan dat:

### Root Cause
SMTP-servers (zoals Gmail) laten niet toe dat je een willekeurig afzenderadres gebruikt bij authenticatie met een ander account. Het verzendadres wordt genegeerd/overschreven door de server en vervangen door het authenticatie-emailadres.

### Impactanalyse
- Geen core functionaliteit afhankelijk van sender_email
- Geen tests beschadigd door verwijdering
- Optionele feature die geen toegevoegde waarde biedt

## Uitgevoerde Verwijderingen

### Backend
- **NotificationHandler**: sender_email parameter en logica verwijderd uit constructor
- **NotificationHandler**: `set_sender_email()` methode volledig verwijderd  
- **Routes**: `/set-sender-email` endpoint verwijderd uit `notification_routes.py`
- **Connection**: sender_email parameter verwijderd uit `connection_routes.py`
- **Polling**: sender_email logica verwijderd uit `polling_routes.py`

### Frontend
- **HTML**: Verzendadres velden verwijderd uit `templates/index.html`
- **HTML**: Aparte sender-form sectie volledig verwijderd
- **JavaScript**: `setupSenderForm()` functie verwijderd uit `form-handlers.js`
- **JavaScript**: Sender form referenties verwijderd uit `app.js`

### Documentatie
- Deze summary toegevoegd ter documentatie van de verwijdering
- Oude verzendadres documentatie blijft ter referentie

## Impact
- **M** (50-300 LOC) - Verwijdering uit meerdere bestanden, maar geen architectuurwijzigingen

## Wat is er gedaan?
- Volledige verwijdering van custom verzendadres functionaliteit
- Backend gebruikt nu altijd het SMTP authenticatie-emailadres als afzender
- UI opgeruimd zonder verzendadres configuratie-opties
- Alle tests blijven werkend
- Notification functionaliteit blijft volledig intact
