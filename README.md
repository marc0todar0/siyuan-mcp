## Config - global mcp
Add this at the end of .claude.json
```
  "mcpServers": {
    "SiYuan": {
      "command": "uvx",
      "args": [
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "<PATH-TO-THIS-REPO>/siyuan-mcp/siyuan_mcp/server.py"
      ],
      "env": {
        "SIYUAN_URL": "<YOUR-HOST>:6806",
        "SIYUAN_TOKEN": "<YOUR-API-TOKEN>"
      }
    }
  }
```
