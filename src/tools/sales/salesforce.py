"""Salesforce CRM tool connector."""

from typing import Any, Dict

from ..base import BaseTool


class SalesforceTool(BaseTool):
    """Salesforce CRM connector."""

    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive Salesforce insights.

        Returns:
            Sales insights
        """
        insights = {
            "source": "salesforce",
            "opportunities": self.get_opportunities(),
            "win_loss": self.get_win_loss_analysis(),
            "feedback": self.get_customer_feedback(),
        }
        return insights

    def get_opportunities(self) -> Dict[str, Any]:
        """Get opportunity data."""
        return self.call_capability("get_opportunities")

    def get_win_loss_analysis(self) -> Dict[str, Any]:
        """Get win/loss reasons."""
        return self.call_capability("get_win_loss_reasons")

    def get_customer_feedback(self) -> Dict[str, Any]:
        """Get customer feedback from sales."""
        return self.call_capability("get_customer_feedback")
