# MCPSkill - Direct MCP Wrapper for Claude Code Skills

A lightweight Python wrapper that enables Claude Code to interact with MCP (Model Context Protocol) servers through skills, without loading tool definitions into context.

## What is MCPSkill?

MCPSkill provides a simple bridge between Claude Code's skill system and MCP servers. Instead of loading all MCP tools into Claude's context (which uses tokens), MCPSkill exposes MCP servers through a skill that Claude can invoke when needed.

### Key Benefits

- **Zero Context Usage**: MCP tool definitions don't load into Claude Code's context
- **Auto-Activation**: Claude Code automatically invokes the skill when relevant
- **Simple Configuration**: Just point to an MCP server, no LLM orchestration needed
- **Fast Execution**: Direct passthrough to MCP servers (no intermediate LLM)
- **Minimal Dependencies**: Only requires `mcp`, `pydantic`, and `pyyaml`

### Architecture

```
┌─────────────────────────┐
│     Claude Code         │  ← Auto-invokes skill when user mentions MCP
│  (0 tools in context)   │     keywords (filesystem, database, etc.)
└────────┬────────────────┘
         │ Direct Python execution
┌────────▼──────────────────┐
│  orchestrate.py           │  ← Simple CLI wrapper
│  (skill entry point)      │
└────────┬──────────────────┘
         │
┌────────▼──────────────────┐
│  DirectExecutor           │  ← Lists available tools, no LLM
│  (executor.py)            │     orchestration needed
└────────┬──────────────────┘
         │ JSON-RPC via MCP
┌────────▼─────────┐
│ Downstream MCP   │  ← filesystem, database, GitHub, etc.
│    Server        │
└──────────────────┘
```

## When to Use MCPSkill

✅ **Use MCPSkill when:**
- You want Claude Code to access MCP servers without loading tool schemas
- The MCP server has simple, well-documented tools
- You want minimal latency and no extra API costs
- You're working with standard MCP servers (filesystem, SQLite, etc.)

❌ **Don't use MCPSkill when:**
- You need complex multi-tool orchestration logic
- You want an MCP server for Claude Desktop (use MCProxy instead)
- You need intermediate LLM reasoning for tool selection

## Installation

### Step 1: Install MCPSkill

```bash
cd /path/to/mcpskill
pip install -e .
```

### Step 2: Skill is Already Configured

The skill is located at `.claude/skills/mcp-orchestrator/` in this repository.

**For project-level use**: You're all set! The skill works in this project.

**For global use** (across all projects):

```bash
# macOS/Linux
cp -r .claude/skills/mcp-orchestrator ~/.claude/skills/

# Windows
xcopy .claude\skills\mcp-orchestrator %USERPROFILE%\.claude\skills\mcp-orchestrator /E /I
```

### Step 3: Configure

```bash
cd .claude/skills/mcp-orchestrator
cp config.example.yaml config.yaml
# Edit config.yaml for your use case
```

## Configuration

MCPSkill uses simple YAML configuration files:

```yaml
# config.yaml
name: filesystem-assistant
description: "Access filesystem operations via MCP"

downstream:
  command: npx
  args:
    - "-y"
    - "@modelcontextprotocol/server-filesystem"
    - "/Users/username/Documents"
  env: {}  # Optional environment variables for the MCP server
```

### Configuration Examples

#### Filesystem Access

```yaml
name: filesystem
description: "File and directory operations"

downstream:
  command: npx
  args:
    - "-y"
    - "@modelcontextprotocol/server-filesystem"
    - "/path/to/directory"
```

#### SQLite Database

```yaml
name: database
description: "SQLite database queries"

downstream:
  command: npx
  args:
    - "-y"
    - "@modelcontextprotocol/server-sqlite"
    - "/path/to/database.db"
```

#### GitHub Integration

```yaml
name: github
description: "GitHub repository and issue management"

downstream:
  command: npx
  args:
    - "-y"
    - "@modelcontextprotocol/server-github"
  env:
    GITHUB_TOKEN: ${GITHUB_TOKEN}  # Loaded from environment
```

## Usage

Once installed, Claude Code will automatically activate the skill when you make relevant requests.

### Example: Filesystem Operations

**Your request:**
> List all Python files in the /tmp directory

**What happens:**
1. Claude recognizes "filesystem" in the skill description
2. Claude invokes: `python orchestrate.py config.yaml "List all Python files in /tmp"`
3. MCPSkill connects to the filesystem MCP server
4. Returns available tools and their descriptions
5. Claude can then use the MCP tools directly

### Example: Database Queries

**Your request:**
> Show me all users who signed up in the last 7 days

**What happens:**
1. Skill activates based on configuration
2. MCPSkill connects to SQLite MCP server
3. Returns available database query tools
4. Claude executes the appropriate queries

## Manual Testing

You can test the skill directly from the command line:

```bash
cd .claude/skills/mcp-orchestrator
python orchestrate.py config.yaml "What can you help me with?"
```

## Debugging

Enable debug logging:

```bash
export MCPSKILL_LOG_LEVEL=DEBUG
```

Then check stderr output for detailed logs.

### Common Issues

**Problem**: `Error: MCPSkill package not found`

**Solution**:
```bash
cd /path/to/mcpskill
pip install -e .
```

**Problem**: `Cannot connect to downstream server`

**Solutions**:
1. Test the MCP server command directly
2. Check that Node.js/npm is installed (for npx-based servers)
3. Verify environment variables are set

**Problem**: Skill doesn't activate

**Solutions**:
1. Check that `SKILL.md` exists in `.claude/skills/mcp-orchestrator/`
2. Verify the description mentions relevant keywords
3. Try explicitly mentioning "MCP" or the server type in your request
4. Restart Claude Code

## Comparison with MCProxy

MCPSkill is a simplified version of MCProxy, optimized for Claude Code skills:

| Feature | MCProxy (Full) | MCPSkill (Simplified) |
|---------|----------------|----------------------|
| **MCP Server Mode** | ✅ Yes | ❌ No |
| **Intermediate LLM** | ✅ Yes (configurable) | ❌ No |
| **Claude Code Skills** | ✅ Yes | ✅ Yes (optimized) |
| **Token Usage** | Minimal (0 in context) | Minimal (0 in context) |
| **Latency** | Medium (2 hops) | Low (1 hop) |
| **API Cost** | Medium (double LLM) | Low (no extra LLM) |
| **Configuration** | Complex (LLM settings) | Simple (just MCP config) |
| **Use Case** | Complex orchestration | Simple direct access |

## Project Structure

```
mcpskill/
├── src/mcpskill/
│   ├── __init__.py
│   ├── client.py       # MCP client for connecting to servers
│   ├── config.py       # YAML configuration loader
│   ├── types.py        # Pydantic models
│   └── executor.py     # Direct tool execution (no LLM)
│
├── .claude/skills/mcp-orchestrator/
│   ├── SKILL.md               # Skill definition for Claude Code
│   ├── README.md              # Skill-specific documentation
│   ├── config.example.yaml    # Example configuration
│   └── orchestrate.py         # Entry point script
│
├── pyproject.toml      # Package configuration
└── README.md           # This file
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type checking
mypy src/
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Resources

- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)

## License

Apache 2.0

## FAQ

### Q: How is this different from loading MCP servers directly into Claude Code?

**A**: Claude Code can load MCP servers directly, but this puts all tool definitions in context (using tokens). MCPSkill wraps MCP servers in a skill that Claude auto-invokes only when needed, keeping your context clean.

### Q: Can I use this with Claude Desktop?

**A**: No, MCPSkill is specifically designed for Claude Code's skill system. For Claude Desktop, use the full MCProxy package with MCP server mode.

### Q: Do I need an API key for orchestration?

**A**: No! MCPSkill doesn't use an intermediate LLM, so you don't need any API keys beyond what the downstream MCP server requires.

### Q: Can I use multiple MCP servers?

**A**: Yes, create multiple config files and copy the skill folder with different names (e.g., `mcp-filesystem`, `mcp-database`). Each gets its own configuration.

### Q: What if I need complex orchestration logic?

**A**: Use the full MCProxy package which includes an intermediate LLM for intelligent tool routing. MCPSkill is optimized for simple, direct access.
