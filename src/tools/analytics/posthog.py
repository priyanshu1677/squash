"""PostHog analytics tool connector."""

from typing import Any, Dict

from ..base import BaseTool


class PostHogTool(BaseTool):
    """PostHog product analytics connector."""

    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive PostHog insights.

        Returns:
            Analytics insights
        """
        insights = {
            "source": "posthog",
            "events": self.get_events(),
            "feature_flags": self.get_feature_flags(),
        }
        return insights

    def get_events(self) -> Dict[str, Any]:
        """Get event data."""
        return self.call_capability("query_events")

    def get_feature_flags(self) -> Dict[str, Any]:
        """Get feature flag data."""
        return self.call_capability("get_feature_flags")
