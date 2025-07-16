[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/ariadng-metatrader-mcp-server-badge.png)](https://mseep.ai/app/ariadng-metatrader-mcp-server)

# MetaTrader MCP Server

[![PyPI version](https://img.shields.io/pypi/v/metatrader-mcp-server.svg?style=flat&color=blue)](https://pypi.org/project/metatrader-mcp-server/)

This is a Model Context Protocol (MCP) server built with Python to enable AI LLMs to trade using MetaTrader platform.

![MetaTrader MCP Server](https://yvkbpmmzjmfqjxusmyop.supabase.co/storage/v1/object/public/github//metatrader-mcp-server-1.png)

## Disclaimer

**Financial trading involves significant risk, and the developers of this package disclaim any liability for any losses or profits; this package is provided solely to facilitate MetaTrader 5 trade executions via AI LLMs using the Model Context Protocol (MCP). By using this package, you assume all risks and agree not to hold the developers liable or to initiate any legal action for any damages, losses, or profits.**

## Updates

- May 5, 2025: Use broker-based filling modes (0.2.5)
- April 23, 2025: Published to PyPi (0.2.0) 
- April 16, 2025: We have our first minor version release (0.1.0) 

## Installation Guide

Make sure you have Python version 3.10+ and MetaTrader 5 terminal installed in your workspace. Then install the package:

```bash
pip install metatrader-mcp-server
```

Then you need to enable algorithmic trading on MetaTrader 5 terminal. Open `Tools > Options` and check `Allow algorithmic trading`.

## Claude Desktop Integration

To use this package to enable trading operations via Claude Desktop app, please add this into your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "metatrader": {
      "command": "metatrader-mcp-server",
      "args": [
        "--login",    "<YOUR_MT5_LOGIN>",
        "--password", "<YOUR_MT5_PASSWORD>",
        "--server",   "<YOUR_MT5_SERVER>"
      ]
    }
  }
}
```

## Other LLMs using Open WebUI

You can use this MCP server with other LLMs such as OpenAI's GPT by using its HTTP server and Open WebUI.

To start, make sure you have installed the package. Then, run the server:

```
metatrader-http-server --login <YOUR_MT5_LOGIN> --password <YOUR_MT5_PASSWORD> --server <YOUR_MT5_SERVER> --host 0.0.0.0 --port 8000
```

It will launch HTTP server locally on port 8000 and automatically launch MetaTrader 5 terminal.

On Open WebUI settings page, navigate to **Tools** menu. Then click plus button on "Manage Tool Servers". Add `http://localhost:8000` (or whatever you set your port is).

![Open WebUI - Add Connection](https://yvkbpmmzjmfqjxusmyop.supabase.co/storage/v1/object/public/github//openwebui-add-tools.png)

If all is well, you can now access the tools via chat using available models, such as `gpt-4o` or `o4-mini`.

![Open WebUI - Chat](https://yvkbpmmzjmfqjxusmyop.supabase.co/storage/v1/object/public/github//openwebui-macos.png)

## Project Roadmap

For full version checklist, see [version-checklist.md](docs/roadmap/version-checklist.md).

| Task | Status | Done | Tested |
|------|--------|------|--------|
| Connect to MetaTrader 5 terminal | Finished | ✅ | ✅ |
| Develop MetaTrader client module | Finished | ✅ | ✅ |
| Develop MCP Server module | Finished | ✅ | ✅ |
| Implement MCP tools | Finished | ✅ | ✅ |
| Publish to PyPi | Finished | ✅ | ✅ |
| Claude Desktop integration | Finished | ✅ | ✅ |
| OpenAPI server | Finished | ✅ | ✅ |
| Open WebUI integration | Finished | ✅ | ✅ |
| Google ADK integration | On progress | - | - |

## Developer Documentation

For developers, see [Developer's Documentation](docs/README.md).
