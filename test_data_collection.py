"""
Test om te verifiëren dat data_collection: "deny" wordt verzonden naar Openrouter API.
"""

import unittest
from unittest.mock import AsyncMock, patch
from core.ocr_processor import OCRProcessor


class TestDataCollection(unittest.TestCase):
    """Test data_collection parameter in API calls."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = OCRProcessor(api_key="test-key")
        
    @patch('httpx.AsyncClient.post')
    async def test_data_collection_deny_sent(self, mock_post):
        """Test dat data_collection: deny wordt verzonden in API call."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "test output"}}]
        }
        mock_post.return_value = mock_response
        
        # Test data
        test_file_b64 = "dGVzdA=="  # base64 van "test"
        test_prompt = "Extract text"
        test_content_type = "image/png"
        test_filename = "test.png"
        
        # Call API
        await self.processor._call_api(
            test_file_b64, test_prompt, test_content_type, test_filename
        )
        
        # Verify data_collection: "deny" in payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']  # json parameter
        
        self.assertEqual(payload.get('data_collection'), 'deny',
                        "data_collection parameter should be set to 'deny'")
        
        # Verify andere parameters nog steeds aanwezig
        self.assertIn('model', payload)
        self.assertIn('messages', payload)
        self.assertEqual(payload.get('temperature'), 0.0)
        
    async def test_payload_structure_intact(self):
        """Test dat payload structuur intact blijft na toevoeging."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
            mock_post.return_value = mock_response
            
            await self.processor._call_api("dGVzdA==", "test", "image/png", "test.png")
            
            payload = mock_post.call_args[1]['json']
            
            # Verify required fields
            required_fields = ['model', 'messages', 'max_tokens', 'temperature', 'data_collection']
            for field in required_fields:
                self.assertIn(field, payload, f"Field '{field}' should be present in payload")


if __name__ == '__main__':
    import asyncio
    
    async def run_tests():
        """Run async tests."""
        test = TestDataCollection()
        test.setUp()
        await test.test_data_collection_deny_sent()
        await test.test_payload_structure_intact()
        print("✅ Alle data_collection tests geslaagd")
    
    asyncio.run(run_tests())
