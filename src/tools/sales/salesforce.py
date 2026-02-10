"""Salesforce CRM tool connector."""

from typing import Any, Dict

from ..base import BaseTool

# Salesforce MCP org alias (set during sf org login)
SF_ORG = "rithenofficial01-p4d0@force.com"
SF_DIR = "/Users/rithen/RAM/squash"


class SalesforceTool(BaseTool):
    """Salesforce CRM connector."""

    def _soql(self, query: str) -> Dict[str, Any]:
        """Run a SOQL query via the Salesforce MCP tool."""
        return self.call_capability("get_opportunities", {
            "query": query,
            "usernameOrAlias": SF_ORG,
            "directory": SF_DIR,
        })

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
        return self._soql(
            "SELECT Id, Name, Amount, StageName, Probability, Account.Name, CloseDate "
            "FROM Opportunity WHERE IsClosed = false ORDER BY Amount DESC LIMIT 20"
        )

    def get_win_loss_analysis(self) -> Dict[str, Any]:
        """Get win/loss reasons."""
        return self._soql(
            "SELECT Id, Name, Amount, StageName, Account.Name, CloseDate "
            "FROM Opportunity WHERE IsClosed = true AND CloseDate = THIS_YEAR "
            "ORDER BY CloseDate DESC LIMIT 20"
        )

    def get_customer_feedback(self) -> Dict[str, Any]:
        """Get customer feedback from cases."""
        return self._soql(
            "SELECT Id, Subject, Description, Status, Priority, Account.Name "
            "FROM Case WHERE Status != 'Closed' ORDER BY CreatedDate DESC LIMIT 20"
        )
