from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the WebSocket Quote Server.

    The values of these settings can be overridden by setting environment variables
    prefixed with `QUOTE_`. For example, to change the `port` setting, set the
    `QUOTE_PORT` environment variable.

    Attributes:
        host (str): Host to bind the WebSocket server.
        port (int): Port to bind the WebSocket server.
        symbols (str): Comma-separated list of symbols to stream.
        poll_interval_ms (int): Polling interval in milliseconds.
    """

    host: str = "0.0.0.0"
    port: int = 8765
    symbols: str = "XAUUSD,USOIL,GBPUSD,USDJPY,EURUSD,BTCUSD"
    poll_interval_ms: int = 100

    model_config = SettingsConfigDict(env_prefix="QUOTE_")
