"""Process analytics data from multiple sources."""

from typing import Dict, Any, List

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsProcessor:
    """
    Process and normalize analytics data from various sources.

    Handles data from Mixpanel, PostHog, and other analytics tools.
    """

    @staticmethod
    def process_user_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user metrics data.

        Args:
            data: Raw user metrics

        Returns:
            Normalized metrics
        """
        return {
            "total_users": data.get("total_users", 0),
            "active_users": data.get("active_users", 0),
            "retention_rate": data.get("retention_rate", 0),
            "engagement_score": data.get("avg_session_duration", "N/A"),
            "top_features": data.get("top_features", []),
        }

    @staticmethod
    def process_events(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process event data.

        Args:
            data: Raw event data

        Returns:
            Normalized events
        """
        events = data.get("events", [])
        return {
            "total_events": len(events),
            "events": events,
            "trending_up": [e for e in events if "+" in str(e.get("trend", ""))],
            "trending_down": [e for e in events if "-" in str(e.get("trend", ""))],
        }

    @staticmethod
    def process_funnel(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process funnel data.

        Args:
            data: Raw funnel data

        Returns:
            Normalized funnel analysis
        """
        steps = data.get("steps", [])
        if not steps:
            return {"error": "No funnel data"}

        # Calculate drop-offs
        drop_offs = []
        for i in range(len(steps) - 1):
            current = steps[i].get("conversion", 0)
            next_step = steps[i + 1].get("conversion", 0)
            drop_off = current - next_step
            drop_offs.append({
                "from": steps[i].get("step"),
                "to": steps[i + 1].get("step"),
                "drop_off_rate": drop_off,
            })

        return {
            "funnel_name": data.get("funnel_name"),
            "total_steps": len(steps),
            "overall_conversion": steps[-1].get("conversion", 0) if steps else 0,
            "bottleneck": data.get("bottleneck"),
            "drop_offs": drop_offs,
        }

    @staticmethod
    def identify_patterns(analytics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify patterns across multiple analytics sources.

        Args:
            analytics_data: List of analytics data from different sources

        Returns:
            Identified patterns and insights
        """
        patterns = {
            "high_usage_features": [],
            "low_usage_features": [],
            "bottlenecks": [],
            "opportunities": [],
        }

        for data in analytics_data:
            source = data.get("source", "unknown")

            # Extract feature usage
            if "top_features" in data:
                for feature in data["top_features"]:
                    if feature.get("usage", 0) > 70:
                        patterns["high_usage_features"].append(feature)
                    elif feature.get("usage", 0) < 30:
                        patterns["low_usage_features"].append(feature)

            # Extract bottlenecks
            if "bottleneck" in data and data["bottleneck"]:
                patterns["bottlenecks"].append({
                    "source": source,
                    "bottleneck": data["bottleneck"]
                })

        logger.info(f"Identified {len(patterns['bottlenecks'])} bottlenecks")
        return patterns
