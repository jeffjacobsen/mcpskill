"""MCP client manager for downstream servers."""

import logging
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .types import DownstreamConfig

logger = logging.getLogger(__name__)


class MCPClient:
    """Manages connection to a downstream MCP server."""

    def __init__(self, config: DownstreamConfig):
        """Initialize MCP client.

        Args:
            config: Downstream server configuration
        """
        self.config = config
        self.session: ClientSession | None = None
        self._exit_stack: AsyncExitStack | None = None

    async def connect(self) -> None:
        """Connect to the downstream MCP server."""
        logger.info(
            f"Connecting to downstream server: {self.config.command} {' '.join(self.config.args)}"
        )

        # Create server parameters
        server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args,
            env=self.config.env if self.config.env else None,
        )

        logger.debug("Creating AsyncExitStack")
        # Use AsyncExitStack to properly manage async context managers
        self._exit_stack = AsyncExitStack()

        logger.debug("Entering stdio_client context")
        read_stream, write_stream = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        logger.debug("Creating and entering ClientSession context")
        # ClientSession is also an async context manager - it starts background tasks
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        logger.debug("Initializing session")
        # Initialize the session
        await self.session.initialize()
        logger.info("Successfully connected to downstream server")

    async def disconnect(self) -> None:
        """Disconnect from the downstream server."""
        if self._exit_stack:
            logger.info("Disconnecting from downstream server")
            await self._exit_stack.aclose()
            self._exit_stack = None
            self.session = None


    async def list_tools(self) -> list[Any]:
        """Get available tools from downstream server.

        Returns:
            List of tool definitions

        Raises:
            RuntimeError: If not connected
        """
        if not self.session:
            raise RuntimeError("Not connected to downstream server")

        result = await self.session.list_tools()
        logger.debug(f"Listed {len(result.tools)} tools from downstream server")
        return result.tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[Any]:
        """Call a tool on the downstream server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result content

        Raises:
            RuntimeError: If not connected
        """
        if not self.session:
            raise RuntimeError("Not connected to downstream server")

        logger.debug(f"Calling tool: {name} with args: {arguments}")
        result = await self.session.call_tool(name, arguments)
        logger.debug(f"Tool call completed: {name}")
        return result.content
