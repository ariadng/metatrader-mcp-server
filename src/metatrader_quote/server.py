import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosed

from metatrader_client.client import MT5Client

logger = logging.getLogger(__name__)


class QuoteServer:
    """WebSocket server that streams live MT5 tick data to connected clients.

    Args:
        client: Connected MT5Client instance.
        symbols: List of symbol names to stream.
        host: Host to bind the WebSocket server.
        port: Port to bind the WebSocket server.
        poll_interval_ms: Tick polling interval in milliseconds.
    """

    def __init__(
        self,
        *,
        client: MT5Client,
        symbols: List[str],
        host: str = "0.0.0.0",
        port: int = 8765,
        poll_interval_ms: int = 100,
    ):
        self._client = client
        self._symbols = symbols
        self._host = host
        self._port = port
        self._poll_interval = poll_interval_ms / 1000.0
        self._clients: Set[ServerConnection] = set()
        self._last_ticks: Dict[str, Dict[str, Any]] = {}
        self._symbol_digits: Dict[str, int] = {}
        self._symbol_points: Dict[str, float] = {}
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def _handler(self, websocket: ServerConnection) -> None:
        """Handle a new WebSocket connection."""
        self._clients.add(websocket)
        logger.info("Client connected (%d total)", len(self._clients))
        try:
            # Send connected message
            connected_msg = json.dumps({
                "type": "connected",
                "symbols": self._symbols,
                "poll_interval_ms": int(self._poll_interval * 1000),
            })
            await websocket.send(connected_msg)

            # Send cached ticks
            for symbol, tick in self._last_ticks.items():
                await websocket.send(json.dumps(tick))

            # Keep connection alive until client disconnects
            async for _ in websocket:
                pass
        except ConnectionClosed:
            pass
        finally:
            self._clients.discard(websocket)
            logger.info("Client disconnected (%d remaining)", len(self._clients))

    async def _broadcast(self, message: str) -> None:
        """Send a message to all connected clients."""
        if not self._clients:
            return
        await asyncio.gather(
            *(client.send(message) for client in self._clients),
            return_exceptions=True,
        )

    def _tick_changed(self, symbol: str, tick: Dict[str, Any]) -> bool:
        """Check if tick data has changed since last poll."""
        last = self._last_ticks.get(symbol)
        if last is None:
            return True
        return (
            last.get("bid") != tick.get("bid")
            or last.get("ask") != tick.get("ask")
            or last.get("volume") != tick.get("volume")
        )

    def _load_symbol_meta(self) -> None:
        """Load static symbol metadata (digits, point) from MT5."""
        for symbol in self._symbols:
            try:
                info = self._client.market.get_symbol_info(symbol)
                self._symbol_digits[symbol] = info.get("digits", 5)
                self._symbol_points[symbol] = info.get("point", 0.00001)
                logger.info(
                    "Symbol %s: digits=%d, point=%s",
                    symbol, self._symbol_digits[symbol], self._symbol_points[symbol],
                )
            except Exception as e:
                self._symbol_digits[symbol] = 5
                self._symbol_points[symbol] = 0.00001
                logger.warning("Could not get metadata for %s, using defaults: %s", symbol, e)

    def _fetch_tick(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch tick data and point values for a symbol (runs in executor thread)."""
        try:
            tick = self._client.market.get_symbol_price(symbol)
            info = self._client.market.get_symbol_info(symbol)
            tick["trade_tick_value_profit"] = info.get("trade_tick_value_profit", 0)
            tick["trade_tick_value_loss"] = info.get("trade_tick_value_loss", 0)
            return tick
        except Exception as e:
            logger.warning("Error fetching %s: %s", symbol, e)
            return None

    async def _poll_ticks(self) -> None:
        """Continuously poll MT5 for tick data and broadcast changes."""
        loop = asyncio.get_running_loop()
        while True:
            for symbol in self._symbols:
                try:
                    tick_data = await loop.run_in_executor(
                        self._executor, self._fetch_tick, symbol
                    )
                except Exception as e:
                    logger.error("Executor error for %s: %s", symbol, e)
                    continue

                if tick_data is None:
                    error_msg = json.dumps({
                        "type": "error",
                        "symbol": symbol,
                        "message": "Symbol not found or data unavailable",
                    })
                    await self._broadcast(error_msg)
                    continue

                # Format tick time as ISO string
                tick_time = tick_data.get("time")
                if isinstance(tick_time, datetime):
                    time_str = tick_time.isoformat()
                else:
                    time_str = datetime.now(tz=timezone.utc).isoformat()

                bid = tick_data.get("bid", 0)
                ask = tick_data.get("ask", 0)
                digits = self._symbol_digits.get(symbol, 5)
                point = self._symbol_points.get(symbol, 0.00001)
                spread = round(ask - bid, digits)
                spread_points = round(spread / point) if point > 0 else 0

                tick_msg = {
                    "type": "tick",
                    "symbol": symbol,
                    "bid": bid,
                    "ask": ask,
                    "bid_string": f"{bid:.{digits}f}",
                    "ask_string": f"{ask:.{digits}f}",
                    "spread": spread,
                    "spread_string": f"{spread:.{digits}f}",
                    "spread_points": spread_points,
                    "buy_point_value": tick_data.get("trade_tick_value_profit", 0),
                    "sell_point_value": tick_data.get("trade_tick_value_loss", 0),
                    "volume": tick_data.get("volume", 0),
                    "time": time_str,
                }

                if self._tick_changed(symbol, tick_msg):
                    self._last_ticks[symbol] = tick_msg
                    await self._broadcast(json.dumps(tick_msg))

            await asyncio.sleep(self._poll_interval)

    async def run(self) -> None:
        """Start the WebSocket server and tick polling loop."""
        logger.info(
            "Quote server starting on ws://%s:%d (symbols: %s, interval: %dms)",
            self._host,
            self._port,
            ", ".join(self._symbols),
            int(self._poll_interval * 1000),
        )
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._load_symbol_meta)
        async with serve(self._handler, self._host, self._port):
            await self._poll_ticks()
