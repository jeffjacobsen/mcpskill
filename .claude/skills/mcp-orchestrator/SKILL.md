---
name: mcp-orchestrator
description: Direct access to MCP (Model Context Protocol) servers. Use this when the user wants to interact with filesystem, database, or other MCP-enabled services. This skill provides zero-context access to MCP tools.
allowed-tools: [Bash, Read, Write, Edit]
---

# MCP Orchestrator Skill

This skill provides direct access to downstream MCP servers, allowing natural language interaction with tools while keeping zero tool definitions in Claude's context.

## When to Use This Skill

Activate this skill when:
- The user wants to interact with an MCP server
- User mentions specific MCP services (filesystem, database, GitHub, etc.)
- You need to access external tools without loading them into context
- The user wants to work with files, databases, or APIs via MCP

## How It Works

The skill provides direct access to MCP servers:
1. Receives the user's natural language request
2. Connects to the configured downstream MCP server
3. Returns available tools and their schemas
4. Claude Code can then call the tools directly

## Configuration

The skill requires a YAML configuration file that specifies the downstream MCP server:

### Example Configuration

```yaml
name: filesystem-assistant
description: "Natural language interface to filesystem operations"

downstream:
  command: npx
  args:
    - "-y"
    - "@modelcontextprotocol/server-filesystem"
    - "/Users/username/Documents"
  env: {}
```

### Minimal Configuration

No LLM configuration is needed. Just specify the downstream MCP server:

```yaml
name: my-mcp-skill
description: "Description of what this skill does"

downstream:
  command: <command to run MCP server>
  args: [<list of arguments>]
  env: {}  # Optional environment variables
```

## Usage Instructions for Claude

When this skill is activated:

1. **Check for Configuration**
   - Look for a config file in `.claude/skills/mcp-orchestrator/config.yaml`
   - Or ask the user for the path to their configuration file

2. **Discover Available Tools**
   - Execute: `python .claude/skills/mcp-orchestrator/orchestrate.py <config-path> "list tools"`
   - Example: `python .claude/skills/mcp-orchestrator/orchestrate.py config.yaml "What tools are available?"`
   - This returns all available tools with their descriptions and parameters

3. **Call a Tool**
   - Execute: `python .claude/skills/mcp-orchestrator/orchestrate.py <config-path> '<json-request>'`
   - JSON format: `{"tool": "tool_name", "arguments": {"param1": "value1", "param2": "value2"}}`
   - Example: `python .claude/skills/mcp-orchestrator/orchestrate.py config.yaml '{"tool": "list_directory", "arguments": {"path": "/tmp"}}'`

4. **Typical Workflow**
   - User asks: "List Python files in /tmp"
   - Step 1: Call skill to discover tools
   - Step 2: Identify that `search_files` tool is available
   - Step 3: Call skill with JSON to execute: `{"tool": "search_files", "arguments": {"path": "/tmp", "pattern": "*.py"}}`
   - Step 4: Present results to user

5. **Environment Variables**
   - Downstream servers may require API keys (check config.yaml `env` section)
   - No API keys are needed for the skill itself (no intermediate LLM)

6. **Error Handling**
   - If the skill fails, check that:
     - The config file exists and is valid YAML
     - The downstream MCP server command is available
     - Python dependencies are installed (`pip install -e .` from mcpskill root)
     - JSON tool call requests are properly formatted

## Common Use Cases

### Filesystem Operations
```yaml
downstream:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"]
```
User: "Find all Python files modified in the last week"

### Database Queries
```yaml
downstream:
  command: python
  args: ["-m", "mcp_server_sqlite", "database.db"]
```
User: "Show me users who signed up this month"

### API Integration
```yaml
downstream:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-github"]
  env:
    GITHUB_TOKEN: ${GITHUB_TOKEN}
```
User: "Create an issue for the bug we just discussed"

## Benefits

- **Token Efficiency**: Downstream server tools aren't loaded into context
- **Direct Access**: No intermediate LLM, just direct MCP communication
- **Fast**: Single hop to MCP server
- **Simple**: No LLM configuration needed
- **SDK Compatible**: Works with MCP servers that use SDKs requiring API keys

## Technical Details

The skill:
- Connects to the downstream MCP server via stdio
- Lists available tools dynamically
- Returns tool information in a readable format
- Claude can then use the tools via direct MCP calls

Dependencies are managed through the mcpskill package. Ensure it's installed:
```bash
cd /path/to/mcpskill
pip install -e .
```

## Debugging

If issues occur:
1. Test the downstream server directly
2. Check that environment variables are set
3. Verify the config YAML is valid
4. Look at skill logs (stderr output)

Set debug mode:
```bash
export MCPSKILL_LOG_LEVEL=DEBUG
```
