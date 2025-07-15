"""
OCR Processing Module voor Remarkable 2 notities.
Gebruikt OpenRouter API voor OCR-conversie van PDF/PNG bestanden.
"""

import base64
import logging
from pathlib import Path
from typing import Dict, Any
import httpx

logger = logging.getLogger(__name__)


class OCRProcessor:
    """OCR processor using OpenRouter API with vision-capable models."""
    
    def __init__(self, api_key: str, model: str = "google/gemini-2.5-flash"):
        """Initialize OCR processor with API key and model."""
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://remarkable-ocr.local",
                "X-Title": "Remarkable OCR Tool"
            }
        )
    
    def _get_content_type(self, filename: str) -> str:
        """Get correct MIME type for file extension."""
        file_ext = Path(filename).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml'
        }
        return content_types.get(file_ext, 'application/octet-stream')
    
    def _encode_base64(self, file_bytes: bytes) -> str:
        """Encode bytes to base64 string."""
        return base64.b64encode(file_bytes).decode('utf-8')
    
    async def process_attachment(self, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """Process attachment for OCR and return extracted text."""
        logger.info(f"Processing attachment: {filename} ({len(file_bytes)} bytes)")
        
        try:
            # Get correct content type
            content_type = self._get_content_type(filename)
            
            # Nederlandse prompt - simpel en effectief
            prompt = (
                "Zet deze handgeschreven Nederlandse tekst om met OCR. "
                "Behoud paragrafen, regeleinden en opmaak. "
                "Geef alleen de geëxtraheerde tekst terug zonder commentaar."
            )
            
            # Encode to base64
            file_b64 = self._encode_base64(file_bytes)
            
            # Call API with correct content structure
            response = await self._call_api(file_b64, prompt, content_type, filename)
            
            # Extract text
            extracted_text = ""
            if response.get("choices") and len(response["choices"]) > 0:
                extracted_text = response["choices"][0]["message"]["content"].strip()
            
            # Return result
            return {
                "text": extracted_text,
                "filename": filename,
                "confidence": "high" if len(extracted_text) > 50 else "low",
                "model": self.model,
                "file_size": len(file_bytes),
                "content_type": content_type,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"OCR processing failed for {filename}: {e}")
            return {
                "filename": filename,
                "text": "",
                "confidence": "failed",
                "error": str(e),
                "success": False
            }
    
    async def _call_api(self, file_b64: str, prompt: str, content_type: str, filename: str) -> Dict[str, Any]:
        """Call OpenRouter API with file content."""
        # PDF vs Image - gebruik juiste content structure
        if content_type == 'application/pdf':
            content_item = {
                "type": "file",
                "file": {
                    "filename": filename,
                    "file_data": f"data:{content_type};base64,{file_b64}"
                }
            }
        else:
            content_item = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{content_type};base64,{file_b64}"
                }
            }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        content_item
                    ]
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.0,
            "data_collection": "deny"
        }
        
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close HTTP client."""
        if hasattr(self, 'client'):
            await self.client.aclose()
