"""Jira project management tool connector."""

from typing import Any, Dict

from ..base import BaseTool


class JiraTool(BaseTool):
    """Jira issue tracking connector."""

    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive Jira insights.

        Returns:
            Project management insights
        """
        insights = {
            "source": "jira",
            "issues": self.get_issues(),
            "sprint": self.get_sprint_data(),
            "backlog": self.get_backlog(),
        }
        return insights

    def get_issues(self) -> Dict[str, Any]:
        """Get issue data."""
        return self.call_capability("get_issues")

    def get_sprint_data(self) -> Dict[str, Any]:
        """Get sprint information."""
        return self.call_capability("get_sprint_data")

    def get_backlog(self) -> Dict[str, Any]:
        """Get backlog items."""
        return self.call_capability("get_backlog")
