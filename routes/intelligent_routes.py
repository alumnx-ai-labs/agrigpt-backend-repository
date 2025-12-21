from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from services.farm_manager.workflow import app as farm_graph
from services.farmer_service import farmer_service

router = APIRouter()

class FarmerQueryRequest(BaseModel):
    farmerId: str
    messageId: Optional[str] = "none"
    query: str
    mediaUrl: Optional[str] = "none"

class FarmerQueryResponse(BaseModel):
    farmerId: str
    response: str
    sources: Optional[Dict[str, List[str]]] = None

class SaveFarmerDataRequest(BaseModel):
    phone: str
    query: str
    mediaUrl: str
    whether_rate_limited: bool

class SaveFarmerDataResponse(BaseModel):
    farmerId: str
    messageId: str

@router.post("/process-farmer-query", response_model=FarmerQueryResponse)
async def process_farmer_query(request: FarmerQueryRequest):
    """
    Endpoint for Farm Manager Service to process farmer queries using LangGraph.
    Matches the contract: POST /process-farmer-query
    """
    try:
        # Initialize state for LangGraph
        initial_state = {
            "farmerId": request.farmerId,
            "messageId": request.messageId,
            "query": request.query,
            "mediaUrl": request.mediaUrl,
            "email": "farmer@agrigpt.com", # Default or derived
            "history": [], # To be fetched from chat_service in future
            "answers": {},
            "sources": {}
        }
        
        # Invoke the graph
        result = await farm_graph.ainvoke(initial_state)
        
        return FarmerQueryResponse(
            farmerId=result["farmerId"],
            response=result["final_response"],
            sources=result["sources"]
        )
    except Exception as e:
        print(f"❌ Error in Farm Manager: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-farmer-data", response_model=SaveFarmerDataResponse)
async def save_farmer_data(request: SaveFarmerDataRequest):
    """
    Saves farmer information and query status to MongoDB.
    """
    try:
        result = await farmer_service.save_farmer_data(
            phone=request.phone,
            query=request.query,
            media_url=request.mediaUrl,
            rate_limited=request.whether_rate_limited
        )
        return SaveFarmerDataResponse(**result)
    except Exception as e:
        print(f"❌ Error saving farmer data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
