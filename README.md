# SiYuan MCP

MCP server for [SiYuan](https://b3log.org/siyuan/) note-taking app, providing Claude Code with access to your notebooks, documents, and blocks.

## Setup

### Option 1: Global (all projects)

Add the SiYuan MCP server to your global Claude Code config with:

```bash
claude mcp add --global SiYuan \
  -e SIYUAN_URL=<YOUR-HOST>:6806 \
  -e SIYUAN_TOKEN=<YOUR-API-TOKEN> \
  -- uvx --from git+https://github.com/marc0todar0/siyuan-mcp siyuan-mcp
```

Replace `<YOUR-HOST>` and `<YOUR-API-TOKEN>` with your SiYuan instance URL and API token.

This will add the following to your `~/.claude.json`:

```json
"mcpServers": {
  "SiYuan": {
    "command": "uvx",
    "args": [
      "--from",
      "git+https://github.com/marc0todar0/siyuan-mcp",
      "siyuan-mcp"
    ],
    "env": {
      "SIYUAN_URL": "<YOUR-HOST>:6806",
      "SIYUAN_TOKEN": "<YOUR-API-TOKEN>"
    }
  }
}
```

### Option 2: Per-project

Add a `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "SiYuan": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/marc0todar0/siyuan-mcp",
        "siyuan-mcp"
      ],
      "env": {
        "SIYUAN_URL": "<YOUR-HOST>:6806",
        "SIYUAN_TOKEN": "<YOUR-API-TOKEN>"
      }
    }
  }
}
```
