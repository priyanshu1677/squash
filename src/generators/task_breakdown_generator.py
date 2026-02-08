"""Generate development task breakdowns."""

import json
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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
        self.llm = ChatOpenAI(
            model="o3-mini",
            api_key=config.openai_api_key,
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
            ("system", """You are a tech lead breaking down a feature into development tasks that can be directly added to a sprint board.

Given the feature spec and UI proposals, create a complete task breakdown covering:
1. Backend tasks — API endpoints, database migrations, business logic, integrations
2. Frontend tasks — UI components, pages, state management, API integration
3. Testing tasks — unit tests, integration tests, E2E tests
4. DevOps tasks — deployment, monitoring, feature flags

Each task should be small enough to complete in 1-3 days. Include clear dependency chains so the team knows the critical path.

Return ONLY valid JSON (no markdown fences, no commentary):
{{
  "epic_name": "Feature name",
  "total_estimated_effort": "X hours or Y story points",
  "tasks": [
    {{
      "id": "TASK-1",
      "category": "backend/frontend/testing/devops",
      "title": "Concise, actionable task title",
      "description": "What to implement, key technical decisions, and any gotchas",
      "estimated_effort": "X hours",
      "priority": "high/medium/low",
      "dependencies": [],
      "acceptance_criteria": ["testable criterion 1", "testable criterion 2"]
    }}
  ],
  "milestones": [
    {{
      "name": "Milestone name",
      "tasks": ["TASK-1", "TASK-2"],
      "description": "What's shippable at this point"
    }}
  ]
}}"""),
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
