# OCR Feature Documentation

## Overview
De OCR feature maakt het mogelijk om PDF en PNG bestanden automatisch om te zetten naar tekst via een AI vision model. 
Deze feature is geïntegreerd in de email handler en verwerkt automatisch bijlagen uit emails van toegestane afzenders.

## Componenten

### OCRProcessor
De `OCRProcessor` klasse is verantwoordelijk voor:
- Direct verwerken van PDF bestanden via OpenRouter API
- Direct verwerken van PNG/JPG afbeeldingen 
- Tekst extractie met behulp van Gemini 2.5 Flash
- Afhandelen van meerdere pagina's in PDF documenten

### Integratie met EmailHandler
- EmailHandler gebruikt de OCRProcessor voor automatische verwerking van bijlagen
- OCR API key configuratie via de web interface
- Whitelist filteren van email afzenders voor security
- Ondersteuning voor PDF en PNG formaten

## API
```python
# Initialisatie
processor = OCRProcessor(api_key="openrouter_api_key")

# PDF verwerking
result = await processor.extract_text_from_pdf(pdf_bytes)

# Afbeelding verwerking
result = await processor.extract_text_from_image(image_bytes)

# Bijlage verwerking (detecteert automatisch het type)
result = await processor.process_attachment(filename, file_bytes)
```

## Configuratie
De OCR feature kan worden geconfigureerd via de web interface:
1. Voer een OpenRouter API key in bij de email configuratie
2. De API key wordt gebruikt voor alle OCR verwerking
3. Zonder API key werkt alleen de email polling (geen OCR)

## Beveiligingsmaatregelen
- API key wordt veilig opgeslagen (niet persistent in MVP fase)
- Alleen bijlagen van whitelisted afzenders worden verwerkt
- Onveilige bestandstypen worden gefilterd

## Toekomstige verbeteringen
- OCR resultaten opslaan in PostgreSQL database
- Email notificaties met geëxtraheerde tekst
- Custom OCR model selectie
- Documentformaat behoud tijdens extractie
