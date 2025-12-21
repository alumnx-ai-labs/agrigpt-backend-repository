from .state import FarmState
from typing import Literal, List

def router_logic(state: FarmState) -> List[str]:
    """
    Determines which nodes to execute based on classification.
    Returns a list of node names to support parallel execution for 'both'.
    """
    classification = state["classification"]
    
    if classification == "both":
        return ["crop_agent", "scheme_agent"]
    elif classification == "crop":
        return ["crop_agent"]
    elif classification == "scheme":
        return ["scheme_agent"]
    else:
        return ["end"]
