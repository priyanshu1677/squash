"""Analyze aggregated data to identify feature opportunities."""

import json
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FeatureAnalyzer:
    """
    Analyze data to identify feature opportunities.

    Uses LLM to analyze aggregated data and suggest features
    based on customer feedback, usage patterns, and business goals.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="o3-mini",
            api_key=config.openai_api_key,
        )

    def analyze(self, aggregated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze aggregated data to identify feature opportunities.

        Args:
            aggregated_data: Data from all sources

        Returns:
            List of feature opportunities
        """
        logger.info("Analyzing data for feature opportunities")

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior product manager using Squash, an AI-powered PM platform. Your job is to analyze cross-functional data and identify the highest-impact feature opportunities.

You will receive aggregated data from multiple sources:
- Analytics (Mixpanel/PostHog): usage patterns, drop-offs, feature adoption
- Support (Zendesk/Intercom): customer complaints, ticket themes, sentiment
- Sales (Salesforce): win/loss reasons, prospect feedback, pipeline signals
- Interviews: customer pain points, feature requests, direct quotes
- PM tools (Jira/Confluence): backlog state, sprint velocity, existing requirements

Analyze this data to identify the top 5-7 feature opportunities. For each, reason through:
1. What recurring signals point to this need across multiple data sources?
2. How many users/customers would benefit and how severely are they impacted?
3. What specific evidence supports building this?

Return ONLY valid JSON (no markdown fences, no commentary):
{{
  "opportunities": [
    {{
      "name": "Short feature name",
      "description": "2-3 sentence description of the feature and what problem it solves",
      "justification": "Why this feature matters, grounded in the data",
      "evidence": ["specific data point or quote 1", "metric or signal 2", "customer quote 3"],
      "expected_impact": "Concrete expected outcomes (e.g. reduce churn by X%, improve onboarding completion)",
      "confidence": "high/medium/low based on strength and consistency of evidence"
    }}
  ]
}}"""),
            ("user", "Data to analyze:\n\n{data}")
        ])

        try:
            chain = prompt | self.llm
            response = chain.invoke({"data": json.dumps(aggregated_data, indent=2)})

            # Parse JSON response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            opportunities = result.get("opportunities", [])

            logger.info(f"Identified {len(opportunities)} feature opportunities")
            return opportunities

        except Exception as e:
            logger.error(f"Error analyzing features: {e}")
            return [{
                "name": "Error",
                "description": "Failed to analyze features",
                "justification": str(e),
                "evidence": [],
                "expected_impact": "N/A",
                "confidence": "low"
            }]

    def rank_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        criteria: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank feature opportunities based on criteria.

        Args:
            opportunities: List of feature opportunities
            criteria: Scoring criteria weights (default: balanced)

        Returns:
            Ranked list of opportunities
        """
        if criteria is None:
            criteria = {
                "confidence": 0.3,
                "evidence_count": 0.3,
                "impact": 0.4,
            }

        def calculate_score(opp: Dict[str, Any]) -> float:
            # Confidence score
            confidence_map = {"high": 1.0, "medium": 0.6, "low": 0.3}
            confidence_score = confidence_map.get(opp.get("confidence", "low"), 0.3)

            # Evidence count score (normalized)
            evidence_count = len(opp.get("evidence", []))
            evidence_score = min(evidence_count / 5.0, 1.0)  # Max at 5 evidence points

            # Impact score (based on keywords)
            impact_text = opp.get("expected_impact", "").lower()
            impact_keywords = ["revenue", "retention", "engagement", "critical", "essential"]
            impact_score = sum(1 for kw in impact_keywords if kw in impact_text) / len(impact_keywords)

            # Weighted total
            total = (
                confidence_score * criteria["confidence"] +
                evidence_score * criteria["evidence_count"] +
                impact_score * criteria["impact"]
            )

            return total

        # Add scores and sort
        for opp in opportunities:
            opp["_score"] = calculate_score(opp)

        ranked = sorted(opportunities, key=lambda x: x["_score"], reverse=True)

        logger.info(f"Ranked {len(ranked)} opportunities")
        return ranked
