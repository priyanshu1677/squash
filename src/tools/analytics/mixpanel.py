"""Mixpanel analytics tool connector."""

from typing import Any, Dict

from ..base import BaseTool


class MixpanelTool(BaseTool):
    """Mixpanel product analytics connector."""

    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive Mixpanel insights.

        Returns:
            Analytics insights
        """
        insights = {
            "source": "mixpanel",
            "user_metrics": self.get_user_metrics(),
            "events": self.get_events(),
            "funnel": self.get_funnel_data(),
            "retention": self.get_retention(),
        }
        return insights

    def get_user_metrics(self) -> Dict[str, Any]:
        """Get user metrics."""
        return self.call_capability("get_user_metrics")

    def get_events(self) -> Dict[str, Any]:
        """Get event data."""
        return self.call_capability("query_events")

    def get_funnel_data(self) -> Dict[str, Any]:
        """Get funnel analysis."""
        return self.call_capability("get_funnel_data")

    def get_retention(self) -> Dict[str, Any]:
        """Get retention data."""
        return self.call_capability("get_retention_data")
