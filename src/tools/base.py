"""Base tool interface for MCP tool connectors."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..mcp.client import MCPClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseTool(ABC):
    """
    Base class for all tool connectors.

    Each tool connector wraps an MCP client and provides
    high-level methods for common operations.
    """

    def __init__(self, mcp_client: MCPClient):
        """
        Initialize tool connector.

        Args:
            mcp_client: MCP client for this tool
        """
        self.client = mcp_client
        self.name = mcp_client.server_name
        self.logger = get_logger(f"{__name__}.{self.name}")

    @abstractmethod
    def get_insights(self) -> Dict[str, Any]:
        """
        Get high-level insights from this tool.

        Returns:
            Insights dictionary
        """
        pass

    def call_capability(
        self,
        capability: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a tool capability.

        Args:
            capability: Capability name
            params: Capability parameters

        Returns:
            Response data
        """
        return self.client.call_tool(capability, params)

    def get_capabilities(self) -> List[str]:
        """
        Get list of available capabilities.

        Returns:
            List of capability names
        """
        return self.client.list_capabilities()
