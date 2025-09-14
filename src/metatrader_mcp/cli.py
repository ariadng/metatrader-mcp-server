import click
import os
from dotenv import load_dotenv
from metatrader_mcp.server import mcp

@click.command()
@click.option("--login", required=True, type=int, help="MT5 login ID")
@click.option("--password", required=True, help="MT5 password")
@click.option("--server", required=True, help="MT5 server name")
@click.option("--transport", type=click.Choice(["stdio", "http"], case_sensitive=False), default="stdio", show_default=True, help="Transport to serve MCP over")
@click.option("--host", default="0.0.0.0", show_default=True, help="HTTP bind host (only used when --transport http)")
@click.option("--port", default=8000, show_default=True, type=int, help="HTTP bind port (only used when --transport http)")
def main(login, password, server, transport, host, port):
    """Launch the MetaTrader MCP server over stdio or HTTP."""
    load_dotenv()
    # override env vars if provided via CLI
    os.environ["login"] = str(login)
    os.environ["password"] = password
    os.environ["server"] = server

    transport = (transport or "stdio").lower()
    if transport == "http":
        # Prefer native HTTP helpers if available
        try:
            run_http = getattr(mcp, "run_http")
        except Exception:
            run_http = None
        if callable(run_http):
            return run_http(host=host, port=port)
        # FastMCP exposes a StreamableHTTP server; use its ASGI app with uvicorn for host/port binding
        streamable_app_fn = getattr(mcp, "streamable_http_app", None)
        if callable(streamable_app_fn):
            try:
                import uvicorn  # type: ignore
            except Exception as e:
                raise RuntimeError("uvicorn is required for HTTP mode but is not installed") from e
            asgi_app = streamable_app_fn()
            return uvicorn.run(asgi_app, host=host, port=port)
        # As a last resort, run the async StreamableHTTP server (no host/port control)
        run_streamable_async = getattr(mcp, "run_streamable_http_async", None)
        if callable(run_streamable_async):
            import asyncio
            return asyncio.run(run_streamable_async())
        # Try run(transport="http") without host/port
        try:
            return mcp.run(transport="http")
        except Exception as e:
            raise RuntimeError("FastMCP does not expose HTTP helpers; cannot run HTTP server") from e
    # Default: stdio
    return mcp.run(transport="stdio")

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
