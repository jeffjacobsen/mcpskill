#!/usr/bin/env python3
"""Direct MCP execution wrapper for Claude Code skills.

This script provides a simple CLI interface to MCP servers,
designed to be called from Claude Code as part of the mcp-orchestrator skill.

Usage:
    python orchestrate.py <config-path> "<user-message>"

Example:
    python orchestrate.py config.yaml "List all Python files in this directory"
"""

import asyncio
import logging
import sys
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Look for .env in skill directory, project root, and user home
    skill_dir = Path(__file__).parent
    env_paths = [
        skill_dir / ".env",
        skill_dir.parent.parent.parent / ".env",  # Project root
        Path.home() / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

# Add the mcpskill package to the Python path
# This assumes the skill is in .claude/skills/mcp-orchestrator/
# and mcpskill is installed in the environment
try:
    from mcpskill.config import load_config
    from mcpskill.client import MCPClient
    from mcpskill.executor import DirectExecutor
except ImportError as e:
    print(
        "Error: MCPSkill package not found. Please install it first:",
        file=sys.stderr,
    )
    print("  cd /path/to/mcpskill", file=sys.stderr)
    print("  pip install -e .", file=sys.stderr)
    print(f"\nOriginal error: {e}", file=sys.stderr)
    sys.exit(1)


async def execute_request(config_path: str, user_message: str) -> str:
    """Execute MCP request directly without intermediate LLM.

    Args:
        config_path: Path to the YAML configuration file
        user_message: User's natural language message

    Returns:
        Information about available tools or execution result

    Raises:
        Exception: If execution fails
    """
    # Load configuration
    config = load_config(config_path)

    # Create and connect MCP client
    client = MCPClient(config.downstream)
    await client.connect()

    try:
        # Create direct executor
        executor = DirectExecutor(client)

        # Process the user's message
        response = await executor.handle_request(user_message)

        return response

    finally:
        # Always disconnect
        await client.disconnect()


def main():
    """Main entry point for the script."""
    # Check arguments
    if len(sys.argv) != 3:
        print("Usage: python orchestrate.py <config-path> <user-message>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print('  python orchestrate.py config.yaml "List all files"', file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    user_message = sys.argv[2]

    # Validate config file exists
    if not Path(config_path).exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    # Set up logging to stderr (so stdout only has the response)
    logging.basicConfig(
        level=logging.WARNING,  # Change to DEBUG for troubleshooting
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    # Allow debug mode via environment variable
    import os
    if os.getenv("MCPSKILL_LOG_LEVEL") == "DEBUG":
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Execute the request
        response = asyncio.run(execute_request(config_path, user_message))

        # Output only the response to stdout
        print(response)

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logging.exception("Execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
