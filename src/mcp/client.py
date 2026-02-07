"""MCP client for tool invocation."""

from typing import Any, Dict, Optional

from ..utils.config import config
from ..utils.logger import get_logger
from .mock_servers import create_mock_server

logger = get_logger(__name__)


class MCPClient:
    """
    Client for invoking MCP tools.

    This implementation supports both mock servers (for prototyping)
    and real MCP connections (for production).
    """

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        """
        Initialize MCP client.

        Args:
            server_name: Name of the MCP server
            server_config: Server configuration
        """
        self.server_name = server_name
        self.server_config = server_config
        self.use_mock = config.use_mock_mcp or server_config.get("mock", False)

        if self.use_mock:
            self.server = create_mock_server(server_name, server_config)
            logger.info(f"Using mock MCP server: {server_name}")
        else:
            # In production, this would initialize real MCP connection
            logger.info(f"Real MCP connection not implemented for: {server_name}")
            raise NotImplementedError("Real MCP connections not yet implemented")

    def call_tool(
        self,
        capability: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a tool capability.

        Args:
            capability: Tool capability name
            params: Tool parameters

        Returns:
            Tool response data
        """
        if params is None:
            params = {}

        try:
            logger.debug(f"Calling {self.server_name}.{capability} with params: {params}")

            if self.use_mock:
                result = self.server.call_tool(capability, params)
            else:
                # In production, call real MCP server
                raise NotImplementedError("Real MCP connections not yet implemented")

            logger.debug(f"Tool response: {result}")
            return result

        except Exception as e:
            logger.error(f"Error calling {self.server_name}.{capability}: {e}")
            return {"error": str(e)}

    def list_capabilities(self) -> list[str]:
        """
        List available tool capabilities.

        Returns:
            List of capability names
        """
        return self.server_config.get("capabilities", [])

    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information.

        Returns:
            Server metadata
        """
        return {
            "name": self.server_name,
            "type": self.server_config.get("type"),
            "description": self.server_config.get("description"),
            "capabilities": self.list_capabilities(),
            "is_mock": self.use_mock,
        }
