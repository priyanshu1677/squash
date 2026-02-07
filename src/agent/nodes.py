"""Agent nodes for LangGraph workflow."""

from pathlib import Path
from typing import Dict, Any

from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

from ..mcp.server_manager import MCPServerManager
from ..tools.analytics import MixpanelTool, PostHogTool
from ..tools.support import ZendeskTool, IntercomTool
from ..tools.sales import SalesforceTool
from ..tools.project_management import JiraTool, ConfluenceTool
from ..processors import DocumentParser, InterviewProcessor, DataAggregator
from ..analyzers import FeatureAnalyzer, PriorityScorer, ImpactAssessor
from ..generators import FeatureSpecGenerator, UIProposalGenerator, TaskBreakdownGenerator
from ..utils.config import config
from ..utils.logger import get_logger
from .state import AgentState
from .prompts import QUERY_ROUTER_PROMPT

logger = get_logger(__name__)


class PMAgentNodes:
    """Collection of nodes for the PM Agent workflow."""

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=config.anthropic_api_key,
            temperature=0.3,
        )
        self.mcp_manager = MCPServerManager()
        self.interview_processor = InterviewProcessor()
        self.feature_analyzer = FeatureAnalyzer()
        self.priority_scorer = PriorityScorer()
        self.impact_assessor = ImpactAssessor()
        self.feature_spec_gen = FeatureSpecGenerator()
        self.ui_proposal_gen = UIProposalGenerator()
        self.task_breakdown_gen = TaskBreakdownGenerator()

    def query_router(self, state: AgentState) -> AgentState:
        """
        Route query to appropriate workflow.

        Determines the type of query and what analysis is needed.
        """
        logger.info(f"Routing query: {state['query']}")

        try:
            prompt = ChatPromptTemplate.from_messages([
                ("user", QUERY_ROUTER_PROMPT)
            ])

            chain = prompt | self.llm
            response = chain.invoke({"query": state["query"]})

            query_type = response.content.strip().lower()
            if query_type not in ["feature_discovery", "analysis", "task_breakdown"]:
                query_type = "feature_discovery"  # Default

            state["query_type"] = query_type
            logger.info(f"Query type: {query_type}")

        except Exception as e:
            logger.error(f"Error in query router: {e}")
            state["query_type"] = "feature_discovery"
            state["error"] = str(e)

        return state

    def data_collector(self, state: AgentState) -> AgentState:
        """
        Collect data from MCP tools.

        Fetches data from analytics, support, sales, and PM tools.
        """
        logger.info("Collecting data from MCP tools")

        try:
            # Process uploaded interviews first
            interview_data = None
            if state.get("uploaded_files"):
                interviews = []
                for file_path in state["uploaded_files"]:
                    doc_data = DocumentParser.parse(Path(file_path))
                    processed = self.interview_processor.process_interview(doc_data)
                    interviews.append(processed)

                interview_data = self.interview_processor.aggregate_interviews(interviews)
                state["interview_data"] = interview_data

            # Collect from analytics tools
            analytics_data = []
            for tool_name in ["mixpanel", "posthog"]:
                client = self.mcp_manager.get_server(tool_name)
                if client:
                    if tool_name == "mixpanel":
                        tool = MixpanelTool(client)
                    else:
                        tool = PostHogTool(client)
                    analytics_data.append(tool.get_insights())

            state["analytics_data"] = analytics_data

            # Collect from support tools
            support_data = []
            for tool_name in ["zendesk", "intercom"]:
                client = self.mcp_manager.get_server(tool_name)
                if client:
                    if tool_name == "zendesk":
                        tool = ZendeskTool(client)
                    else:
                        tool = IntercomTool(client)
                    support_data.append(tool.get_insights())

            state["support_data"] = support_data

            # Collect from sales tools
            sales_client = self.mcp_manager.get_server("salesforce")
            if sales_client:
                sales_tool = SalesforceTool(sales_client)
                state["sales_data"] = sales_tool.get_insights()

            # Collect from PM tools
            pm_data = []
            for tool_name in ["jira", "confluence"]:
                client = self.mcp_manager.get_server(tool_name)
                if client:
                    if tool_name == "jira":
                        tool = JiraTool(client)
                    else:
                        tool = ConfluenceTool(client)
                    pm_data.append(tool.get_insights())

            state["pm_data"] = pm_data

            logger.info("Data collection completed")

        except Exception as e:
            logger.error(f"Error in data collector: {e}")
            state["error"] = str(e)

        return state

    def data_processor(self, state: AgentState) -> AgentState:
        """
        Process and aggregate data from all sources.

        Combines data into a unified view.
        """
        logger.info("Processing and aggregating data")

        try:
            aggregated = DataAggregator.aggregate_all(
                analytics_data=state.get("analytics_data", []),
                support_data=state.get("support_data", []),
                sales_data=state.get("sales_data", {}),
                pm_data=state.get("pm_data", []),
                interview_data=state.get("interview_data", {})
            )

            state["aggregated_data"] = aggregated
            logger.info("Data processing completed")

        except Exception as e:
            logger.error(f"Error in data processor: {e}")
            state["error"] = str(e)

        return state

    def analyzer(self, state: AgentState) -> AgentState:
        """
        Analyze data to identify opportunities.

        Uses FeatureAnalyzer and PriorityScorer.
        """
        logger.info("Analyzing data for opportunities")

        try:
            aggregated_data = state.get("aggregated_data", {})

            # Identify feature opportunities
            opportunities = self.feature_analyzer.analyze(aggregated_data)
            state["feature_opportunities"] = opportunities

            # Score and rank features
            scored = self.priority_scorer.score_all(opportunities, method="rice")
            state["scored_features"] = scored

            # Pick top feature
            if scored:
                state["top_feature"] = scored[0]

            logger.info(f"Analysis completed: {len(opportunities)} opportunities found")

        except Exception as e:
            logger.error(f"Error in analyzer: {e}")
            state["error"] = str(e)

        return state

    def generator(self, state: AgentState) -> AgentState:
        """
        Generate outputs (specs, proposals, tasks).

        Creates comprehensive deliverables.
        """
        logger.info("Generating deliverables")

        try:
            top_feature = state.get("top_feature")
            if not top_feature:
                logger.warning("No top feature to generate from")
                return state

            # Impact assessment
            context = {
                "analytics": state.get("analytics_data", []),
                "support": state.get("support_data", [])
            }
            impact = self.impact_assessor.assess_impact(top_feature, context)
            state["impact_assessment"] = impact

            # Feature spec
            spec = self.feature_spec_gen.generate_spec(top_feature, impact)
            state["feature_spec"] = spec

            # UI proposals
            ui_proposals = self.ui_proposal_gen.generate_proposals(spec)
            state["ui_proposals"] = ui_proposals

            # Task breakdown
            tasks = self.task_breakdown_gen.generate_tasks(spec, ui_proposals)
            state["task_breakdown"] = tasks

            logger.info("Generation completed")

        except Exception as e:
            logger.error(f"Error in generator: {e}")
            state["error"] = str(e)

        return state

    def reviewer(self, state: AgentState) -> AgentState:
        """
        Review and validate outputs.

        Final quality check before returning results.
        """
        logger.info("Reviewing outputs")

        # Mark as completed
        state["completed"] = True

        return state
