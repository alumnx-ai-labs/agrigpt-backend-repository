from .state import FarmState
from routes.rag_routes import rag_service
from langchain_core.messages import HumanMessage, SystemMessage
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

async def classifier_node(state: FarmState) -> FarmState:
    """
    Classifies the user query into crop, scheme, both, or neither using LLM.
    """
    query = state["query"]
    
    system_prompt = (
        "You are an intelligent classifier for an agricultural assistant. "
        "Classify the user query into one of these categories:\n"
        "1. 'crop': Questions about growing crops, pests, diseases, or general farming techniques.\n"
        "2. 'scheme': Questions about government agricultural schemes, subsidies, or policies.\n"
        "3. 'both': If the query contains elements of both crops and schemes.\n"
        "4. 'neither': If the query is off-topic or irrelevant to agriculture.\n\n"
        "If the category is 'both', you MUST provide two separate sub-queries:\n"
        "- 'crop_query': Focused purely on the crop aspect.\n"
        "- 'scheme_query': Focused purely on the scheme aspect.\n\n"
        "Output ONLY a JSON object with keys: 'classification', 'crop_query', 'scheme_query', and 'reasoning'."
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Query: {query}")
    ]
    
    try:
        response = await rag_service.llm.ainvoke(messages)
        # Attempt to parse JSON from the response
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        state["classification"] = result.get("classification", "neither")
        state["crop_query"] = result.get("crop_query")
        state["scheme_query"] = result.get("scheme_query")
        state["reasoning"] = result.get("reasoning")
        
    except Exception as e:
        logger.error(f"❌ Classification LLM failed: {e}")
        # Fallback to simple logic (existing mock logic as fallback)
        state["classification"] = "neither"
        if "scheme" in query.lower(): state["classification"] = "scheme"
        if "crop" in query.lower() or "grow" in query.lower():
            state["classification"] = "both" if state["classification"] == "scheme" else "crop"
            
    return state

async def crop_agent_node(state: FarmState) -> dict:
    """
    RAG Agent for crop-related queries using the real RAG service.
    """
    query = state.get("crop_query") or state["query"]
    logger.info(f"--- EXECUTING CROP AGENT: {query} ---")
    
    try:
        answer, sources = await rag_service.query(query, "citrus", state.get("history", []))
        return {
            "answers": {"crop": answer},
            "sources": {"crop": sources}
        }
    except Exception as e:
        logger.error(f"❌ Crop Agent Error: {e}")
        return {
            "answers": {"crop": "Sorry, I encountered an error while searching for crop information."},
            "sources": {"crop": []}
        }

async def scheme_agent_node(state: FarmState) -> dict:
    """
    RAG Agent for government scheme queries using the real RAG service.
    """
    query = state.get("scheme_query") or state["query"]
    logger.info(f"--- EXECUTING SCHEME AGENT: {query} ---")
    
    try:
        answer, sources = await rag_service.query(query, "schemes", state.get("history", []))
        return {
            "answers": {"scheme": answer},
            "sources": {"scheme": sources}
        }
    except Exception as e:
        logger.error(f"❌ Scheme Agent Error: {e}")
        return {
            "answers": {"scheme": "Sorry, I encountered an error while searching for scheme information."},
            "sources": {"scheme": []}
        }

async def combiner_node(state: FarmState) -> dict:
    """
    Merges results from both agents into a final cohesive response using LLM.
    """
    classification = state["classification"]
    answers = state.get("answers", {})
    
    if classification == "neither":
        return {"final_response": "I'm sorry, I can only help with questions related to crop cultivation and government agricultural schemes."}
    
    if classification != "both":
        # If only one agent responded, return that answer directly
        ans = answers.get("crop") or answers.get("scheme")
        return {"final_response": ans}

    # If 'both', use LLM to combine them nicely
    crop_ans = answers.get("crop", "Information not found.")
    scheme_ans = answers.get("scheme", "Information not found.")
    
    system_prompt = (
        "You are a helpful agricultural assistant. You have been given two separate answers to a farmer's query: "
        "one about crop cultivation and one about government schemes. "
        "Your job is to merge them into a single, cohesive, and friendly response. "
        "Use markdown for better readability. Ensure the tone is helpful and encouraging."
    )
    
    user_msg = (
        f"Original Query: {state['query']}\n\n"
        f"Crop Information: {crop_ans}\n\n"
        f"Scheme Information: {scheme_ans}"
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ]
    
    try:
        response = await rag_service.llm.ainvoke(messages)
        return {"final_response": response.content}
    except Exception as e:
        logger.error(f"❌ Combiner LLM failed: {e}")
        # Manual fallback
        final_response = (
            f"### Regarding Crop Cultivation\n{crop_ans}\n\n"
            f"### Regarding Government Schemes\n{scheme_ans}"
        )
        return {"final_response": final_response}
