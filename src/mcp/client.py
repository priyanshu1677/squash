"""MCP client for tool invocation."""

from typing import Any, Dict, Optional

from ..utils.config import config
from ..utils.logger import get_logger
from .mock_servers import create_mock_server
from .real_servers import create_real_server

logger = get_logger(__name__)

# Servers that have legacy real API implementations (direct HTTP)
REAL_SERVERS = {"mixpanel", "posthog", "jira", "confluence", "salesforce"}


class MCPClient:
    """
    Client for invoking MCP tools.

    Supports three backends (checked in order):
    1. Mock servers — when force_mock or server_config.mock is true
    2. Real MCP servers — when server_config has a "command" key (official MCP SDK, stdio transport)
    3. Legacy real servers — direct HTTP wrappers in real_servers.py
    """

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        self.server_name = server_name
        self.server_config = server_config
        self._real_mcp_client = None

        force_mock = config.use_mock_mcp
        server_mock = server_config.get("mock", True)
        has_command = "command" in server_config
        has_real = server_name in REAL_SERVERS

        self.use_mock = force_mock or server_mock

        if self.use_mock:
            self.server = create_mock_server(server_name, server_config)
            logger.info(f"Using mock MCP server: {server_name}")
        elif has_command:
            # Real MCP server via stdio transport (official SDK)
            try:
                from .real_mcp_client import RealMCPServerClient
                client = RealMCPServerClient(server_name, server_config)
                client.connect()
                self._real_mcp_client = client
                self.server = client  # duck-typed: has call_tool()
                logger.info(f"Using real MCP server: {server_name}")
            except Exception as e:
                logger.warning(
                    f"Failed to connect to MCP server '{server_name}', "
                    f"falling back to mock: {e}"
                )
                self.server = create_mock_server(server_name, server_config)
                self.use_mock = True
        elif has_real:
            # Legacy direct-HTTP wrappers
            try:
                self.server = create_real_server(server_name, server_config)
                logger.info(f"Using real API server: {server_name}")
            except Exception as e:
                logger.warning(f"Failed to init real server {server_name}, falling back to mock: {e}")
                self.server = create_mock_server(server_name, server_config)
                self.use_mock = True
        else:
            self.server = create_mock_server(server_name, server_config)
            self.use_mock = True
            logger.info(f"Using mock MCP server: {server_name}")

    def call_tool(
        self,
        capability: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if params is None:
            params = {}

        try:
            logger.debug(f"Calling {self.server_name}.{capability} with params: {params}")
            result = self.server.call_tool(capability, params)
            logger.debug(f"Tool response: {result}")
            return result

        except Exception as e:
            logger.error(f"Error calling {self.server_name}.{capability}: {e}")
            return {"error": str(e)}

    def disconnect(self) -> None:
        """Disconnect the real MCP client if one is active."""
        if self._real_mcp_client is not None:
            self._real_mcp_client.disconnect()
            self._real_mcp_client = None

    def list_capabilities(self) -> list[str]:
        return self.server_config.get("capabilities", [])

    def get_server_info(self) -> Dict[str, Any]:
        return {
            "name": self.server_name,
            "type": self.server_config.get("type"),
            "description": self.server_config.get("description"),
            "capabilities": self.list_capabilities(),
            "is_mock": self.use_mock,
        }
