"""Confluence documentation tool connector."""

from typing import Any, Dict

from ..base import BaseTool


class ConfluenceTool(BaseTool):
    """Confluence documentation connector."""

    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive Confluence insights.

        Returns:
            Documentation insights
        """
        insights = {
            "source": "confluence",
            "requirements": self.get_requirements(),
        }
        return insights

    def get_requirements(self) -> Dict[str, Any]:
        """Get product requirements."""
        return self.call_capability("get_requirements")

    def search(self, query: str) -> Dict[str, Any]:
        """Search documentation."""
        return self.call_capability("search_pages", {"query": query})
