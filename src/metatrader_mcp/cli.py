import click
import os
from dotenv import load_dotenv
from metatrader_mcp.server import mcp

@click.command()
@click.option("--login", required=True, type=int, help="MT5 login ID")
@click.option("--password", required=True, help="MT5 password")
@click.option("--server", required=True, help="MT5 server name")
@click.option("--portable", default=None, help="MT5 in Portable Mode")
@click.option("--path", default=None, help="Path to MT5 terminal executable (optional, auto-detected if not provided)")
def main(login, password, server, path, portable):
    """Launch the MetaTrader MCP STDIO server."""
    load_dotenv()
    # override env vars if provided via CLI
    os.environ["login"] = str(login)
    os.environ["password"] = password
    os.environ["server"] = server

    if path:
        os.environ["path"] = path
    if portable == "True":
        os.environ["portable"] = portable

    
    # run STDIO transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
