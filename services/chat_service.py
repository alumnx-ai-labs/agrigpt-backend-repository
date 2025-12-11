import os
from typing import List, Dict, Any, Optional
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorClient


class ChatService:
    """
    Simple Mongo-backed chat storage.
    Conversations are keyed by conversationId and store an email and messages array.
    """

    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.db_name = os.getenv("MONGODB_DB_NAME", "agriculture")
        self.collection_name = os.getenv("MONGODB_CHATS_COLLECTION", "chats")
        self.client = None
        self.collection = None

        if self.mongo_uri:
            self._initialize_client()

    def _initialize_client(self) -> None:
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.collection = self.client[self.db_name][self.collection_name]

    async def get_chats_by_email(self, email: str) -> List[Dict[str, Any]]:
        if not self.mongo_uri:
            raise RuntimeError("MONGODB_URI is not configured")
        if self.client is None or self.collection is None:
            self._initialize_client()

        cursor = self.collection.find({"email": email})
        chats = []
        async for doc in cursor:
            chat_id = str(doc.get("_id"))
            chats.append(
                {
                    "chatId": chat_id,
                    "messages": doc.get("messages", []),
                }
            )
        return chats

    async def create_chat(self, email: str, initial_message: Optional[Dict[str, str]] = None) -> str:
        if not self.mongo_uri:
            raise RuntimeError("MONGODB_URI is not configured")
        if self.client is None or self.collection is None:
            self._initialize_client()

        doc: Dict[str, Any] = {"email": email, "messages": []}
        if initial_message:
            doc["messages"].append(initial_message)

        insert_result = await self.collection.insert_one(doc)
        return str(insert_result.inserted_id)

    async def append_message(
        self, chat_id: str, message_source: str, message: str, email: str
    ) -> str:
        """
        Append a message to an existing chat by chat_id.
        """
        if not self.mongo_uri:
            raise RuntimeError("MONGODB_URI is not configured")
        if self.client is None or self.collection is None:
            self._initialize_client()

        try:
            oid = ObjectId(chat_id)
        except Exception:
            raise RuntimeError("Invalid chatId")

        result = await self.collection.update_one(
            {"_id": oid, "email": email},
            {"$push": {"messages": {"messageSource": message_source, "message": message}}},
        )
        if result.matched_count == 0:
            raise RuntimeError("Chat not found for this email or chatId")
        return chat_id


chat_service = ChatService()

