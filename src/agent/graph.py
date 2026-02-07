"""LangGraph workflow definition."""

from typing import Dict, Any

from langgraph.graph import StateGraph, END

from ..utils.logger import get_logger
from .state import AgentState
from .nodes import PMAgentNodes

logger = get_logger(__name__)


def create_agent() -> StateGraph:
    """
    Create the PM Agent LangGraph workflow.

    Returns:
        Compiled StateGraph
    """
    logger.info("Creating PM Agent workflow")

    # Initialize nodes
    nodes = PMAgentNodes()

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("query_router", nodes.query_router)
    workflow.add_node("data_collector", nodes.data_collector)
    workflow.add_node("data_processor", nodes.data_processor)
    workflow.add_node("analyzer", nodes.analyzer)
    workflow.add_node("generator", nodes.generator)
    workflow.add_node("reviewer", nodes.reviewer)

    # Define edges
    workflow.set_entry_point("query_router")

    workflow.add_edge("query_router", "data_collector")
    workflow.add_edge("data_collector", "data_processor")
    workflow.add_edge("data_processor", "analyzer")
    workflow.add_edge("analyzer", "generator")
    workflow.add_edge("generator", "reviewer")
    workflow.add_edge("reviewer", END)

    # Compile
    app = workflow.compile()

    logger.info("PM Agent workflow created")
    return app


def run_agent(
    query: str,
    uploaded_files: list[str] = None
) -> Dict[str, Any]:
    """
    Run the PM Agent.

    Args:
        query: User query
        uploaded_files: List of uploaded file paths

    Returns:
        Final agent state with results
    """
    logger.info(f"Running agent with query: {query}")

    # Initialize state
    initial_state: AgentState = {
        "query": query,
        "uploaded_files": uploaded_files or [],
        "analytics_data": None,
        "support_data": None,
        "sales_data": None,
        "pm_data": None,
        "interview_data": None,
        "aggregated_data": None,
        "feature_opportunities": None,
        "scored_features": None,
        "top_feature": None,
        "impact_assessment": None,
        "feature_spec": None,
        "ui_proposals": None,
        "task_breakdown": None,
        "query_type": None,
        "error": None,
        "completed": False,
    }

    # Create and run agent
    app = create_agent()

    try:
        result = app.invoke(initial_state)
        logger.info("Agent execution completed")
        return result

    except Exception as e:
        logger.error(f"Error running agent: {e}")
        return {
            **initial_state,
            "error": str(e),
            "completed": False,
        }
