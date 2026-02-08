"""Mixpanel analytics tool connector."""

import os
from datetime import datetime, timedelta
from typing import Any, Dict

from ..base import BaseTool


# Default project ID from env, fallback to config
_PROJECT_ID = int(os.environ.get("MIXPANEL_PROJECT_ID", "0"))


def _default_dates(days_back: int = 30) -> tuple[str, str]:
    """Return (from_date, to_date) strings for the last N days."""
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    return from_date, to_date


class MixpanelTool(BaseTool):
    """Mixpanel product analytics connector."""

    def __init__(self, mcp_client):
        super().__init__(mcp_client)
        self.project_id = _PROJECT_ID

    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive Mixpanel insights.

        Returns:
            Analytics insights
        """
        insights = {
            "source": "mixpanel",
            "events": self.get_events(),
            "user_metrics": self.get_user_metrics(),
            "funnel": self.get_funnel_data(),
            "retention": self.get_retention(),
        }
        return insights

    def get_events(self) -> Dict[str, Any]:
        """Get list of event names."""
        return self.call_capability("get_events", {
            "project_id": self.project_id,
        })

    def get_user_metrics(self) -> Dict[str, Any]:
        """Get user metrics via segmentation query on a key event."""
        from_date, to_date = _default_dates(30)
        return self.call_capability("query_events", {
            "project_id": self.project_id,
            "event": "Login Completed",
            "from_date": from_date,
            "to_date": to_date,
            "unit": "week",
        })

    def get_funnel_data(self) -> Dict[str, Any]:
        """Get funnel analysis."""
        from_date, to_date = _default_dates(30)
        return self.call_capability("get_funnel_data", {
            "project_id": self.project_id,
            "from_date": from_date,
            "to_date": to_date,
            "events": '[{"event": "Page Viewed"}, {"event": "Sign Up Started"}, {"event": "Sign Up Completed"}]',
        })

    def get_retention(self) -> Dict[str, Any]:
        """Get retention data."""
        from_date, to_date = _default_dates(30)
        return self.call_capability("get_retention_data", {
            "project_id": self.project_id,
            "event": "Login Completed",
            "born_event": "Sign Up Completed",
            "from_date": from_date,
            "to_date": to_date,
            "retention_type": "birth",
            "unit": "week",
        })
