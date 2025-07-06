#!/usr/bin/env python3
"""
API endpoint tests voor de Remarkable OCR app
Test de FastAPI endpoints
"""

import httpx
import asyncio

async def test_api_endpoints():
    """Test API endpoints"""
    print("🌐 Testing API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health check
        print("\n1️⃣ Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check OK: {data}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test 2: Home page
        print("\n2️⃣ Testing home page...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print(f"✅ Home page OK: {len(response.text)} chars")
            else:
                print(f"❌ Home page failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Home page error: {e}")
        
        # Test 3: API status (debug)
        print("\n3️⃣ Testing debug endpoints...")
        try:
            response = await client.get(f"{base_url}/debug/polling")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Debug polling OK: {data}")
            else:
                print(f"❌ Debug polling failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Debug polling error: {e}")
        
        # Test 4: Test connection endpoint (should fail without proper data)
        print("\n4️⃣ Testing connection endpoint (expect error)...")
        try:
            response = await client.post(f"{base_url}/test-connection", data={
                "email": "test@example.com",
                "password": "invalid",
                "imap_server": "invalid.server",
                "imap_port": 993,
                "smtp_server": "invalid.server", 
                "smtp_port": 587,
                "allowed_senders": "test@sender.com",
                "openrouter_api_key": ""
            })
            data = response.json()
            print(f"✅ Connection test responded: {data.get('status')} - {data.get('message', '')[:100]}...")
        except Exception as e:
            print(f"❌ Connection test error: {e}")
    
    print("\n✅ API endpoint tests completed!")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
