"""Assess potential impact of features."""

import json
from typing import Dict, Any

from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ImpactAssessor:
    """
    Assess the potential impact of features on users and business.

    Uses Claude to predict outcomes and identify risks.
    """

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=config.anthropic_api_key,
            temperature=0.5,
        )

    def assess_impact(
        self,
        feature: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess the impact of a feature.

        Args:
            feature: Feature data
            context: Business and user context

        Returns:
            Impact assessment
        """
        logger.info(f"Assessing impact for feature: {feature.get('name')}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert product strategist assessing feature impact.

Analyze the proposed feature and provide:
1. User impact (how it affects users)
2. Business impact (metrics, revenue, retention)
3. Technical considerations (complexity, dependencies)
4. Risks (what could go wrong)
5. Success metrics (how to measure success)

Format as JSON:
{
  "user_impact": {
    "description": "How users benefit",
    "affected_user_segments": ["segment1", "segment2"],
    "adoption_prediction": "high/medium/low"
  },
  "business_impact": {
    "description": "Business outcomes",
    "potential_metrics": {
      "retention": "+X%",
      "engagement": "+Y%"
    }
  },
  "technical_considerations": {
    "complexity": "high/medium/low",
    "estimated_effort": "X weeks",
    "dependencies": ["dep1", "dep2"]
  },
  "risks": ["risk1", "risk2"],
  "success_metrics": ["metric1", "metric2"]
}"""),
            ("user", "Feature:\n{feature}\n\nContext:\n{context}")
        ])

        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "feature": json.dumps(feature, indent=2),
                "context": json.dumps(context, indent=2)
            })

            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            assessment = json.loads(content)
            logger.info("Impact assessment completed")
            return assessment

        except Exception as e:
            logger.error(f"Error assessing impact: {e}")
            return {
                "user_impact": {"error": str(e)},
                "business_impact": {"error": str(e)},
                "technical_considerations": {"error": str(e)},
                "risks": [str(e)],
                "success_metrics": []
            }

    def compare_features(
        self,
        features: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare multiple features to help prioritization.

        Args:
            features: List of features with scores

        Returns:
            Comparison analysis
        """
        if len(features) < 2:
            return {"error": "Need at least 2 features to compare"}

        # Simple comparison based on scores
        comparisons = []
        for i, feature in enumerate(features):
            score = feature.get("rice_score") or feature.get("ice_score", 0)
            comparisons.append({
                "rank": i + 1,
                "name": feature.get("name"),
                "score": score,
                "confidence": feature.get("confidence"),
                "recommendation": "High priority" if i < 3 else "Consider later"
            })

        return {
            "comparison": comparisons,
            "top_recommendation": comparisons[0] if comparisons else None
        }
