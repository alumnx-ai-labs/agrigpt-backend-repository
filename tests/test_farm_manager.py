import asyncio
from services.farm_manager.workflow import app
from routes.rag_routes import rag_service

async def test_graph():
    # Initialize RAG service because we are running outside main.py
    print("Initializing RAG Service...")
    await rag_service.initialize()
    
    print("\n=== TEST 1: CROP ONLY ===")
    input_1 = {
        "farmerId": "u1",
        "email": "test@v.com",
        "query": "How do I grow oranges?",
        "mediaUrl": "none",
        "history": [],
        "answers": {},
        "sources": {}
    }
    result_1 = await app.ainvoke(input_1)
    print(f"Classification: {result_1['classification']}")
    print(f"Response: {result_1['final_response']}")
    print(f"Sources: {result_1['sources']}")

    print("\n=== TEST 2: SCHEME ONLY ===")
    input_2 = {
        "farmerId": "u1",
        "email": "test@v.com",
        "query": "What subsidies are available for farmers?",
        "mediaUrl": "none",
        "history": [],
        "answers": {},
        "sources": {}
    }
    result_2 = await app.ainvoke(input_2)
    print(f"Classification: {result_2['classification']}")
    print(f"Response: {result_2['final_response']}")

    print("\n=== TEST 3: BOTH (CROP + SCHEME) ===")
    input_3 = {
        "farmerId": "u1",
        "email": "test@v.com",
        "query": "How do I grow oranges and what are the subsidies?",
        "mediaUrl": "none",
        "history": [],
        "answers": {},
        "sources": {}
    }
    result_3 = await app.ainvoke(input_3)
    print(f"Classification: {result_3['classification']}")
    print(f"Crop Query: {result_3.get('crop_query')}")
    print(f"Scheme Query: {result_3.get('scheme_query')}")
    print(f"Final Response:\n{result_3['final_response']}")
    print(f"Sources: {result_3['sources']}")

if __name__ == "__main__":
    asyncio.run(test_graph())
