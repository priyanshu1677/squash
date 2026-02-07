"""Tests for MCP tool connectors."""

import pytest
from src.mcp.server_manager import MCPServerManager
from src.tools.analytics import MixpanelTool, PostHogTool
from src.tools.support import ZendeskTool, IntercomTool
from src.tools.sales import SalesforceTool
from src.tools.project_management import JiraTool, ConfluenceTool


@pytest.fixture
def mcp_manager():
    """Create MCP server manager."""
    return MCPServerManager()


def test_mcp_manager_initialization(mcp_manager):
    """Test that MCP manager initializes with mock servers."""
    assert mcp_manager is not None
    servers = mcp_manager.get_all_server_info()
    assert len(servers) > 0


def test_mixpanel_tool(mcp_manager):
    """Test Mixpanel tool connector."""
    client = mcp_manager.get_server("mixpanel")
    assert client is not None

    tool = MixpanelTool(client)
    insights = tool.get_insights()

    assert "source" in insights
    assert insights["source"] == "mixpanel"
    assert "user_metrics" in insights


def test_zendesk_tool(mcp_manager):
    """Test Zendesk tool connector."""
    client = mcp_manager.get_server("zendesk")
    assert client is not None

    tool = ZendeskTool(client)
    insights = tool.get_insights()

    assert "source" in insights
    assert insights["source"] == "zendesk"
    assert "tickets" in insights


def test_salesforce_tool(mcp_manager):
    """Test Salesforce tool connector."""
    client = mcp_manager.get_server("salesforce")
    assert client is not None

    tool = SalesforceTool(client)
    insights = tool.get_insights()

    assert "source" in insights
    assert insights["source"] == "salesforce"
    assert "opportunities" in insights


def test_jira_tool(mcp_manager):
    """Test Jira tool connector."""
    client = mcp_manager.get_server("jira")
    assert client is not None

    tool = JiraTool(client)
    insights = tool.get_insights()

    assert "source" in insights
    assert insights["source"] == "jira"
    assert "issues" in insights


def test_mock_server_capabilities(mcp_manager):
    """Test that mock servers have correct capabilities."""
    mixpanel_client = mcp_manager.get_server("mixpanel")
    capabilities = mixpanel_client.list_capabilities()

    assert "query_events" in capabilities
    assert "get_user_metrics" in capabilities
