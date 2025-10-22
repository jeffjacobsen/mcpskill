# MCP Orchestrator Skill

A Claude Code Agent Skill that provides direct access to MCP (Model Context Protocol) servers without loading tool definitions into context.

## What is This?

This skill wraps MCPSkill functionality as a Claude Code Skill, enabling:

- **Zero context usage**: MCP tools aren't loaded into Claude's context
- **Direct access**: Simple passthrough to MCP servers (no intermediate LLM)
- **Fast execution**: Single hop to MCP server
- **SDK compatibility**: Works with MCP servers that require API keys and SDKs
- **Zero server overhead**: Direct Python execution, no MCP server process needed
- **Auto-activation**: Claude invokes this skill automatically when relevant

## Installation

### 1. Install MCPSkill

First, ensure the MCPSkill package is installed:

```bash
cd /path/to/mcpskill
pip install -e .
```

### 2. Set Up the Skill

The skill is already in this repository at `.claude/skills/mcp-orchestrator/`. You have two options:

#### Option A: Project-Level Skill (Recommended for this project)
Already done! The skill is in `.claude/skills/` and will work for this project.

#### Option B: Personal Skill (Use across all projects)
Copy the skill to your personal skills directory:

```bash
# macOS/Linux
mkdir -p ~/.claude/skills
cp -r .claude/skills/mcp-orchestrator ~/.claude/skills/

# Windows
mkdir %USERPROFILE%\.claude\skills
xcopy .claude\skills\mcp-orchestrator %USERPROFILE%\.claude\skills\mcp-orchestrator /E /I
```

### 3. Create Your Configuration

Copy the example config and customize it:

```bash
cd .claude/skills/mcp-orchestrator
cp config.example.yaml config.yaml
```

Edit `config.yaml` to configure the downstream MCP server (no LLM configuration needed).

### 4. Set Environment Variables (if needed)

Some downstream servers require API keys:

```bash
# For GitHub MCP server
export GITHUB_TOKEN="your-github-token"

# For other MCP servers, check their documentation
```

**Note**: No API keys are needed for MCPSkill itself (no intermediate LLM).

## Usage

Once installed, Claude Code will automatically activate this skill when you make requests related to MCP servers. You don't need to explicitly invoke it.

### Example Interactions

**Filesystem Operations:**
```
You: List all Python files in my Documents folder
Claude: [Activates mcp-orchestrator skill]
Claude: [Connects to filesystem MCP, shows available tools]
Claude: [Uses tools to list files]
Claude: I found 23 Python files in your Documents folder:
  - script1.py
  - data_analysis.py
  ...
```

**Database Queries:**
```
You: Show me users who signed up this month
Claude: [Activates mcp-orchestrator skill with database config]
Claude: [Connects to database MCP, queries data]
Claude: There are 47 new users this month. Here are the details:
  ...
```

**GitHub Integration:**
```
You: Create an issue for the bug we just discussed
Claude: [Activates mcp-orchestrator skill with GitHub config]
Claude: [Uses GitHub MCP tools]
Claude: I've created issue #123 in your repository: "Fix authentication bug"
```

### Manual Testing

You can test the skill directly:

**List available tools:**
```bash
python .claude/skills/mcp-orchestrator/orchestrate.py config.yaml "What tools are available?"
```

**Call a specific tool:**
```bash
# Example: List directory contents
python .claude/skills/mcp-orchestrator/orchestrate.py config.yaml '{"tool": "list_directory", "arguments": {"path": "/tmp"}}'

# Example: Search for files
python .claude/skills/mcp-orchestrator/orchestrate.py config.yaml '{"tool": "search_files", "arguments": {"path": "/tmp", "pattern": "*.py"}}'

# Example: Read a file
python .claude/skills/mcp-orchestrator/orchestrate.py config.yaml '{"tool": "read_text_file", "arguments": {"path": "/tmp/test.txt"}}'
```

## Configuration Examples

### Filesystem Assistant

```yaml
name: filesystem-assistant
description: "Direct access to filesystem operations"

downstream:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/Documents"]
  env: {}
```

### Database Assistant

```yaml
name: database-assistant
description: "Direct access to SQLite database"

downstream:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-sqlite", "myapp.db"]
  env: {}
```

### GitHub Assistant

```yaml
name: github-assistant
description: "Direct access to GitHub operations"

downstream:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-github"]
  env:
    GITHUB_TOKEN: ${GITHUB_TOKEN}
```

## How It Works

### Tool Discovery and Execution

1. **Claude detects relevance**: Based on your request, Claude determines this skill is needed
2. **Skill activation**: Claude loads the SKILL.md instructions
3. **Step 1 - Discover tools**:
   - Claude runs: `orchestrate.py config.yaml "list tools"`
   - Returns: All available tools with descriptions and parameters
4. **Step 2 - Claude decides**: Claude Code analyzes tools and selects appropriate one(s)
5. **Step 3 - Execute tool**:
   - Claude runs: `orchestrate.py config.yaml '{"tool": "tool_name", "arguments": {...}}'`
   - MCPSkill calls the tool on the downstream MCP server
   - Returns: Tool execution results
6. **Step 4 - Present results**: Claude formats and presents results to you

### Two Request Formats

**Format 1: Plain text (lists tools)**
```bash
python orchestrate.py config.yaml "What can you do?"
# Returns: List of all available tools
```

**Format 2: JSON (calls a tool)**
```bash
python orchestrate.py config.yaml '{"tool": "list_directory", "arguments": {"path": "/tmp"}}'
# Returns: Directory listing
```

Claude Code uses Format 1 to discover tools, then Format 2 to execute them.

## Benefits Over Traditional MCP

| Aspect | Traditional MCP | MCP Orchestrator Skill |
|--------|----------------|------------------------|
| Tools in context | All tools loaded | None (auto-invoked) |
| Token usage | High | Minimal (zero) |
| Process overhead | MCP server running | Direct execution |
| API key handling | Through MCP config | Direct env vars |
| Complexity | Medium | Low |
| Latency | Single hop | Single hop |
| Extra LLM cost | No | No |

## Troubleshooting

### Skill Not Activating

- Check that `SKILL.md` exists in the skill directory
- Verify the description field matches your use case
- Try mentioning "MCP server" or specific service (filesystem, database) explicitly

### Import Errors

```
Error: MCPSkill package not found
```

**Solution**: Install MCPSkill:
```bash
cd /path/to/mcpskill
pip install -e .
```

### Connection Errors

```
Error: Cannot connect to downstream server
```

**Solution**:
- Test the downstream server directly: `npx -y @modelcontextprotocol/server-filesystem /tmp`
- Check that the command in `config.yaml` is correct
- Verify required packages (Node.js/npm for npx commands) are installed

### Debug Mode

Enable verbose logging:

```bash
export MCPSKILL_LOG_LEVEL=DEBUG
```

Then make your request in Claude Code. Check the stderr output for detailed logs.

## Configuration Reference

See [config.example.yaml](config.example.yaml) for a fully documented configuration with multiple examples.

### Key Fields

- **name**: Identifier for this skill instance
- **description**: Human-readable description (helps Claude understand when to use it)
- **downstream.command**: Command to run the MCP server
- **downstream.args**: Arguments for the command
- **downstream.env**: Environment variables for the server (use ${VAR} syntax)

## Advanced Usage

### Multiple Configurations

You can have multiple config files for different use cases:

```bash
.claude/skills/mcp-orchestrator/
├── SKILL.md
├── orchestrate.py
├── config-filesystem.yaml
├── config-database.yaml
└── config-github.yaml
```

Then specify which config to use:
```
You: Use the database config to show me recent users
```

Claude will use `config-database.yaml`.

### Custom MCP Servers

The skill works with any MCP server:

```yaml
downstream:
  command: python
  args: ["-m", "my_custom_mcp_server"]
  env:
    CUSTOM_API_KEY: ${CUSTOM_API_KEY}
```

## What's Different from MCProxy?

MCPSkill is a simplified version of MCProxy:

| Feature | MCProxy | MCPSkill |
|---------|---------|----------|
| MCP Server Mode | ✅ Yes | ❌ No |
| Intermediate LLM | ✅ Yes | ❌ No |
| Claude Code Skills | ✅ Yes | ✅ Yes (optimized) |
| Configuration | Complex (LLM settings) | Simple (just MCP server) |
| Use Case | Complex orchestration | Direct access |

If you need intermediate LLM orchestration for complex tool routing, use the full MCProxy package instead.

## Contributing

This skill is part of the MCPSkill project. See the main [README](../../../README.md) for contribution guidelines.

## License

Apache 2.0

## Resources

- [MCPSkill Documentation](../../../README.md)
- [Claude Code Skills Docs](https://docs.claude.com/en/docs/claude-code/skills)
- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)

---

Built with [MCPSkill](../../../README.md) - Direct MCP wrapper for Claude Code
