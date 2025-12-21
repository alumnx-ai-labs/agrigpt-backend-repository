import os
from typing import Dict, Any, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

class FarmerService:
    """
    Service for managing farmer data and query logs in MongoDB.
    """
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.db_name = os.getenv("MONGODB_DB_NAME", "agriculture")
        self.farmer_collection_name = os.getenv("MONGODB_FARMER_COLLECTION", "farmer")
        self.queries_collection_name = os.getenv("MONGODB_QUERIES_COLLECTION", "farmer-queries")
        
        self.client = None
        self.db = None
        
        if self.mongo_uri:
            self._initialize_client()

    def _initialize_client(self) -> None:
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.db_name]

    async def save_farmer_data(self, phone: str, query: str, media_url: str, rate_limited: bool) -> Dict[str, str]:
        """
        Saves farmer data to 'farmer' and log the query to 'farmer-queries'.
        """
        if not self.mongo_uri:
            raise RuntimeError("MONGODB_URI is not configured")
        if self.db is None:
            self._initialize_client()

        # 1. Update/Upsert farmer record
        farmer_result = await self.db[self.farmer_collection_name].update_one(
            {"phone": phone},
            {"$set": {"phone": phone, "last_query": query}},
            upsert=True
        )
        
        # Get farmerId (from upsert or existing)
        farmer_doc = await self.db[self.farmer_collection_name].find_one({"phone": phone})
        farmer_id = str(farmer_doc["_id"])

        # 2. Log the query
        query_doc = {
            "farmerId": farmer_doc["_id"],
            "phone": phone,
            "query": query,
            "mediaUrl": media_url,
            "status": "rejected" if rate_limited else "accepted",
            "timestamp": ObjectId().generation_time
        }
        query_result = await self.db[self.queries_collection_name].insert_one(query_doc)
        message_id = str(query_result.inserted_id)

        return {
            "farmerId": farmer_id,
            "messageId": message_id
        }

farmer_service = FarmerService()
