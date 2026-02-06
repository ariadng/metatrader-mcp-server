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
    # Load environment and support uppercase or lowercase vars
    load_dotenv()
    login = os.getenv("LOGIN", os.getenv("login"))
    password = os.getenv("PASSWORD", os.getenv("password"))
    server = os.getenv("SERVER", os.getenv("server"))
    path = os.getenv("PATH", os.getenv("path"))
    portable = os.getenv("PORTABLE", os.getenv("portable"))
    client = init(login, password, server, path, portable)
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
    parser.add_argument("--login", required=True, help="MT5 login")
    parser.add_argument("--password", required=True, help="MT5 password")
    parser.add_argument("--server", required=True, help="MT5 server address")
    parser.add_argument("--path", default=None, help="Path to MT5 terminal executable (optional, auto-detected if not provided)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8000, help="Bind port")
    args = parser.parse_args()

    # set both uppercase and lowercase env vars for CLI
    os.environ["LOGIN"] = args.login
    os.environ["PASSWORD"] = args.password
    os.environ["SERVER"] = args.server
    os.environ["login"] = args.login
    os.environ["password"] = args.password
    os.environ["server"] = args.server
    if args.path:
        os.environ["PATH"] = args.path
        os.environ["path"] = args.path

    uvicorn.run(
        "metatrader_openapi.main:app",
        host=args.host,
        port=args.port,
        reload=True,
    )

if __name__ == "__main__":
    main()
