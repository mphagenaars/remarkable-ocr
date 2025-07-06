"""
OCR Processing Module voor Remarkable 2 notities.

Gebruikt OpenRouter API voor OCR-conversie van PDF/PNG bestanden.
Ondersteunt zowel handgeschreven tekst als gescannte documenten.
"""

import base64
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import tempfile
import os

import httpx

logger = logging.getLogger(__name__)


class OCRProcessor:
    """OCR processor using OpenRouter API with vision-capable models."""
    
    def __init__(self, api_key: str, model: str = "google/gemini-pro-vision"):
        """
        Initialize OCR processor.
        
        Args:
            api_key: OpenRouter API key
            model: Vision model to use (default: gemini-pro-vision)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.Client(
            timeout=120.0,  # OCR can take time
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://remarkable-ocr.local",
                "X-Title": "Remarkable OCR Tool"
            }
        )
    
    def _encode_image_base64(self, image_bytes: bytes) -> str:
        """Encode image bytes to base64 string."""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _prepare_image(self, image_bytes: bytes, max_size: int = 2048) -> bytes:
        """
        Prepare image for OCR. For now, just return original bytes.
        Gemini can handle large images efficiently.
        
        Args:
            image_bytes: Raw image bytes
            max_size: Maximum dimension in pixels (unused for now)
            
        Returns:
            Image bytes (unchanged for now)
        """
        # For simplicity, return original bytes
        # Gemini handles image optimization internally
        logger.debug(f"Using original image ({len(image_bytes)} bytes)")
        return image_bytes
    
    async def _call_vision_api_pdf(self, pdf_b64: str, prompt: str) -> Dict[str, Any]:
        """
        Call OpenRouter vision API for PDF OCR directly.
        
        Args:
            pdf_b64: Base64 encoded PDF
            prompt: OCR instruction prompt
            
        Returns:
            API response dict
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:application/pdf;base64,{pdf_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 8000,  # More tokens for multi-page PDFs
            "temperature": 0.1
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter PDF API error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"PDF OCR API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"PDF OCR API call failed: {e}")
            raise
    
    async def _call_vision_api(self, image_b64: str, prompt: str) -> Dict[str, Any]:
        """
        Call OpenRouter vision API for OCR.
        
        Args:
            image_b64: Base64 encoded image
            prompt: OCR instruction prompt
            
        Returns:
            API response dict
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.1  # Low temperature for consistent OCR
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"OCR API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"OCR API call failed: {e}")
            raise
    
    async def extract_text_from_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from a single image using OCR.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Dict with extracted text and metadata
        """
        try:
            # Optimize image
            optimized_image = self._prepare_image(image_bytes)
            image_b64 = self._encode_image_base64(optimized_image)
            
            # OCR prompt optimized for handwriting
            prompt = """
            Please extract ALL text from this image with high accuracy. This appears to be handwritten notes, possibly from a Remarkable 2 tablet.

            Instructions:
            1. Extract ALL visible text, including handwritten notes, typed text, diagrams labels, etc.
            2. Maintain the logical reading order (top to bottom, left to right)
            3. Preserve structure with line breaks and spacing where meaningful
            4. If text is unclear, make your best interpretation but note uncertainty
            5. Include any numbers, symbols, or special characters you can identify
            6. If there are multiple columns or sections, separate them clearly

            Return only the extracted text content. Do not include explanations or commentary.
            """
            
            # Call vision API
            response = await self._call_vision_api(image_b64, prompt)
            
            # Extract text from response
            extracted_text = ""
            if response.get("choices") and len(response["choices"]) > 0:
                extracted_text = response["choices"][0]["message"]["content"].strip()
            
            return {
                "text": extracted_text,
                "confidence": "high" if len(extracted_text) > 10 else "low",
                "model_used": self.model,
                "page_count": 1,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            return {
                "text": "",
                "confidence": "failed",
                "error": str(e),
                "success": False
            }
    
    async def extract_text_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from PDF using direct vision API call.
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Dict with extracted text and metadata
        """
        try:
            # Encode PDF to base64
            pdf_b64 = self._encode_image_base64(pdf_bytes)
            
            # OCR prompt optimized for PDF documents
            prompt = """
            Please extract ALL text from this PDF document with high accuracy. This may contain handwritten notes from a Remarkable 2 tablet or scanned documents.

            Instructions:
            1. Extract ALL visible text from all pages, including handwritten notes, typed text, diagrams labels, etc.
            2. Maintain the logical reading order (top to bottom, left to right)
            3. If there are multiple pages, clearly separate them with "--- Page X ---" headers
            4. Preserve structure with line breaks and spacing where meaningful
            5. If text is unclear, make your best interpretation but note uncertainty
            6. Include any numbers, symbols, or special characters you can identify
            7. If there are multiple columns or sections, separate them clearly

            Return only the extracted text content. Do not include explanations or commentary.
            """
            
            # Call vision API directly with PDF
            response = await self._call_vision_api_pdf(pdf_b64, prompt)
            
            # Extract text from response
            extracted_text = ""
            if response.get("choices") and len(response["choices"]) > 0:
                extracted_text = response["choices"][0]["message"]["content"].strip()
            
            # Estimate page count from content structure
            page_indicators = extracted_text.count("--- Page")
            estimated_pages = max(1, page_indicators) if page_indicators > 0 else 1
            
            return {
                "text": extracted_text,
                "confidence": "high" if len(extracted_text) > 50 else "low",
                "model_used": self.model,
                "page_count": estimated_pages,
                "processing_method": "direct_pdf",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            return {
                "text": "",
                "confidence": "failed",
                "error": str(e),
                "success": False
            }
    
    async def process_attachment(self, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """
        Process an email attachment for OCR.
        
        Args:
            filename: Original filename
            file_bytes: File content bytes
            
        Returns:
            OCR result dict
        """
        file_ext = Path(filename).suffix.lower()
        
        logger.info(f"Processing attachment: {filename} ({len(file_bytes)} bytes)")
        
        try:
            if file_ext == '.pdf':
                result = await self.extract_text_from_pdf(file_bytes)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                result = await self.extract_text_from_image(file_bytes)
            else:
                return {
                    "text": "",
                    "confidence": "failed",
                    "error": f"Unsupported file type: {file_ext}",
                    "success": False
                }
            
            # Add filename to result
            result["filename"] = filename
            result["file_type"] = file_ext
            result["file_size"] = len(file_bytes)
            
            return result
            
        except Exception as e:
            logger.error(f"Attachment processing failed for {filename}: {e}")
            return {
                "filename": filename,
                "text": "",
                "confidence": "failed",
                "error": str(e),
                "success": False
            }
    
    def close(self):
        """Close HTTP client."""
        if hasattr(self, 'client'):
            self.client.close()
