#!/usr/bin/env python3
import os
import argparse
import logging
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional, Union

from metatrader_mcp.utils import init, get_client

# ────────────────────────────────────────────────────────────────────────────────
# 1) Lifespan context definition
# ────────────────────────────────────────────────────────────────────────────────
@dataclass
class AppContext:
	client: str

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:

	try:
		client = init(
			os.getenv("login"),
			os.getenv("password"),
			os.getenv("server"),
			os.getenv("path"),
			os.getenv("portable")
		)
		yield AppContext(client=client)
	finally:
		client.disconnect()

# ────────────────────────────────────────────────────────────────────────────────
# 2) Instantiate FastMCP as `mcp` (must be named `mcp`, `server`, or `app`)
# ────────────────────────────────────────────────────────────────────────────────
mcp = FastMCP(
	"metatrader",
	lifespan=app_lifespan,
	dependencies=[],
)

# ────────────────────────────────────────────────────────────────────────────────
# 3) Register tools with @mcp.tool()
# ────────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_account_info(ctx: Context) -> dict:
	"""Get account information (balance, equity, profit, margin level, free margin, account type, leverage, currency)."""
	client = get_client(ctx)
	return client.account.get_trade_statistics()

@mcp.tool()
def get_deals(ctx: Context, from_date: Optional[str] = None, to_date: Optional[str] = None, symbol: Optional[str] = None) -> str:
	"""Get historical deals as CSV. Date input in format: 'YYYY-MM-DD'."""
	client = get_client(ctx)
	df = client.history.get_deals_as_dataframe(from_date=from_date, to_date=to_date, group=symbol)
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def get_orders(ctx: Context, from_date: Optional[str] = None, to_date: Optional[str] = None, symbol: Optional[str] = None) -> str:
	"""Get historical orders as CSV. Date input in format: 'YYYY-MM-DD'"""
	client = get_client(ctx)
	df = client.history.get_orders_as_dataframe(from_date=from_date, to_date=to_date, group=symbol)
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

def get_candles_by_date(ctx: Context, symbol_name: str, timeframe: str, from_date: str = None, to_date: str = None) -> str:
	"""Get candle data for a symbol in a given timeframe and date range as CSV. Date input in format: ISO 8601 or 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'."""
	client = get_client(ctx)
	df = client.market.get_candles_by_date(symbol_name=symbol_name, timeframe=timeframe, from_date=from_date, to_date=to_date)
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def get_candles_latest(ctx: Context, symbol_name: str, timeframe: str, count: int = 100) -> str:
	"""Get the latest N candles for a symbol and timeframe as CSV."""
	client = get_client(ctx)
	df = client.market.get_candles_latest(symbol_name=symbol_name, timeframe=timeframe, count=count)
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def get_symbol_price(ctx: Context, symbol_name: str) -> dict:
	"""Get the latest price info for a symbol as a dictionary."""
	client = get_client(ctx)
	return client.market.get_symbol_price(symbol_name=symbol_name)

@mcp.tool()
def get_all_symbols(ctx: Context) -> list:
	"""Get a list of all available market symbols."""
	client = get_client(ctx)
	return client.market.get_symbols()

@mcp.tool()
def get_symbols(ctx: Context, group: Optional[str] = None) -> list:
	"""
	Get a list of available market symbols. Filter symbols by group pattern (e.g., '*USD*').
	"""
	client = get_client(ctx)
	return client.market.get_symbols(group=group)

# ────────────────────────────────────────────────────────────────────────────────
# Order module tools
# ────────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_all_positions(ctx: Context) -> list:
	"""Get all open positions."""
	client = get_client(ctx)
	df = client.order.get_all_positions()
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def get_positions_by_symbol(ctx: Context, symbol: str) -> list:
	"""Get open positions for a specific symbol."""
	client = get_client(ctx)
	df = client.order.get_positions_by_symbol(symbol=symbol)
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def get_positions_by_id(ctx: Context, id: Union[int, str]) -> list:
	"""Get open positions by ID."""
	client = get_client(ctx)
	df = client.order.get_positions_by_id(id=id)
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def get_all_pending_orders(ctx: Context) -> list:
	"""Get all pending orders."""
	client = get_client(ctx)
	df = client.order.get_all_pending_orders()
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def get_pending_orders_by_symbol(ctx: Context, symbol: str) -> list:
	"""Get pending orders for a specific symbol."""
	client = get_client(ctx)
	df = client.order.get_pending_orders_by_symbol(symbol=symbol)
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def get_pending_orders_by_id(ctx: Context, id: Union[int, str]) -> list:
	"""Get pending orders by id."""
	client = get_client(ctx)
	df = client.order.get_pending_orders_by_id(id=id)
	return df.to_csv() if hasattr(df, 'to_csv') else str(df)

@mcp.tool()
def place_market_order(ctx: Context, symbol: str, volume: float, type: str) -> dict:
	"""
	Place a market order. Parameters:
		symbol: Symbol name (e.g., 'EURUSD')
		volume: Lot size. (e.g. 1.5)
		type: Order type ('BUY' or 'SELL')
	"""
	client = get_client(ctx)
	return client.order.place_market_order(symbol=symbol, volume=volume, type=type)

@mcp.tool()
def place_pending_order(ctx: Context, symbol: str, volume: float, type: str, price: float, stop_loss: Optional[Union[int, float]] = 0.0, take_profit: Optional[Union[int, float]] = 0.0) -> dict:
	"""
	Place a pending order. Parameters:
		symbol: Symbol name (e.g., 'EURUSD')
		volume: Lot size. (e.g. 1.5)
		type: Order type ('BUY', 'SELL').
		price: Pending order price.
		stop_loss (optional): Stop loss price.
		take_profit (optional): Take profit price.
	"""
	client = get_client(ctx)
	return client.order.place_pending_order(symbol=symbol, volume=volume, type=type, price=price, stop_loss=stop_loss, take_profit=take_profit)

@mcp.tool()
def modify_position(ctx: Context, id: Union[int, str], stop_loss: Optional[Union[int, float]] = None, take_profit: Optional[Union[int, float]] = None) -> dict:
	"""Modify an open position by ID."""
	client = get_client(ctx)
	return client.order.modify_position(id=id, stop_loss=stop_loss, take_profit=take_profit)
@mcp.tool()
def modify_pending_order(ctx: Context, id: Union[int, str], price: Optional[Union[int, float]] = None, stop_loss: Optional[Union[int, float]] = None, take_profit: Optional[Union[int, float]] = None) -> dict:
	"""Modify a pending order by ID."""
	client = get_client(ctx)
	return client.order.modify_pending_order(id=id, price=price, stop_loss=stop_loss, take_profit=take_profit)
@mcp.tool()
def close_position(ctx: Context, id: Union[int, str]) -> dict:
	"""Close an open position by ID."""
	client = get_client(ctx)
	return client.order.close_position(id=id)

@mcp.tool()
def cancel_pending_order(ctx: Context, id: Union[int, str]) -> dict:
	"""Cancel a pending order by ID."""
	client = get_client(ctx)
	return client.order.cancel_pending_order(id=id)

@mcp.tool()
def close_all_positions(ctx: Context) -> dict:
	"""Close all open positions."""
	client = get_client(ctx)
	return client.order.close_all_positions()

@mcp.tool()
def close_all_positions_by_symbol(ctx: Context, symbol: str) -> dict:
	"""Close all open positions for a specific symbol."""
	client = get_client(ctx)
	return client.order.close_all_positions_by_symbol(symbol=symbol)

@mcp.tool()
def close_all_profitable_positions(ctx: Context) -> dict:
	"""Close all profitable positions."""
	client = get_client(ctx)
	return client.order.close_all_profitable_positions()

@mcp.tool()
def close_all_losing_positions(ctx: Context) -> dict:
	"""Close all losing positions."""
	client = get_client(ctx)
	return client.order.close_all_losing_positions()

@mcp.tool()
def cancel_all_pending_orders(ctx: Context) -> dict:
	"""Cancel all pending orders."""
	client = get_client(ctx)
	return client.order.cancel_all_pending_orders()

@mcp.tool()
def cancel_pending_orders_by_symbol(ctx: Context, symbol: str) -> dict:
	"""Cancel all pending orders for a specific symbol."""
	client = get_client(ctx)
	return client.order.cancel_pending_orders_by_symbol(symbol=symbol)

if __name__ == "__main__":
	load_dotenv()
	parser = argparse.ArgumentParser(description="MetaTrader MCP Server")
	parser.add_argument("--login",    type=str, help="MT5 login")
	parser.add_argument("--password", type=str, help="MT5 password")
	parser.add_argument("--server",   type=str, help="MT5 server name")
	parser.add_argument("--path",     type=str, help="Path to MT5 terminal executable (optional)")
	parser.add_argument("--portable",     type=str, help="MT5 terminal portable mode (optional)")

	args = parser.parse_args()

	# inject into lifespan via env vars
	if args.login:    os.environ["login"]    = args.login
	if args.password: os.environ["password"] = args.password
	if args.server:   os.environ["server"]   = args.server
	if args.path:     os.environ["path"]     = args.path
	if args.portable: os.environ["portable"]     = args.portable

	# run the MCP server (must call mcp.run)
	mcp.run(
		transport="stdio"
	)
