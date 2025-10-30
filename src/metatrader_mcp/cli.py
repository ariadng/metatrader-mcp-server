import click
from dotenv import load_dotenv
from metatrader_mcp.server import mcp

load_dotenv()

@click.command()
@click.option("--login", type=int, envvar="MT5_LOGIN", help="MT5 login ID")
@click.option("--password", envvar="MT5_PASSWORD", help="MT5 password")
@click.option("--server", envvar="MT5_SERVER", help="MT5 server name")
@click.option("--path", envvar="MT5_PATH", help="Path to MT5 terminal executable (optional, auto-detected if not provided)")
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio", envvar="MCP_TRANSPORT", help="Transport to use: 'stdio' for standard I/O (default), 'http' for Streamable HTTP transport")
@click.option("--host", default="127.0.0.1", envvar="MCP_HOST", help="Host for HTTP transport (ignored for stdio)")
@click.option("--port", default=8000, type=int, envvar="MCP_PORT", help="Port for HTTP transport (ignored for stdio)")
def main(login, password, server, path, transport, host, port):
    """Launch the MetaTrader MCP server."""
    
    # run the MCP server with the chosen transport
    if transport == "http":
        # Update settings with custom host and port
        mcp.settings.host = host
        mcp.settings.port = port
        
        # Run with Streamable HTTP transport
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()