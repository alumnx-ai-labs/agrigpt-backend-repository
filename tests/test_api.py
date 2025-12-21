import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000" # Update port if running on 8005

async def test_endpoints():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        print("\n🚀 Testing /save-farmer-data...")
        save_payload = {
            "phone": "9876543210",
            "query": "How do I get subsidies for oranges?",
            "mediaUrl": "none",
            "whether_rate_limited": False
        }
        try:
            resp = await client.post("/process-farmer-query", json=save_payload) # Using the router path
            # Wait, the route is actually in the intelligent_router. 
            # If main.py says app.include_router(intelligent_router), then it's at root.
            
            # Let's try the save endpoint
            resp = await client.post("/save-farmer-data", json=save_payload)
            print(f"Status: {resp.status_code}")
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Save Failed (Is the server running?): {e}")

        print("\n🚀 Testing /process-farmer-query...")
        query_payload = {
            "farmerId": "some_id",
            "messageId": "msg_001",
            "query": "I want to grow rice and know about help.",
            "mediaUrl": "none"
        }
        try:
            resp = await client.post("/process-farmer-query", json=query_payload)
            print(f"Status: {resp.status_code}")
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Query Failed: {e}")

if __name__ == "__main__":
    print("🔔 Ensure your server is running (uvicorn main:app --reload) before running this test.")
    asyncio.run(test_endpoints())
