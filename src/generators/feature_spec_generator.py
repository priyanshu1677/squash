"""Generate feature specifications."""

import json
from typing import Dict, Any

from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FeatureSpecGenerator:
    """
    Generate detailed feature specifications.

    Creates comprehensive specs with customer quotes, acceptance criteria,
    and implementation guidance.
    """

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=config.anthropic_api_key,
            temperature=0.6,
        )

    def generate_spec(
        self,
        feature: Dict[str, Any],
        impact_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate feature specification.

        Args:
            feature: Feature opportunity data
            impact_assessment: Impact assessment data

        Returns:
            Feature specification
        """
        logger.info(f"Generating spec for: {feature.get('name')}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior product manager writing a feature specification.

Create a comprehensive feature spec with:
1. Overview (what it is, why it matters)
2. User stories (who, what, why format)
3. Acceptance criteria (clear, testable conditions)
4. Customer evidence (quotes and data supporting this)
5. Success metrics (how we'll measure success)
6. Dependencies and considerations

Format as JSON:
{
  "overview": {
    "title": "Feature name",
    "problem_statement": "What problem this solves",
    "solution_summary": "How this solves it"
  },
  "user_stories": [
    "As a [user], I want [goal] so that [benefit]"
  ],
  "acceptance_criteria": [
    "Given [context], when [action], then [outcome]"
  ],
  "customer_evidence": {
    "quotes": ["quote1", "quote2"],
    "data_points": ["data1", "data2"]
  },
  "success_metrics": [
    {"metric": "name", "target": "value", "timeframe": "period"}
  ],
  "dependencies": ["dep1", "dep2"],
  "considerations": ["consideration1", "consideration2"]
}"""),
            ("user", "Feature:\n{feature}\n\nImpact Assessment:\n{impact}")
        ])

        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "feature": json.dumps(feature, indent=2),
                "impact": json.dumps(impact_assessment, indent=2)
            })

            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            spec = json.loads(content)
            logger.info("Feature spec generated successfully")
            return spec

        except Exception as e:
            logger.error(f"Error generating spec: {e}")
            return {
                "overview": {"error": str(e)},
                "user_stories": [],
                "acceptance_criteria": [],
                "customer_evidence": {},
                "success_metrics": [],
                "dependencies": [],
                "considerations": []
            }

    def format_spec_markdown(self, spec: Dict[str, Any]) -> str:
        """
        Format specification as markdown.

        Args:
            spec: Feature specification

        Returns:
            Markdown formatted spec
        """
        overview = spec.get("overview", {})
        title = overview.get("title", "Feature Specification")

        md = f"# {title}\n\n"
        md += f"## Problem Statement\n{overview.get('problem_statement', 'N/A')}\n\n"
        md += f"## Solution Summary\n{overview.get('solution_summary', 'N/A')}\n\n"

        # User stories
        md += "## User Stories\n"
        for story in spec.get("user_stories", []):
            md += f"- {story}\n"
        md += "\n"

        # Acceptance criteria
        md += "## Acceptance Criteria\n"
        for criteria in spec.get("acceptance_criteria", []):
            md += f"- [ ] {criteria}\n"
        md += "\n"

        # Evidence
        evidence = spec.get("customer_evidence", {})
        if evidence.get("quotes"):
            md += "## Customer Evidence\n"
            md += "### Quotes\n"
            for quote in evidence.get("quotes", []):
                md += f"> {quote}\n\n"

        # Success metrics
        md += "## Success Metrics\n"
        for metric in spec.get("success_metrics", []):
            md += f"- **{metric.get('metric')}**: {metric.get('target')} ({metric.get('timeframe')})\n"
        md += "\n"

        # Dependencies
        if spec.get("dependencies"):
            md += "## Dependencies\n"
            for dep in spec.get("dependencies", []):
                md += f"- {dep}\n"
            md += "\n"

        return md
