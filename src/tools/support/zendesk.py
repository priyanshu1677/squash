"""Zendesk support tool connector."""

from typing import Any, Dict

from ..base import BaseTool


class ZendeskTool(BaseTool):
    """Zendesk customer support connector."""

    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive Zendesk insights.

        Returns:
            Support insights
        """
        insights = {
            "source": "zendesk",
            "tickets": self.get_tickets(),
            "metrics": self.get_metrics(),
        }
        return insights

    def get_tickets(self) -> Dict[str, Any]:
        """Get ticket data."""
        return self.call_capability("get_tickets")

    def get_metrics(self) -> Dict[str, Any]:
        """Get ticket metrics."""
        return self.call_capability("get_ticket_metrics")

    def search_issues(self, query: str) -> Dict[str, Any]:
        """Search for specific issues."""
        return self.call_capability("search_tickets", {"query": query})
