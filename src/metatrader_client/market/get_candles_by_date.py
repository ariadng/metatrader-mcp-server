from typing import Optional, Union
import pandas as pd
from datetime import datetime, timezone, timedelta
import MetaTrader5 as mt5
from ..types import Timeframe
from ..exceptions import SymbolNotFoundError, InvalidTimeframeError, MarketDataError
from .get_symbols import get_symbols

def get_candles_by_date(
    connection,
    symbol_name: str,
    timeframe: str,
    from_date: Optional[Union[str, datetime]] = None,
    to_date: Optional[Union[str, datetime]] = None,
) -> pd.DataFrame:
    if not get_symbols(connection, symbol_name):
        raise SymbolNotFoundError(f"Symbol '{symbol_name}' not found")
    tf = Timeframe.get(timeframe)
    if tf is None:
        raise InvalidTimeframeError(f"Invalid timeframe: '{timeframe}'")
    from_datetime = None
    to_datetime = None
    def parse_date(date_str, is_to_date=False):
        if isinstance(date_str, datetime):
            if date_str.tzinfo is None:
                return date_str.replace(tzinfo=timezone.utc)
            return date_str
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(date_str, fmt)
                if fmt == "%Y-%m-%d":
                    if is_to_date:
                        dt = dt.replace(hour=23, minute=59)
                    else:
                        dt = dt.replace(hour=0, minute=0)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        raise ValueError(f"Invalid date format: {date_str}. Expected 'yyyy-MM-dd' or 'yyyy-MM-dd HH:mm'")
    if from_date:
        from_datetime = parse_date(from_date)
    if to_date:
        to_datetime = parse_date(to_date, is_to_date=True)
    if from_datetime and to_datetime and from_datetime > to_datetime:
        from_datetime, to_datetime = to_datetime, from_datetime
    candles = None
    if from_datetime and to_datetime:
        candles = mt5.copy_rates_range(symbol_name, tf, from_datetime, to_datetime)
    elif from_datetime:
        candles = mt5.copy_rates_from(symbol_name, tf, from_datetime, 1000)
    elif to_datetime:
        lookback_days = 30
        start_date = to_datetime - timedelta(days=lookback_days)
        candles = mt5.copy_rates_range(symbol_name, tf, start_date, to_datetime)
    else:
        candles = mt5.copy_rates_from_pos(symbol_name, tf, 0, 1000)
    if candles is None or len(candles) == 0:
        raise MarketDataError(f"Failed to retrieve historical data for symbol '{symbol_name}' with timeframe '{timeframe}'")
    df = pd.DataFrame(candles)
    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
    df = df.sort_values('time', ascending=False)
    return df
