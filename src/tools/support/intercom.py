"""Intercom support tool connector."""

from typing import Any, Dict

from ..base import BaseTool


class IntercomTool(BaseTool):
    """Intercom customer messaging connector."""

    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive Intercom insights.

        Returns:
            Support insights
        """
        insights = {
            "source": "intercom",
            "conversations": self.get_conversations(),
            "sentiment": self.get_sentiment(),
        }
        return insights

    def get_conversations(self) -> Dict[str, Any]:
        """Get conversation data."""
        return self.call_capability("get_conversations")

    def get_sentiment(self) -> Dict[str, Any]:
        """Get customer sentiment."""
        return self.call_capability("get_customer_sentiment")
