"""Generate development task breakdowns."""

import json
from typing import Dict, Any, List

from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TaskBreakdownGenerator:
    """
    Generate development task breakdowns.

    Creates actionable task lists for developers with estimates
    and dependencies.
    """

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=config.anthropic_api_key,
            temperature=0.4,
        )

    def generate_tasks(
        self,
        feature_spec: Dict[str, Any],
        ui_proposals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate development tasks.

        Args:
            feature_spec: Feature specification
            ui_proposals: UI proposals

        Returns:
            Task breakdown
        """
        logger.info("Generating task breakdown")

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a tech lead breaking down a feature into development tasks.

Create a comprehensive task breakdown with:
1. Backend tasks (API, database, logic)
2. Frontend tasks (UI components, pages)
3. Testing tasks (unit, integration, E2E)
4. DevOps tasks (deployment, monitoring)

For each task:
- Clear, actionable description
- Estimated effort (hours or story points)
- Dependencies (what must be done first)
- Priority (high/medium/low)

Format as JSON:
{
  "epic_name": "Feature name",
  "total_estimated_effort": "X hours or Y points",
  "tasks": [
    {
      "id": "TASK-1",
      "category": "backend/frontend/testing/devops",
      "title": "Task title",
      "description": "Detailed description",
      "estimated_effort": "X hours",
      "priority": "high/medium/low",
      "dependencies": ["TASK-0"],
      "acceptance_criteria": ["criteria1", "criteria2"]
    }
  ],
  "milestones": [
    {
      "name": "Milestone name",
      "tasks": ["TASK-1", "TASK-2"],
      "description": "What's achieved"
    }
  ]
}"""),
            ("user", "Feature Spec:\n{spec}\n\nUI Proposals:\n{ui}")
        ])

        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "spec": json.dumps(feature_spec, indent=2),
                "ui": json.dumps(ui_proposals, indent=2)
            })

            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            breakdown = json.loads(content)
            logger.info(f"Generated {len(breakdown.get('tasks', []))} tasks")
            return breakdown

        except Exception as e:
            logger.error(f"Error generating tasks: {e}")
            return {
                "epic_name": "Error",
                "total_estimated_effort": "Unknown",
                "tasks": [],
                "milestones": [],
                "error": str(e)
            }

    def format_tasks_markdown(self, breakdown: Dict[str, Any]) -> str:
        """
        Format tasks as markdown.

        Args:
            breakdown: Task breakdown

        Returns:
            Markdown formatted tasks
        """
        md = f"# {breakdown.get('epic_name', 'Task Breakdown')}\n\n"
        md += f"**Total Estimated Effort**: {breakdown.get('total_estimated_effort')}\n\n"

        # Group by category
        categories = {}
        for task in breakdown.get("tasks", []):
            category = task.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(task)

        for category, tasks in categories.items():
            md += f"## {category.upper()} Tasks\n\n"
            for task in tasks:
                md += f"### {task.get('id')}: {task.get('title')}\n"
                md += f"**Priority**: {task.get('priority')} | "
                md += f"**Effort**: {task.get('estimated_effort')}\n\n"
                md += f"{task.get('description')}\n\n"

                if task.get('dependencies'):
                    md += f"**Dependencies**: {', '.join(task.get('dependencies'))}\n\n"

                if task.get('acceptance_criteria'):
                    md += "**Acceptance Criteria**:\n"
                    for criteria in task.get('acceptance_criteria'):
                        md += f"- [ ] {criteria}\n"
                    md += "\n"

        # Milestones
        if breakdown.get("milestones"):
            md += "## Milestones\n\n"
            for milestone in breakdown.get("milestones", []):
                md += f"### {milestone.get('name')}\n"
                md += f"{milestone.get('description')}\n"
                md += f"**Tasks**: {', '.join(milestone.get('tasks', []))}\n\n"

        return md
