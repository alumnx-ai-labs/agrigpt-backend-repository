from typing import TypedDict, List, Optional, Dict, Literal, Annotated
import operator

class FarmState(TypedDict):
    """
    State object for the Farm Manager LangGraph.
    """
    # Contract data
    farmerId: str
    messageId: Optional[str]
    query: str
    mediaUrl: Optional[str]
    
    # Internal context
    email: Optional[str]
    history: List[Dict[str, str]]
    
    # Classification results
    classification: Optional[Literal["crop", "scheme", "both", "neither"]]
    crop_query: Optional[str]
    scheme_query: Optional[str]
    reasoning: Optional[str]
    
    # Processing results
    # Using Annotated with operator.ior to merge dictionaries from parallel execution nodes
    answers: Annotated[Dict[str, Optional[str]], operator.ior]
    sources: Annotated[Dict[str, List[str]], operator.ior]
    
    # Final output
    final_response: Optional[str]
