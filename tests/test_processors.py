"""Tests for data processors."""

import pytest
from src.processors import DocumentParser, AnalyticsProcessor, DataAggregator


def test_analytics_processor():
    """Test analytics data processing."""
    processor = AnalyticsProcessor()

    mock_data = {
        "total_users": 10000,
        "active_users": 7500,
        "retention_rate": 0.75,
        "top_features": [
            {"feature": "Dashboard", "usage": 90},
            {"feature": "Reports", "usage": 65},
        ]
    }

    processed = processor.process_user_metrics(mock_data)

    assert "total_users" in processed
    assert processed["total_users"] == 10000
    assert "top_features" in processed


def test_analytics_patterns():
    """Test pattern identification."""
    processor = AnalyticsProcessor()

    analytics_data = [
        {
            "source": "mixpanel",
            "top_features": [
                {"feature": "Dashboard", "usage": 92},
                {"feature": "Export", "usage": 15},
            ]
        }
    ]

    patterns = processor.identify_patterns(analytics_data)

    assert "high_usage_features" in patterns
    assert "low_usage_features" in patterns
    assert len(patterns["high_usage_features"]) > 0


def test_data_aggregator():
    """Test data aggregation."""
    aggregator = DataAggregator()

    analytics = [{"source": "mixpanel", "user_metrics": {"total_users": 1000}}]
    support = [{"source": "zendesk", "tickets": {"total_tickets": 100}}]
    sales = {"opportunities": {"total_opportunities": 50}}
    pm = [{"source": "jira", "issues": {"total_issues": 200}}]
    interviews = {"total_interviews": 5, "pain_points": ["slow performance"]}

    result = aggregator.aggregate_all(
        analytics_data=analytics,
        support_data=support,
        sales_data=sales,
        pm_data=pm,
        interview_data=interviews
    )

    assert "analytics_summary" in result
    assert "support_summary" in result
    assert "common_themes" in result


def test_theme_extraction():
    """Test common theme extraction."""
    aggregator = DataAggregator()

    interview_data = {
        "pain_points": ["slow export", "mobile issues"],
        "feature_requests": ["bulk export", "mobile redesign"],
        "positive_feedback": ["easy to use"]
    }

    themes = aggregator._extract_themes([], [], {}, interview_data)

    assert "pain_points" in themes
    assert "feature_requests" in themes
    assert len(themes["pain_points"]) > 0
