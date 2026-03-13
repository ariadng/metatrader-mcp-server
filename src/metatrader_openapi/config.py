from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the OpenAPI interface.

    The values of these settings can be overridden by setting environment variables
    prefixed with `OPENAPI_`. For example, to change the `title` setting, set the
    `OPENAPI_TITLE` environment variable.

    Attributes:
        openapi_url (str): The URL path for the OpenAPI JSON schema.
        docs_url (str): The URL path for the OpenAPI documentation.
        redoc_url (str): The URL path for the ReDoc interface.
        title (str): The title of the API.
        version (str): The version of the API.

    """

    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    title: str = "MetaTrader MCP API"
    version: str = "0.3.2"

    # Load from env vars prefixed with OPENAPI_
    model_config = SettingsConfigDict(env_prefix="OPENAPI_")
