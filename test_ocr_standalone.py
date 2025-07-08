#!/usr/bin/env python3
"""
Standalone OCR test script voor OpenRouter API debugging.
"""

import asyncio
import base64
import os
from pathlib import Path
import httpx

class OCRTester:
    """Standalone OCR tester."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "google/gemini-2.5-flash"
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://remarkable-ocr.local",
                "X-Title": "Remarkable OCR Tool",
                "Content-Type": "application/json"
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
        
    async def test_file(self, file_path: str):
        """Test OCR with any file."""
        path = Path(file_path)
        
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return
            
        # Read file
        file_bytes = path.read_bytes()
        
        # Check file size
        if len(file_bytes) > 20 * 1024 * 1024:  # 20MB limit
            print(f"❌ File too large: {len(file_bytes)} bytes")
            return
            
        print(f"📄 Testing: {path.name}")
        print(f"📏 File size: {len(file_bytes)} bytes")
        
        try:
            # Encode to base64
            file_b64 = base64.b64encode(file_bytes).decode('utf-8')
            content_type = self._get_content_type(path.name)
            
            # Nederlandse prompt - simpel en effectief
            prompt = (
                "Zet deze handgeschreven Nederlandse tekst om met OCR. "
                "Behoud paragrafen, regeleinden en opmaak. "
                "Geef alleen de geëxtraheerde tekst terug zonder commentaar."
            )
            
            # PDF vs Image - gebruik juiste content type
            if content_type == 'application/pdf':
                content_item = {
                    "type": "file",
                    "file": {
                        "filename": path.name,
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
                "temperature": 0.0
            }
            
            print("🚀 Calling OpenRouter API...")
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                text = result["choices"][0]["message"]["content"]
                print(f"✅ OCR Success!")
                print(f"📝 Raw response length: {len(text)} chars")
                print(f"📝 Full extracted text:\n{'-'*50}")
                print(text)
                print(f"{'-'*50}")
            else:
                print(f"❌ No choices in response")
                print(f"📝 Full response: {result}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

async def main():
    """Main test function."""
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Set OPENROUTER_API_KEY environment variable")
        return
        
    # Get file path from command line or use default
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("📁 Enter path to file: ")
    
    tester = OCRTester(api_key)
    await tester.test_file(file_path)
    await tester.close()

if __name__ == "__main__":
    asyncio.run(main())
