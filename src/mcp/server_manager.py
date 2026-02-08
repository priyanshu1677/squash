"""MCP server connection manager."""

import atexit
from typing import Any, Dict, List, Optional

from ..utils.config import load_config
from ..utils.logger import get_logger
from .client import MCPClient

logger = get_logger(__name__)


class MCPServerManager:
    """
    Manages connections to multiple MCP servers.

    Handles initialization, connection pooling, and tool routing.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize server manager.

        Args:
            config_path: Optional path to MCP servers configuration
        """
        self.config = load_config(config_path)
        self.servers: Dict[str, MCPClient] = {}
        self._initialize_servers()
        atexit.register(self.shutdown)

    def _initialize_servers(self) -> None:
        """Initialize all configured MCP servers."""
        servers_config = self.config.get("servers", {})

        for server_name, server_config in servers_config.items():
            try:
                client = MCPClient(server_name, server_config)
                self.servers[server_name] = client
                logger.info(f"Initialized MCP server: {server_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {server_name}: {e}")

    def get_server(self, server_name: str) -> Optional[MCPClient]:
        """
        Get a server client by name.

        Args:
            server_name: Server name

        Returns:
            MCP client or None if not found
        """
        return self.servers.get(server_name)

    def call_tool(
        self,
        server_name: str,
        capability: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a tool on a specific server.

        Args:
            server_name: Server name
            capability: Tool capability
            params: Tool parameters

        Returns:
            Tool response
        """
        server = self.get_server(server_name)
        if not server:
            return {"error": f"Server {server_name} not found"}

        return server.call_tool(capability, params)

    def get_servers_by_type(self, server_type: str) -> List[MCPClient]:
        """
        Get all servers of a specific type.

        Args:
            server_type: Server type (e.g., 'analytics', 'support')

        Returns:
            List of MCP clients
        """
        return [
            client for client in self.servers.values()
            if client.server_config.get("type") == server_type
        ]

    def list_all_capabilities(self) -> Dict[str, List[str]]:
        """
        List all capabilities across all servers.

        Returns:
            Dictionary mapping server names to capabilities
        """
        return {
            name: client.list_capabilities()
            for name, client in self.servers.items()
        }

    def get_all_server_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all servers.

        Returns:
            List of server metadata
        """
        return [client.get_server_info() for client in self.servers.values()]

    def query_all_analytics(self, query_type: str) -> Dict[str, Any]:
        """
        Query all analytics tools and aggregate results.

        Args:
            query_type: Type of query (e.g., 'user_metrics', 'events')

        Returns:
            Aggregated analytics data
        """
        analytics_servers = self.get_servers_by_type("analytics")
        results = {}

        for server in analytics_servers:
            # Map query types to capabilities
            capability_map = {
                "user_metrics": "get_user_metrics",
                "events": "query_events",
                "retention": "get_retention_data",
            }

            capability = capability_map.get(query_type)
            if capability and capability in server.list_capabilities():
                results[server.server_name] = server.call_tool(capability)

        return results

    def query_all_support(self) -> Dict[str, Any]:
        """
        Query all support tools for customer feedback.

        Returns:
            Aggregated support data
        """
        support_servers = self.get_servers_by_type("support")
        results = {}

        for server in support_servers:
            server_data = {}

            # Get tickets/conversations
            if "get_tickets" in server.list_capabilities():
                server_data["tickets"] = server.call_tool("get_tickets")
            elif "get_conversations" in server.list_capabilities():
                server_data["conversations"] = server.call_tool("get_conversations")

            # Get sentiment
            if "get_customer_sentiment" in server.list_capabilities():
                server_data["sentiment"] = server.call_tool("get_customer_sentiment")

            results[server.server_name] = server_data

        return results

    def shutdown(self) -> None:
        """Disconnect all MCP server clients and clean up subprocesses."""
        logger.info("Shutting down MCP server manager...")
        for name, client in self.servers.items():
            try:
                client.disconnect()
                logger.info(f"Disconnected MCP server: {name}")
            except Exception as e:
                logger.warning(f"Error disconnecting {name}: {e}")
        self.servers.clear()
