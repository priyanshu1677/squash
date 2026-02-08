"""Generate UI and workflow change proposals."""

import json
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class UIProposalGenerator:
    """
    Generate UI and workflow change proposals.

    Creates specific recommendations for UI changes, screen mockups,
    and workflow improvements.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="o3-mini",
            api_key=config.openai_api_key,
        )

    def generate_proposals(
        self,
        feature_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate UI and workflow proposals.

        Args:
            feature_spec: Feature specification

        Returns:
            UI proposals
        """
        logger.info("Generating UI proposals")

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a product designer creating UI and workflow proposals based on a feature spec.

For each UI change, describe the screen layout, key components, and interactions in enough detail that a frontend developer could implement it. Think through the full user journey from entry point to completion.

Return ONLY valid JSON (no markdown fences, no commentary):
{{
  "ui_changes": [
    {{
      "screen": "Screen name",
      "change_type": "new/modify/remove",
      "description": "What changes and why",
      "components": ["component1", "component2"],
      "mockup_description": "Detailed layout description: what the user sees, where elements are positioned, key interactions"
    }}
  ],
  "user_flow": [
    {{
      "step": 1,
      "screen": "Screen name",
      "action": "What the user does",
      "outcome": "What happens as a result"
    }}
  ],
  "data_model_changes": [
    {{
      "entity": "Entity name",
      "change_type": "new_field/new_table/modify",
      "description": "What changes",
      "fields": ["field1: type - purpose", "field2: type - purpose"]
    }}
  ],
  "design_considerations": [
    "Accessibility consideration",
    "Responsive design consideration",
    "Edge case or error state"
  ]
}}"""),
            ("user", "Feature Spec:\n{spec}")
        ])

        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "spec": json.dumps(feature_spec, indent=2)
            })

            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            proposals = json.loads(content)
            logger.info("UI proposals generated successfully")
            return proposals

        except Exception as e:
            logger.error(f"Error generating UI proposals: {e}")
            return {
                "ui_changes": [],
                "user_flow": [],
                "data_model_changes": [],
                "design_considerations": [],
                "error": str(e)
            }

    def format_proposals_markdown(self, proposals: Dict[str, Any]) -> str:
        """
        Format proposals as markdown.

        Args:
            proposals: UI proposals

        Returns:
            Markdown formatted proposals
        """
        md = "# UI & Workflow Proposals\n\n"

        # UI Changes
        md += "## UI Changes\n\n"
        for change in proposals.get("ui_changes", []):
            md += f"### {change.get('screen')} ({change.get('change_type')})\n"
            md += f"{change.get('description')}\n\n"
            md += f"**Components**: {', '.join(change.get('components', []))}\n\n"
            md += f"**Mockup Description**:\n{change.get('mockup_description')}\n\n"

        # User Flow
        md += "## User Flow\n\n"
        for step in proposals.get("user_flow", []):
            md += f"{step.get('step')}. **{step.get('screen')}**\n"
            md += f"   - Action: {step.get('action')}\n"
            md += f"   - Outcome: {step.get('outcome')}\n\n"

        # Data Model
        md += "## Data Model Changes\n\n"
        for change in proposals.get("data_model_changes", []):
            md += f"### {change.get('entity')} ({change.get('change_type')})\n"
            md += f"{change.get('description')}\n"
            if change.get('fields'):
                md += f"**Fields**: {', '.join(change.get('fields'))}\n"
            md += "\n"

        # Considerations
        md += "## Design Considerations\n\n"
        for consideration in proposals.get("design_considerations", []):
            md += f"- {consideration}\n"

        return md
