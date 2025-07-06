#!/usr/bin/env python3
"""
Simple test script voor Email Handler
Test configuratie en validatie
"""

import logging
from core.email_handler import EmailConfig, create_email_config, validate_email_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_config():
    """Test email configuration functions"""
    print("📧 Testing Email Configuration...")
    
    # Test 1: Valid configuration
    print("\n1️⃣ Testing valid configuration...")
    try:
        config_data = {
            "email": "test@example.com",
            "password": "test-password",
            "imap_server": "imap.example.com",
            "imap_port": 993,
            "smtp_server": "smtp.example.com", 
            "smtp_port": 587,
            "openrouter_api_key": "sk-test-key"
        }
        allowed_senders = ["sender@example.com"]
        
        config = create_email_config(config_data, allowed_senders)
        print(f"✅ Config created: {config.email}")
        print(f"✅ IMAP: {config.imap_server}:{config.imap_port}")
        print(f"✅ SMTP: {config.smtp_server}:{config.smtp_port}")
        print(f"✅ Senders: {config.allowed_senders}")
        print(f"✅ OCR Key: {'Present' if config.openrouter_api_key else 'None'}")
        
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        return
    
    # Test 2: Configuration validation
    print("\n2️⃣ Testing configuration validation...")
    
    # Valid config
    is_valid, error = validate_email_config(config)
    print(f"✅ Valid config test: {is_valid}, error: {error}")
    
    # Invalid configs
    test_cases = [
        (EmailConfig("", "pass", "imap", 993, "smtp", 587, ["sender"]), "Empty email"),
        (EmailConfig("invalid-email", "pass", "imap", 993, "smtp", 587, ["sender"]), "Invalid email format"),
        (EmailConfig("test@email.com", "", "imap", 993, "smtp", 587, ["sender"]), "Empty password"),
        (EmailConfig("test@email.com", "pass", "imap", 993, "smtp", 587, []), "No allowed senders"),
    ]
    
    for test_config, description in test_cases:
        is_valid, error = validate_email_config(test_config)
        status = "✅" if not is_valid else "❌"
        print(f"{status} {description}: valid={is_valid}, error={error}")
    
    print("\n✅ Email Configuration tests completed!")

if __name__ == "__main__":
    test_email_config()
