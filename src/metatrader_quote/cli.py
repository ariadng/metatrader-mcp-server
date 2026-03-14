import asyncio
import logging

import click
from dotenv import load_dotenv

from metatrader_mcp.utils import init
from metatrader_quote.config import Settings
from metatrader_quote.server import QuoteServer

logger = logging.getLogger(__name__)


@click.command()
@click.option("--login", required=True, type=int, help="MT5 login ID")
@click.option("--password", required=True, help="MT5 password")
@click.option("--server", required=True, help="MT5 server name")
@click.option("--path", default=None, help="Path to MT5 terminal executable (optional, auto-detected if not provided)")
@click.option("--host", default=None, help="Host to bind (default: 0.0.0.0, env: QUOTE_HOST)")
@click.option("--port", default=None, type=int, help="Port to bind (default: 8765, env: QUOTE_PORT)")
@click.option("--symbols", default=None, help="Comma-separated symbols to stream (env: QUOTE_SYMBOLS)")
@click.option("--poll-interval", default=None, type=int, help="Poll interval in ms (default: 100, env: QUOTE_POLL_INTERVAL_MS)")
def main(login, password, server, path, host, port, symbols, poll_interval):
    """Launch the MetaTrader WebSocket Quote Server."""
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    settings = Settings()

    # CLI flags override settings
    host = host or settings.host
    port = port if port is not None else settings.port
    symbols_str = symbols or settings.symbols
    poll_interval_ms = poll_interval if poll_interval is not None else settings.poll_interval_ms

    symbol_list = [s.strip() for s in symbols_str.split(",") if s.strip()]

    client = init(login=login, password=password, server=server, path=path)
    if client is None:
        raise click.ClickException("Failed to initialize MT5 client. Check credentials.")

    try:
        quote_server = QuoteServer(
            client=client,
            symbols=symbol_list,
            host=host,
            port=port,
            poll_interval_ms=poll_interval_ms,
        )
        asyncio.run(quote_server.run())
    finally:
        client.disconnect()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
