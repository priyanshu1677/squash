"""Agent state schema for LangGraph."""

from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """
    State for the PM Agent workflow.

    This state is passed between nodes and accumulates information
    throughout the agent's execution.
    """

    # Input
    query: str
    uploaded_files: List[str]

    # Data collection
    analytics_data: Optional[List[Dict[str, Any]]]
    support_data: Optional[List[Dict[str, Any]]]
    sales_data: Optional[Dict[str, Any]]
    pm_data: Optional[List[Dict[str, Any]]]
    interview_data: Optional[Dict[str, Any]]

    # Processing
    aggregated_data: Optional[Dict[str, Any]]

    # Analysis
    feature_opportunities: Optional[List[Dict[str, Any]]]
    scored_features: Optional[List[Dict[str, Any]]]
    top_feature: Optional[Dict[str, Any]]
    impact_assessment: Optional[Dict[str, Any]]

    # Generation
    feature_spec: Optional[Dict[str, Any]]
    ui_proposals: Optional[Dict[str, Any]]
    task_breakdown: Optional[Dict[str, Any]]

    # Control flow
    query_type: Optional[str]  # "feature_discovery", "analysis", "task_breakdown"
    error: Optional[str]
    completed: bool
