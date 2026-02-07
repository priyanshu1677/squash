"""Tests for LangGraph agent."""

import pytest
from src.agent import run_agent, AgentState


def test_agent_initialization():
    """Test that agent can be created without errors."""
    from src.agent.graph import create_agent
    agent = create_agent()
    assert agent is not None


def test_agent_query_basic():
    """Test basic agent query execution."""
    result = run_agent("What are the top pain points?", uploaded_files=[])

    assert result is not None
    assert "query" in result
    assert "completed" in result
    # Agent should complete without errors (may have limited results with mock data)


def test_agent_state_initialization():
    """Test agent state structure."""
    state: AgentState = {
        "query": "test query",
        "uploaded_files": [],
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

    assert state["query"] == "test query"
    assert state["completed"] is False
