"""Generate UI and workflow change proposals."""

import json
from typing import Dict, Any, List

from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

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
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=config.anthropic_api_key,
            temperature=0.7,
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
            ("system", """You are a UX designer creating UI proposals for a feature.

Based on the feature spec, propose:
1. UI changes (new screens, components, modifications)
2. User flow (step-by-step how users interact)
3. Data model changes (new fields, relationships)
4. Design considerations (accessibility, responsiveness, etc.)

Format as JSON:
{
  "ui_changes": [
    {
      "screen": "Screen name",
      "change_type": "new/modify/remove",
      "description": "What changes",
      "components": ["component1", "component2"],
      "mockup_description": "Detailed description of UI"
    }
  ],
  "user_flow": [
    {
      "step": 1,
      "screen": "Screen name",
      "action": "What user does",
      "outcome": "What happens"
    }
  ],
  "data_model_changes": [
    {
      "entity": "Entity name",
      "change_type": "new_field/new_table/modify",
      "description": "What changes",
      "fields": ["field1", "field2"]
    }
  ],
  "design_considerations": [
    "Consideration 1",
    "Consideration 2"
  ]
}"""),
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
