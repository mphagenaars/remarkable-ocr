# OCR Processor Feature

## Overzicht
De OCR Processor gebruikt OpenRouter API met vision-capable models om handgeschreven tekst uit Remarkable 2 notities te extraheren.

## Technische Implementatie

### Model Selectie
- **Default:** `google/gemini-2.5-flash`
- **Reden:** Goede balans tussen snelheid en kwaliteit voor Nederlandse tekst
- **Configureerbaar:** Via constructor parameter

### API Integratie
- **Provider:** OpenRouter API (https://openrouter.ai)
- **Timeout:** 120 seconden (voor grote bestanden)
- **Rate limiting:** Automatisch via OpenRouter
- **Data collection:** Expliciet geweigerd (`"data_collection": "deny"`)

### Bestandsondersteuning
| Formaat | Content-Type | OCR Method |
|---------|--------------|------------|
| PDF | `application/pdf` | File upload |
| PNG | `image/png` | Image URL |
| JPG/JPEG | `image/jpeg` | Image URL |
| SVG | `image/svg+xml` | Image URL |

### Nederlandse Optimalisatie
```python
prompt = (
    "Zet deze handgeschreven Nederlandse tekst om met OCR. "
    "Behoud paragrafen, regeleinden en opmaak. "
    "Geef alleen de geëxtraheerde tekst terug zonder commentaar."
)
```

**Waarom deze prompt:**
- Expliciet Nederlandse focus
- Behoudt document structuur
- Minimaliseert model "commentaar"
- Geoptimaliseerd voor handschrift

### Configuration Parameters
```python
{
    "max_tokens": 4000,      # Voldoende voor lange notities
    "temperature": 0.0,      # Deterministisch voor consistentie
    "data_collection": "deny" # Privacy-first
}
```

## Usage Example

```python
from core.ocr_processor import OCRProcessor

# Initialize
processor = OCRProcessor(
    api_key="your_openrouter_key",
    model="google/gemini-2.5-flash"
)

# Process file
with open("notebook.pdf", "rb") as f:
    result = await processor.process_attachment(
        filename="notebook.pdf",
        file_bytes=f.read()
    )

print(result["text"])  # Extracted text
await processor.close()
```

## Response Format

```python
{
    "text": "Geëxtraheerde tekst...",
    "filename": "notebook.pdf",
    "confidence": "high|low|failed",
    "model": "google/gemini-2.5-flash",
    "file_size": 1234567,
    "content_type": "application/pdf",
    "success": True
}
```

## Error Handling

- **Network errors:** Automatic retry via httpx
- **API errors:** Graceful fallback met error details
- **File errors:** Validation en user-friendly messages
- **Timeout:** 120s timeout voor grote bestanden

## Performance Considerations

- **Base64 encoding:** In-memory voor bestanden < 10MB
- **Async processing:** Non-blocking voor web interface
- **Connection pooling:** Via httpx AsyncClient
- **Resource cleanup:** Explicit client close

## Security Features

- **No data retention:** OpenRouter data collection disabled
- **API key protection:** Environment variable only
- **Input validation:** File type en size checks
- **Error sanitization:** Geen API details in user errors
