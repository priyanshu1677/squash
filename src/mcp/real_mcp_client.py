"""Real MCP server client using the official MCP Python SDK (stdio transport)."""

import asyncio
import json
import os
import threading
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ..utils.logger import get_logger

logger = get_logger(__name__)

CALL_TOOL_TIMEOUT = 30  # seconds


def _find_var_refs(s: str) -> list[str]:
    """Find all ${VAR} references in a string."""
    import re
    return re.findall(r'\$\{[^}]+\}', s)


class RealMCPServerClient:
    """
    Connects to a real MCP server subprocess via stdio transport.

    Runs a dedicated background thread with its own asyncio event loop so that
    the sync call_tool() interface used by the rest of the pipeline works
    without blocking the main thread.
    """

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        self.server_name = server_name
        self.server_config = server_config
        self.capability_map: Dict[str, str] = server_config.get("capability_map", {})
        self.capabilities: List[str] = server_config.get("capabilities", [])

        # Async internals (set during connect)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None
        self._available_tools: List[str] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> "RealMCPServerClient":
        """Start the background event loop, launch the MCP server, and initialise the session."""
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name=f"mcp-{self.server_name}"
        )
        self._thread.start()

        # Run the async connect on the background loop and wait for it
        future = asyncio.run_coroutine_threadsafe(self._async_connect(), self._loop)
        future.result(timeout=30)  # wait up to 30s for server startup
        return self

    async def _async_connect(self) -> None:
        server_params = StdioServerParameters(
            command=self.server_config["command"],
            args=self._resolve_arg_vars(self.server_config.get("args", [])),
            env=self._resolve_env_vars(self.server_config.get("env")),
        )

        self._exit_stack = AsyncExitStack()
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._session.initialize()

        # Discover tools
        tools_result = await self._session.list_tools()
        self._available_tools = [t.name for t in tools_result.tools]
        logger.info(
            f"Connected to MCP server '{self.server_name}' with tools: {self._available_tools}"
        )

    def disconnect(self) -> None:
        """Shut down the MCP server subprocess and stop the background loop."""
        if self._loop is None or not self._loop.is_running():
            return

        try:
            future = asyncio.run_coroutine_threadsafe(self._async_disconnect(), self._loop)
            future.result(timeout=10)
        except Exception as e:
            logger.warning(f"Error disconnecting MCP server '{self.server_name}': {e}")
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread is not None:
                self._thread.join(timeout=5)
            self._loop = None
            self._thread = None
            self._session = None

    async def _async_disconnect(self) -> None:
        if self._exit_stack is not None:
            await self._exit_stack.aclose()
            self._exit_stack = None

    # ------------------------------------------------------------------
    # Tool invocation
    # ------------------------------------------------------------------

    def call_tool(self, capability: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Map a capability name to an MCP tool name and invoke it synchronously.

        Falls back to using the capability name directly if no mapping exists.
        """
        if self._loop is None or self._session is None:
            return {"error": f"MCP server '{self.server_name}' is not connected"}

        tool_name = self.capability_map.get(capability, capability)
        if tool_name not in self._available_tools:
            return {"error": f"Tool '{tool_name}' (capability '{capability}') not available on '{self.server_name}'"}

        future = asyncio.run_coroutine_threadsafe(
            self._async_call_tool(tool_name, params or {}), self._loop
        )
        try:
            return future.result(timeout=CALL_TOOL_TIMEOUT)
        except TimeoutError:
            return {"error": f"Timeout calling '{tool_name}' on '{self.server_name}'"}
        except Exception as e:
            return {"error": f"Error calling '{tool_name}' on '{self.server_name}': {e}"}

    async def _async_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        result = await self._session.call_tool(tool_name, arguments=arguments)

        if result.isError:
            text_parts = [c.text for c in result.content if hasattr(c, "text")]
            return {"error": " ".join(text_parts) or "Unknown MCP tool error"}

        # Collect all text content; attempt to parse as JSON
        text_parts = [c.text for c in result.content if hasattr(c, "text")]
        combined = "\n".join(text_parts)
        try:
            return json.loads(combined)
        except (json.JSONDecodeError, ValueError):
            return {"result": combined}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _run_loop(self) -> None:
        """Entry point for the background thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    @staticmethod
    def _resolve_env_vars(env_template: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """
        Resolve ${VAR} references in env values from os.environ.

        Returns a full copy of the current environment with the template values
        merged in, so the subprocess inherits PATH etc.
        """
        if env_template is None:
            return None

        resolved = os.environ.copy()
        for key, value in env_template.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                resolved[key] = os.environ.get(env_var, "")
            else:
                resolved[key] = value
        return resolved

    @staticmethod
    def _resolve_arg_vars(args: List[str]) -> List[str]:
        """Resolve ${VAR} references in command args from os.environ."""
        resolved = []
        for arg in args:
            if isinstance(arg, str) and "${" in arg:
                for var_ref in _find_var_refs(arg):
                    env_var = var_ref[2:-1]
                    arg = arg.replace(var_ref, os.environ.get(env_var, ""))
            resolved.append(arg)
        return resolved
