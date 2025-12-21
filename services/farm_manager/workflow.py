from langgraph.graph import StateGraph, END
from .state import FarmState
from .nodes import (
    classifier_node,
    crop_agent_node,
    scheme_agent_node,
    combiner_node
)
from .router import router_logic

def create_farm_manager_graph():
    """
    Assembles the LangGraph for the Farm Manager Service.
    Supports classification, parallel execution for BOTH queries, and merging results.
    """
    # Initialize the graph with our state
    workflow = StateGraph(FarmState)
    
    # Add nodes
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("crop_agent", crop_agent_node)
    workflow.add_node("scheme_agent", scheme_agent_node)
    workflow.add_node("combiner", combiner_node)
    
    # Set the entry point
    workflow.set_entry_point("classifier")
    
    # Add conditional edges from classifier
    # If BOTH, it will return ["crop_agent", "scheme_agent"] triggering parallel execution
    workflow.add_conditional_edges(
        "classifier",
        router_logic,
        {
            "crop_agent": "crop_agent",
            "scheme_agent": "scheme_agent",
            "end": "combiner" # Fallback/Neither goes to combiner for generic msg
        }
    )
    
    # Connect parallel/single agents to the combiner
    # LangGraph handles the "fan-in" automatically when multiple edges point to same node
    workflow.add_edge("crop_agent", "combiner")
    workflow.add_edge("scheme_agent", "combiner")
    
    # Connect combiner to END
    workflow.add_edge("combiner", END)
    
    # Compile the graph
    return workflow.compile()

# Singleton instance of the graph
app = create_farm_manager_graph()
