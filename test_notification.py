"""
Unit tests for NotificationHandler
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.notification_handler import NotificationHandler


class TestNotificationHandler(unittest.TestCase):
    """Test suite for NotificationHandler"""

    def setUp(self):
        """Setup test environment"""
        self.smtp_config = {
            "email": "test@example.com",
            "password": "test_password",
            "smtp_server": "smtp.example.com",
            "smtp_port": 587
        }
        self.notification_email = "notify@example.com"
        self.handler = NotificationHandler(self.smtp_config, self.notification_email)

    def test_set_notification_email(self):
        """Test setting notification email"""
        new_email = "new@example.com"
        self.handler.set_notification_email(new_email)
        self.assertEqual(self.handler.notification_email, new_email)

    def test_format_ocr_result(self):
        """Test formatting OCR result"""
        # Sample OCR result
        ocr_result = {
            "text": "This is a test document.\nWith multiple lines.\n\nAnd paragraphs.",
            "confidence": 0.95,
            "processing_time": "2.3s",
            "timestamp": "2025-07-07",
            "model": "google/gemini-pro-vision",
            "success": True
        }
        
        # Call the async method in a synchronous way for testing
        formatted_result = asyncio.run(self.handler.format_ocr_result(ocr_result))
        
        # Check all keys are present
        self.assertIn("text", formatted_result)
        self.assertIn("confidence", formatted_result)
        self.assertIn("processing_time", formatted_result)
        self.assertIn("timestamp", formatted_result)
        self.assertIn("model", formatted_result)
        self.assertIn("success", formatted_result)
        
        # Check text is preserved
        self.assertEqual(formatted_result["text"], ocr_result["text"])
        
    def test_format_ocr_result_preserves_newlines(self):
        """Test that formatting preserves newlines in text"""
        # OCR result with multiple lines and paragraphs
        ocr_result = {
            "text": "Eerste regel\nTweede regel\n\nNieuwe paragraaf\nMet meerdere regels",
            "confidence": 0.95,
            "success": True
        }
        
        formatted_result = asyncio.run(self.handler.format_ocr_result(ocr_result))
        
        # Check that newlines are preserved exactly in original text
        self.assertEqual(formatted_result["text"], ocr_result["text"])
        self.assertIn("\n", formatted_result["text"])
        self.assertIn("\n\n", formatted_result["text"])  # Double newlines for paragraphs
        
        # Check that HTML version has proper <br> tags
        self.assertIn("html_text", formatted_result)
        html_text = formatted_result["html_text"]
        self.assertIn("<br>", html_text)
        self.assertIn("<br><br>", html_text)  # Double breaks for paragraphs
        
        # Ensure original text structure is converted correctly
        self.assertIn("Eerste regel<br>Tweede regel<br><br>Nieuwe paragraaf", html_text)
        
    def test_convert_newlines_to_html(self):
        """Test HTML newline conversion function"""
        # Test the private method directly
        test_text = "Line 1\nLine 2\n\nParagraph 2\nLine 3"
        expected_html = "Line 1<br>Line 2<br><br>Paragraph 2<br>Line 3"
        
        result = self.handler._convert_newlines_to_html(test_text)
        self.assertEqual(result, expected_html)
        
        # Test HTML escaping
        test_text_with_html = "Text with <script>alert('xss')</script>\nNew line"
        result = self.handler._convert_newlines_to_html(test_text_with_html)
        self.assertIn("&lt;script&gt;", result)  # HTML should be escaped
        self.assertIn("<br>", result)  # But newlines should become <br>
        
    @patch('smtplib.SMTP')
    def test_send_with_retry(self, mock_smtp):
        """Test sending email with retry mechanism"""
        # Create a mock email message
        message = MagicMock()
        message.as_string.return_value = "Test email content"
        recipient = "test@example.com"
        
        # Configure the mock SMTP client
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test successful send
        result = asyncio.run(self.handler._send_with_retry(message, recipient))
        self.assertTrue(result)
        
        # Verify SMTP methods were called
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            self.smtp_config["email"], 
            self.smtp_config["password"]
        )
        mock_smtp_instance.sendmail.assert_called_once_with(
            self.smtp_config["email"],
            recipient,
            message.as_string()
        )
        
    @patch('smtplib.SMTP')
    def test_send_with_retry_failure(self, mock_smtp):
        """Test send retry mechanism on failure"""
        # Create a mock email message
        message = MagicMock()
        message.as_string.return_value = "Test email content"
        recipient = "test@example.com"
        
        # Configure mock to raise exception on first attempt
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.side_effect = [
            Exception("Connection error"),  # First attempt fails
            mock_smtp_instance,            # Second attempt succeeds
        ]
        
        # Temporarily set short retry delay for testing
        original_delay = self.handler.retry_delay
        self.handler.retry_delay = 0.1
        
        # Test retry behavior
        result = asyncio.run(self.handler._send_with_retry(message, recipient))
        
        # Should still succeed on retry
        self.assertTrue(result)
        
        # Reset retry delay
        self.handler.retry_delay = original_delay
        
    @patch('jinja2.Environment.get_template')
    def test_prepare_email(self, mock_get_template):
        """Test preparing email content"""
        # Mock template rendering
        mock_template = MagicMock()
        mock_template.render.return_value = "<html><body>Test Email</body></html>"
        mock_get_template.return_value = mock_template
        
        # Sample data
        recipient = "test@example.com"
        formatted_result = {
            "text": "Test document content",
            "confidence": 0.95,
            "model": "test-model"
        }
        filename = "test.pdf"
        
        # Prepare email
        message = asyncio.run(self.handler.prepare_email(recipient, formatted_result, filename))
        
        # Check email headers
        self.assertEqual(message["Subject"], f"OCR Resultaat: {filename}")
        self.assertEqual(message["From"], self.smtp_config["email"])
        self.assertEqual(message["To"], recipient)
        
        # Check template was called
        mock_template.render.assert_called_once()
        
        # Check both plain text and HTML parts are present
        self.assertEqual(len(message.get_payload()), 2)
        self.assertEqual(message.get_payload(0).get_content_type(), "text/plain")
        self.assertEqual(message.get_payload(1).get_content_type(), "text/html")


if __name__ == "__main__":
    unittest.main()