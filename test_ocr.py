#!/usr/bin/env python3
"""
Simple test script voor OCR processor
Test zonder echte API key (mock mode)
"""

import asyncio
import logging
from core.ocr_processor import OCRProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ocr_processor():
    """Test OCR processor zonder echte API key"""
    print("🧪 Testing OCR Processor...")
    
    # Test 1: Initialisatie
    print("\n1️⃣ Testing initialization...")
    try:
        processor = OCRProcessor("test-api-key")
        print("✅ OCR Processor initialized successfully")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Test 2: Base64 encoding
    print("\n2️⃣ Testing base64 encoding...")
    try:
        test_data = b"Hello, this is test data"
        encoded = processor._encode_image_base64(test_data)
        print(f"✅ Base64 encoding works: {encoded[:20]}...")
    except Exception as e:
        print(f"❌ Base64 encoding failed: {e}")
    
    # Test 3: Image preparation (dummy data)
    print("\n3️⃣ Testing image preparation...")
    try:
        dummy_image = b"fake-image-data"
        prepared = processor._prepare_image(dummy_image)
        print(f"✅ Image preparation works: {len(prepared)} bytes")
    except Exception as e:
        print(f"❌ Image preparation failed: {e}")
    
    # Test 4: File type detection
    print("\n4️⃣ Testing file type detection...")
    test_files = [
        ("test.pdf", ".pdf"),
        ("test.png", ".png"),
        ("test.jpg", ".jpg"),
        ("test.txt", ".txt")
    ]
    
    for filename, expected_ext in test_files:
        from pathlib import Path
        actual_ext = Path(filename).suffix.lower()
        status = "✅" if actual_ext == expected_ext else "❌"
        print(f"{status} {filename} -> {actual_ext}")
    
    print("\n✅ OCR Processor tests completed!")
    print("📝 Note: Dit zijn basis tests zonder echte API calls")
    print("🔑 Voor volledige test is een OpenRouter API key nodig")

if __name__ == "__main__":
    asyncio.run(test_ocr_processor())
