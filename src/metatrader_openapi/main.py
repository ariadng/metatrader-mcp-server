# pylint: disable=import-error
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from .routers import router as api_router
import os
import argparse
import uvicorn
from dotenv import load_dotenv
from metatrader_mcp.utils import init
from contextlib import asynccontextmanager

# Instantiate settings
settings = Settings()

# Define a lifespan handler for MT5 client lifecycle
@asynccontextmanager
async def lifespan(app):
    # Load environment variables
    load_dotenv()
    # Use MT5_* variables as source of truth
    login = os.getenv("MT5_LOGIN")
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER")
    path = os.getenv("MT5_PATH")
    client = init(login, password, server, path)
    app.state.client = client
    yield
    if client:
        client.disconnect()

# Initialize FastAPI app with OpenAPI metadata and lifespan
app = FastAPI(
    title=settings.title,
    version=settings.version,
    openapi_url=settings.openapi_url,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

# Enable CORS for Open WebUI and other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
def strip_prefix(route: APIRoute) -> str:
    op_id = route.name
    prefix = "api_v1_"
    if op_id.startswith(prefix):
        op_id = op_id[len(prefix):]
    return op_id
app.include_router(api_router, prefix="/api/v1", generate_unique_id_function=strip_prefix)

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="MetaTrader OpenAPI server")
    parser.add_argument("--login", type=int, default=None, help="MT5 login (or set MT5_LOGIN env var)")
    parser.add_argument("--password", default=None, help="MT5 password (or set MT5_PASSWORD env var)")
    parser.add_argument("--server", default=None, help="MT5 server address (or set MT5_SERVER env var)")
    parser.add_argument("--path", default=None, help="Path to MT5 terminal executable (optional, auto-detected if not provided)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8000, help="Bind port")
    args = parser.parse_args()
    
    # Use CLI args if provided, otherwise fall back to environment variables
    login = args.login or (int(os.getenv("MT5_LOGIN")) if os.getenv("MT5_LOGIN") else None) # type: ignore
    password = args.password or os.getenv("MT5_PASSWORD")
    server = args.server or os.getenv("MT5_SERVER")
    path = args.path or os.getenv("MT5_PATH")
    
    # Set environment variables for the lifespan handler to use
    if login:
        os.environ["MT5_LOGIN"] = str(login)
    if password:
        os.environ["MT5_PASSWORD"] = password
    if server:
        os.environ["MT5_SERVER"] = server
    if path:
        os.environ["MT5_PATH"] = path
 
    uvicorn.run(
        "metatrader_openapi.main:app",
        host=args.host,
        port=args.port,
        reload=False,
    )

if __name__ == "__main__":
    main()
