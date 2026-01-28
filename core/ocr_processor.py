"""
OCR Processing Module voor Remarkable 2 notities.
Gebruikt OpenRouter API voor OCR-conversie van PDF/PNG bestanden.
"""

import base64
import logging
import os
import asyncio
import time
from pathlib import Path
from typing import Dict, Any
import httpx

from .retry import compute_backoff
from .metrics import inc_counter, observe_duration

logger = logging.getLogger(__name__)


class OCRProcessor:
    """OCR processor using OpenRouter API with vision-capable models."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "google/gemini-2.5-flash",
        max_retries: int | None = None,
        base_retry_delay: float | None = None,
        max_retry_delay: float | None = None,
        retry_multiplier: float | None = None,
        retry_jitter: float | None = None,
    ):
        """Initialize OCR processor with API key and model."""
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.max_retries = max_retries if max_retries is not None else int(os.getenv("OCR_MAX_RETRIES", "3"))
        self.base_retry_delay = base_retry_delay if base_retry_delay is not None else float(os.getenv("OCR_RETRY_BASE_DELAY", "2"))
        self.max_retry_delay = max_retry_delay if max_retry_delay is not None else float(os.getenv("OCR_RETRY_MAX_DELAY", "30"))
        self.retry_multiplier = retry_multiplier if retry_multiplier is not None else float(os.getenv("OCR_RETRY_MULTIPLIER", "2"))
        self.retry_jitter = retry_jitter if retry_jitter is not None else float(os.getenv("OCR_RETRY_JITTER", "0.1"))
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
        start_time = time.monotonic()
        inc_counter("ocr_requests_total")
        
        try:
            # Get correct content type
            content_type = self._get_content_type(filename)
            
            # Nederlandse prompt - simpel en effectief
            prompt = (
                "Je krijgt van mij een PDF met daarop mijn aantekeningen. "
                "Deze aantekeningen kunnen bestaan uit handgeschreven tekst en plaatjes. "
                "Als je handgeschreven Nederlandse tekst aantreft dan zet je deze om met OCR. "
                "Maak logische zinnen. Zorg dat zinnen die bij elkaar horen op 1 regel komen. "
                "Corrigeer spelfouten waar nodig. "
                "Als je een tekening aantreft dan stuur je deze als plaatje mee. "
                "Behoud paragrafen, opmaak, bullets en pijltjes. "
                "Stuur de output terug zonder enig commentaar. "
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
            observe_duration("ocr_processing_seconds", time.monotonic() - start_time)
            inc_counter("ocr_success_total")
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
            observe_duration("ocr_processing_seconds", time.monotonic() - start_time)
            inc_counter("ocr_fail_total")
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
        
        last_error: Exception | None = None
        total_attempts = max(self.max_retries, 1)

        for attempt in range(1, total_attempts + 1):
            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_error = e
                should_retry = True
                if isinstance(e, httpx.HTTPStatusError):
                    status = e.response.status_code
                    should_retry = status in (408, 429) or 500 <= status <= 599

                if not should_retry or attempt >= total_attempts:
                    raise

                delay = compute_backoff(
                    attempt=attempt,
                    base_delay=self.base_retry_delay,
                    max_delay=self.max_retry_delay,
                    multiplier=self.retry_multiplier,
                    jitter=self.retry_jitter,
                )
                logger.warning(
                    "OCR API call failed (attempt %s/%s): %s. Retrying in %.2fs",
                    attempt,
                    total_attempts,
                    e,
                    delay,
                )
                await asyncio.sleep(delay)
            except Exception as e:
                last_error = e
                if attempt >= total_attempts:
                    raise
                delay = compute_backoff(
                    attempt=attempt,
                    base_delay=self.base_retry_delay,
                    max_delay=self.max_retry_delay,
                    multiplier=self.retry_multiplier,
                    jitter=self.retry_jitter,
                )
                logger.warning(
                    "OCR API call failed (attempt %s/%s): %s. Retrying in %.2fs",
                    attempt,
                    total_attempts,
                    e,
                    delay,
                )
                await asyncio.sleep(delay)

        if last_error:
            raise last_error
        raise RuntimeError("OCR API call failed without specific error")
    
    async def close(self):
        """Close HTTP client."""
        if hasattr(self, 'client'):
            await self.client.aclose()
