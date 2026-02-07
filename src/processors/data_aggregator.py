"""Aggregate data from multiple sources."""

from typing import Dict, Any, List

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataAggregator:
    """
    Aggregate and combine data from multiple sources.

    Handles deduplication and cross-referencing of data from:
    - Analytics tools
    - Support tools
    - Sales tools
    - Project management tools
    - Customer interviews
    """

    @staticmethod
    def aggregate_all(
        analytics_data: List[Dict[str, Any]],
        support_data: List[Dict[str, Any]],
        sales_data: Dict[str, Any],
        pm_data: List[Dict[str, Any]],
        interview_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggregate all data sources.

        Args:
            analytics_data: Analytics insights
            support_data: Support insights
            sales_data: Sales insights
            pm_data: Project management insights
            interview_data: Interview insights

        Returns:
            Comprehensive aggregated data
        """
        logger.info("Aggregating data from all sources")

        # Extract common themes
        themes = DataAggregator._extract_themes(
            analytics_data,
            support_data,
            sales_data,
            interview_data
        )

        # Build comprehensive view
        aggregated = {
            "analytics_summary": DataAggregator._summarize_analytics(analytics_data),
            "support_summary": DataAggregator._summarize_support(support_data),
            "sales_summary": DataAggregator._summarize_sales(sales_data),
            "pm_summary": DataAggregator._summarize_pm(pm_data),
            "interview_summary": interview_data,
            "common_themes": themes,
            "cross_references": DataAggregator._find_cross_references(themes),
        }

        logger.info("Data aggregation complete")
        return aggregated

    @staticmethod
    def _summarize_analytics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize analytics data."""
        if not data:
            return {}

        summary = {
            "sources": [d.get("source") for d in data],
            "key_metrics": [],
            "trends": [],
        }

        for item in data:
            if "user_metrics" in item:
                summary["key_metrics"].append(item["user_metrics"])
            if "events" in item:
                summary["trends"].append(item["events"])

        return summary

    @staticmethod
    def _summarize_support(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize support data."""
        if not data:
            return {}

        all_issues = []
        sentiments = []

        for item in data:
            if "tickets" in item and "top_issues" in item["tickets"]:
                all_issues.extend(item["tickets"]["top_issues"])
            if "sentiment" in item:
                sentiments.append(item["sentiment"])

        return {
            "total_sources": len(data),
            "top_issues": sorted(all_issues, key=lambda x: x.get("count", 0), reverse=True)[:10],
            "sentiment_data": sentiments,
        }

    @staticmethod
    def _summarize_sales(data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize sales data."""
        if not data:
            return {}

        return {
            "opportunities": data.get("opportunities", {}),
            "win_loss": data.get("win_loss", {}),
            "customer_feedback": data.get("feedback", []),
        }

    @staticmethod
    def _summarize_pm(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize project management data."""
        if not data:
            return {}

        backlog_items = []
        for item in data:
            if "backlog" in item and "top_priority" in item["backlog"]:
                backlog_items.extend(item["backlog"]["top_priority"])

        return {
            "total_sources": len(data),
            "top_backlog_items": backlog_items,
        }

    @staticmethod
    def _extract_themes(
        analytics_data: List[Dict[str, Any]],
        support_data: List[Dict[str, Any]],
        sales_data: Dict[str, Any],
        interview_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract common themes across all data sources."""
        themes = {
            "pain_points": set(),
            "feature_requests": set(),
            "positive_mentions": set(),
        }

        # From interviews
        if interview_data:
            themes["pain_points"].update(interview_data.get("pain_points", []))
            themes["feature_requests"].update(interview_data.get("feature_requests", []))
            themes["positive_mentions"].update(interview_data.get("positive_feedback", []))

        # From support
        for item in support_data:
            if "tickets" in item and "top_issues" in item["tickets"]:
                for issue in item["tickets"]["top_issues"]:
                    themes["pain_points"].add(issue.get("issue", ""))

        # From sales
        if sales_data and "win_loss" in sales_data:
            loss_reasons = sales_data["win_loss"].get("loss_reasons", [])
            themes["pain_points"].update(loss_reasons)

        # Convert sets to lists
        return {
            "pain_points": list(themes["pain_points"])[:20],
            "feature_requests": list(themes["feature_requests"])[:20],
            "positive_mentions": list(themes["positive_mentions"])[:20],
        }

    @staticmethod
    def _find_cross_references(themes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find items mentioned across multiple sources."""
        # This would use more sophisticated matching in production
        # For now, just flag items that appear in multiple categories
        cross_refs = []

        pain_points = set([p.lower() for p in themes.get("pain_points", [])])
        feature_requests = set([f.lower() for f in themes.get("feature_requests", [])])

        # Find pain points that have corresponding feature requests
        for pain in themes.get("pain_points", []):
            pain_lower = pain.lower()
            # Simple keyword matching
            for request in themes.get("feature_requests", []):
                if any(word in request.lower() for word in pain_lower.split() if len(word) > 4):
                    cross_refs.append({
                        "pain_point": pain,
                        "related_request": request,
                        "confidence": "medium"
                    })

        return cross_refs[:10]  # Top 10 cross-references
