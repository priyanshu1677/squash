"""Mock MCP servers for prototype testing."""

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MockMCPServer:
    """Base class for mock MCP servers."""

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        self.name = server_name
        self.config = server_config
        self.capabilities = server_config.get("capabilities", [])
        logger.info(f"Initialized mock MCP server: {self.name}")

    def call_tool(self, capability: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool capability on the mock server.

        Args:
            capability: Tool capability name
            params: Tool parameters

        Returns:
            Mock response data
        """
        if capability not in self.capabilities:
            raise ValueError(f"Capability {capability} not supported by {self.name}")

        # Route to appropriate mock method
        method_name = f"mock_{capability}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(params)
        else:
            return {"error": f"Mock method {method_name} not implemented"}


class MockMixpanelServer(MockMCPServer):
    """Mock Mixpanel analytics server."""

    def mock_query_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock event query."""
        return {
            "events": [
                {"name": "feature_used", "count": 1250, "trend": "+15%"},
                {"name": "page_view", "count": 5600, "trend": "+8%"},
                {"name": "button_clicked", "count": 3200, "trend": "-3%"},
                {"name": "form_submitted", "count": 890, "trend": "+22%"},
            ],
            "date_range": "last_30_days"
        }

    def mock_get_user_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock user metrics."""
        return {
            "total_users": 12500,
            "active_users": 8400,
            "retention_rate": 0.67,
            "avg_session_duration": "8m 23s",
            "top_features": [
                {"feature": "Dashboard", "usage": 92},
                {"feature": "Reports", "usage": 78},
                {"feature": "Settings", "usage": 45},
            ]
        }

    def mock_get_funnel_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock funnel data."""
        return {
            "funnel_name": "User Onboarding",
            "steps": [
                {"step": "Sign Up", "users": 1000, "conversion": 100},
                {"step": "Email Verification", "users": 850, "conversion": 85},
                {"step": "Profile Setup", "users": 720, "conversion": 72},
                {"step": "First Action", "users": 580, "conversion": 58},
            ],
            "bottleneck": "Profile Setup - 15% drop-off"
        }

    def mock_get_retention_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock retention data."""
        return {
            "cohort": "January 2024",
            "retention": {
                "day_1": 0.85,
                "day_7": 0.62,
                "day_30": 0.45,
                "day_90": 0.38,
            },
            "churn_reasons": [
                "Missing key features",
                "UI complexity",
                "Performance issues"
            ]
        }


class MockPostHogServer(MockMCPServer):
    """Mock PostHog analytics server."""

    def mock_query_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock event query."""
        return {
            "events": [
                {"event": "feature_interaction", "count": 2100},
                {"event": "error_occurred", "count": 45},
                {"event": "page_load", "count": 8900},
            ]
        }

    def mock_get_feature_flags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock feature flags."""
        return {
            "flags": [
                {"name": "new_dashboard", "enabled": True, "rollout": 50},
                {"name": "beta_feature", "enabled": True, "rollout": 10},
                {"name": "dark_mode", "enabled": True, "rollout": 100},
            ]
        }


class MockZendeskServer(MockMCPServer):
    """Mock Zendesk support server."""

    def mock_get_tickets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock ticket data."""
        return {
            "total_tickets": 456,
            "open_tickets": 123,
            "avg_resolution_time": "4.2 hours",
            "satisfaction_score": 4.2,
            "recent_tickets": [
                {"id": 1001, "subject": "Can't export data", "priority": "high", "status": "open"},
                {"id": 1002, "subject": "Feature request: bulk actions", "priority": "medium", "status": "pending"},
                {"id": 1003, "subject": "UI bug on mobile", "priority": "high", "status": "open"},
            ]
        }

    def mock_search_tickets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock ticket search."""
        return {
            "results": [
                {"id": 1004, "subject": "Export functionality broken", "tags": ["export", "bug"]},
                {"id": 1005, "subject": "Need better export options", "tags": ["export", "feature-request"]},
            ]
        }

    def mock_get_ticket_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock ticket metrics."""
        return {
            "top_issues": [
                {"issue": "Data export problems", "count": 67},
                {"issue": "Mobile UI issues", "count": 45},
                {"issue": "Performance slowness", "count": 38},
                {"issue": "Search not working", "count": 29},
            ],
            "trend": "Export issues increased 40% this month"
        }


class MockIntercomServer(MockMCPServer):
    """Mock Intercom support server."""

    def mock_get_conversations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock conversations."""
        return {
            "total_conversations": 234,
            "avg_response_time": "2.1 hours",
            "topics": [
                {"topic": "Feature requests", "count": 89},
                {"topic": "Bug reports", "count": 67},
                {"topic": "How-to questions", "count": 78},
            ]
        }

    def mock_get_customer_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock sentiment analysis."""
        return {
            "overall_sentiment": "positive",
            "positive": 62,
            "neutral": 28,
            "negative": 10,
            "common_praise": [
                "Easy to use",
                "Great support team",
                "Powerful features"
            ],
            "common_complaints": [
                "Missing export feature",
                "Mobile app needs work",
                "Slow performance on large datasets"
            ]
        }


class MockSalesforceServer(MockMCPServer):
    """Mock Salesforce CRM server."""

    def mock_get_opportunities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock opportunities."""
        return {
            "total_opportunities": 89,
            "total_value": "$2.3M",
            "win_rate": 0.34,
            "avg_deal_size": "$25,800",
            "top_opportunities": [
                {"account": "TechCorp", "value": "$120K", "stage": "Negotiation", "probability": 75},
                {"account": "RetailCo", "value": "$85K", "stage": "Proposal", "probability": 60},
            ]
        }

    def mock_get_win_loss_reasons(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock win/loss analysis."""
        return {
            "win_reasons": [
                "Better features than competitors",
                "Strong customer support",
                "Competitive pricing"
            ],
            "loss_reasons": [
                "Missing key integrations",
                "Too expensive",
                "Competitor had better mobile app",
                "Lacking advanced analytics"
            ]
        }

    def mock_get_customer_feedback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock customer feedback."""
        return {
            "feedback": [
                {"account": "TechCorp", "comment": "Love the product but need better export options", "sentiment": "positive"},
                {"account": "StartupXYZ", "comment": "Mobile experience needs improvement", "sentiment": "neutral"},
                {"account": "Enterprise Inc", "comment": "Would pay more for advanced analytics", "sentiment": "positive"},
            ]
        }


class MockJiraServer(MockMCPServer):
    """Mock Jira project management server."""

    def mock_get_issues(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock issues."""
        return {
            "total_issues": 234,
            "open_issues": 89,
            "in_progress": 45,
            "by_type": {
                "bug": 67,
                "feature": 112,
                "improvement": 55
            }
        }

    def mock_get_sprint_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock sprint data."""
        return {
            "current_sprint": "Sprint 24",
            "points_committed": 45,
            "points_completed": 38,
            "velocity": 42,
            "burndown_status": "On track"
        }

    def mock_get_backlog(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock backlog."""
        return {
            "total_items": 156,
            "top_priority": [
                {"key": "PROD-123", "summary": "Add bulk export feature", "priority": "High", "votes": 23},
                {"key": "PROD-124", "summary": "Improve mobile UI", "priority": "High", "votes": 18},
                {"key": "PROD-125", "summary": "Performance optimization", "priority": "Medium", "votes": 12},
            ]
        }


class MockConfluenceServer(MockMCPServer):
    """Mock Confluence documentation server."""

    def mock_search_pages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock page search."""
        return {
            "results": [
                {"title": "Q1 Product Roadmap", "url": "/roadmap-q1"},
                {"title": "User Research Summary", "url": "/research-summary"},
                {"title": "Feature Requests Log", "url": "/feature-requests"},
            ]
        }

    def mock_get_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock requirements."""
        return {
            "requirements": [
                {"id": "REQ-001", "title": "Data Export Feature", "status": "Approved"},
                {"id": "REQ-002", "title": "Mobile App Redesign", "status": "In Review"},
                {"id": "REQ-003", "title": "Advanced Analytics", "status": "Draft"},
            ]
        }


# Factory to create appropriate mock server
def create_mock_server(server_name: str, server_config: Dict[str, Any]) -> MockMCPServer:
    """
    Create appropriate mock server based on server name.

    Args:
        server_name: Name of the server
        server_config: Server configuration

    Returns:
        Mock server instance
    """
    server_map = {
        "mixpanel": MockMixpanelServer,
        "posthog": MockPostHogServer,
        "zendesk": MockZendeskServer,
        "intercom": MockIntercomServer,
        "salesforce": MockSalesforceServer,
        "jira": MockJiraServer,
        "confluence": MockConfluenceServer,
    }

    server_class = server_map.get(server_name, MockMCPServer)
    return server_class(server_name, server_config)
