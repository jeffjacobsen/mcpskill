"""Direct execution of MCP tools without intermediate LLM."""

import json
import logging
from typing import Any

from .client import MCPClient

logger = logging.getLogger(__name__)


class DirectExecutor:
    """Executes MCP tools directly based on user requests.

    This is a simple pass-through executor that lists available tools
    and returns them in a format Claude Code can understand.
    """

    def __init__(self, mcp_client: MCPClient):
        """Initialize executor.

        Args:
            mcp_client: Connected MCP client for downstream server
        """
        self.mcp_client = mcp_client

    async def handle_request(self, message: str) -> str:
        """Process user message - either list tools or call a tool.

        Supports two types of requests:
        1. JSON format for tool calls: {"tool": "tool_name", "arguments": {...}}
        2. Plain text: Lists available tools

        Args:
            message: User's message/request

        Returns:
            Tool execution result or formatted description of available tools
        """
        logger.info(f"Handling request: {message[:100]}...")

        # Check if this is a JSON tool call request
        message_stripped = message.strip()
        if message_stripped.startswith('{') and message_stripped.endswith('}'):
            try:
                request = json.loads(message_stripped)
                if 'tool' in request:
                    tool_name = request['tool']
                    arguments = request.get('arguments', {})
                    return await self.call_tool(tool_name, arguments)
            except json.JSONDecodeError:
                # Not valid JSON, fall through to list tools
                pass

        # Default: List available tools
        tools = await self.mcp_client.list_tools()

        if not tools:
            return "No tools available from the downstream MCP server."

        # Format tools for Claude Code
        response_parts = [
            f"Available tools from MCP server ({len(tools)} tools):\n"
        ]

        for tool in tools:
            response_parts.append(f"\n**{tool.name}**")
            if tool.description:
                response_parts.append(f"  {tool.description}")

            # Show input schema
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                if 'properties' in schema:
                    props = schema['properties']
                    required = schema.get('required', [])
                    response_parts.append("  Parameters:")
                    for prop_name, prop_def in props.items():
                        req_marker = "* " if prop_name in required else "  "
                        prop_type = prop_def.get('type', 'any')
                        prop_desc = prop_def.get('description', '')
                        response_parts.append(
                            f"    {req_marker}{prop_name} ({prop_type}): {prop_desc}"
                        )

        response_parts.append(
            "\n\nTo call a tool, send a JSON request like:"
        )
        response_parts.append(
            '{"tool": "tool_name", "arguments": {"param": "value"}}'
        )

        return "\n".join(response_parts)

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Call a specific tool directly.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        logger.info(f"Calling tool: {tool_name}")

        try:
            result_content = await self.mcp_client.call_tool(tool_name, arguments)
            return self._format_result(result_content)
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return f"Error calling tool {tool_name}: {str(e)}"

    def _format_result(self, result_content: list[Any]) -> str:
        """Format tool result content as text.

        Args:
            result_content: Content from tool call result

        Returns:
            Formatted text
        """
        if not result_content:
            return "Tool executed successfully (no output)"

        parts = []
        for item in result_content:
            if hasattr(item, "text"):
                parts.append(item.text)
            elif hasattr(item, "type") and item.type == "text":
                parts.append(str(item))
            else:
                # Try to serialize as JSON for structured content
                try:
                    parts.append(json.dumps(item, indent=2))
                except (TypeError, ValueError):
                    parts.append(str(item))

        return "\n".join(parts)
