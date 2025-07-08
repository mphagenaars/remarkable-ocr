"""
Test script to verify notification functionality
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.notification_handler import NotificationHandler

async def main():
    """Test notification functionality"""
    # Load environment variables
    load_dotenv()
    
    # Use environment variables or default values for testing
    smtp_config = {
        "email": os.getenv("TEST_EMAIL", "test@example.com"),
        "password": os.getenv("TEST_PASSWORD", "test_password"),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587"))
    }
    
    notification_email = os.getenv("NOTIFICATION_EMAIL", "notify@example.com")
    
    # Create handler
    handler = NotificationHandler(smtp_config, notification_email)
    
    # Sample OCR result
    ocr_result = {
        "text": "Dit is een test van de notification handler.\n\nHet lijkt erop dat de handler correct werkt.\n\nDit is een paragraaf om te testen of witregels correct behouden blijven.\n\nEinde van de test.",
        "confidence": 0.95,
        "processing_time": "1.2s",
        "timestamp": "2025-07-07",
        "model": "google/gemini-pro-vision",
        "success": True,
        "filename": "test_document.pdf"
    }
    
    # Format and send
    print(f"Formatting OCR result...")
    formatted_result = await handler.format_ocr_result(ocr_result)
    
    print(f"Sending notification to {notification_email}...")
    success = await handler.send_ocr_result(ocr_result)
    
    if success:
        print("✅ Notification sent successfully!")
    else:
        print("❌ Failed to send notification")

if __name__ == "__main__":
    asyncio.run(main())
