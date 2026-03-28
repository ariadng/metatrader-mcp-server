from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Dict, Any, Optional
from datetime import datetime # Ensure datetime is imported
# Removed unused import of pandas (pd)
from metatrader_client.exceptions import ConnectionError as MT5ConnectionError

router = APIRouter()

@router.get("/candles/latest", response_model=List[Dict[str, Any]])
async def candles_latest(
    request: Request,
    symbol_name: str = Query(..., description="Symbol name, e.g., 'EURUSD'"),
    timeframe: str = Query(..., description="Timeframe, e.g., 'M1', 'H1'"),
    count: int = Query(100, description="Number of candles to retrieve")
):
    """Fetch the latest N candles for a given symbol and timeframe.

    Input:
        symbol_name (str): The symbol, e.g., 'EURUSD'.
        timeframe (str): Timeframe string, e.g., 'M1', 'H1'.
        count (int): Number of candles to retrieve (default=100).

    Response:
        List[Dict[str, Any]]: List of candle records with keys 'time', 'open', 'high', 'low', 'close', 'volume'.
    """
    client = request.app.state.client
    try:
        df = client.market.get_candles_latest(symbol_name=symbol_name, timeframe=timeframe, count=count)
        return df.to_dict(orient="records")
    except MT5ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/candles/date", response_model=List[Dict[str, Any]])
async def get_candles_by_date_endpoint( # Choose a descriptive name
    request: Request,
    symbol_name: str = Query(..., description="Symbol name, e.g., 'EURUSD'"),
    timeframe: str = Query(..., description="Timeframe, e.g., 'M1', 'H1'"),
    date_from: datetime = Query(..., description="Start date and time (ISO 8601 format, e.g., 2023-01-01T00:00:00)"),
    date_to: datetime = Query(..., description="End date and time (ISO 8601 format, e.g., 2023-01-02T23:59:59)")
):
    """Fetch candles for a given symbol, timeframe, and date range.

    Input:
        symbol_name (str): The symbol, e.g., 'EURUSD'.
        timeframe (str): Timeframe string, e.g., 'M1', 'H1'.
        date_from (datetime): Start date and time for candles.
        date_to (datetime): End date and time for candles.

    Response:
        List[Dict[str, Any]]: List of candle records with keys 'time', 'open', 'high', 'low', 'close', 'volume'.
    """
    client = request.app.state.client
    try:
        df = client.market.get_candles_by_date(
            symbol_name=symbol_name,
            timeframe=timeframe,
            from_date=date_from,
            to_date=date_to
        )
        if df is None or df.empty:
            # Return empty list if no data, or handle as appropriate
            return []
        return df.to_dict(orient="records")
    except MT5ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e: # Catch potential ValueError from date parsing or client logic
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the exception for debugging
        # logger.error(f"Error fetching candles for {symbol_name} by date: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching candles by date for {symbol_name}: {str(e)}")

@router.get("/symbol/info/{symbol_name}", response_model=Dict[str, Any])
async def get_symbol_info_endpoint( # Choose a descriptive name like get_symbol_info_route or symbol_info
    request: Request,
    symbol_name: str # Path parameter
):
    """Get detailed information for a specific symbol.

    Input:
        symbol_name (str): The trading instrument symbol (e.g., "EURUSD").

    Response:
        Dict[str, Any]: A dictionary containing various details about the symbol.
                        The exact fields depend on the MetaTrader 5 platform's response
                        for `symbol_info()`.
    """
    client = request.app.state.client
    try:
        # The client.market.get_symbol_info() function likely returns an object
        # that might not be directly JSON serializable (e.g. MT5SymbolInfo).
        # It might have a ._asdict() method or similar, or you might need to
        # manually convert its fields to a dictionary if it's a custom class.
        # For now, assume it returns a dict or a Pydantic model that FastAPI can handle.
        info = client.market.get_symbol_info(symbol_name=symbol_name)
        if info is None: # Or however the client function indicates "not found"
            raise HTTPException(status_code=404, detail=f"Symbol {symbol_name} not found or no info available.")
        # If 'info' is an object with attributes, convert to dict:
        # Example: if hasattr(info, '_asdict'): info = info._asdict()
        # Or if it's a Pydantic model, FastAPI handles it.
        # If it's a simple class, you might need: info = info.__dict__ or vars(info)
        # For now, let's assume it's directly returnable or a Pydantic model.
        return info
    except MT5ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    # Specific exception for symbol not found if your client raises one
    # except SymbolNotFoundError as e: # Replace with actual exception if available
    #     raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log the exception for debugging
        # logger.error(f"Error fetching symbol info for {symbol_name}: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching info for {symbol_name}: {str(e)}")

@router.get("/price/{symbol_name}", response_model=Dict[str, Any])
async def symbol_price(
    request: Request,
    symbol_name: str,
    query_symbol_name: Optional[str] = Query(None, alias="symbol_name")
):
    """Get the latest price and tick data for a symbol.

    Input:
        symbol_name (str): The symbol to query (path parameter).
        query_symbol_name (Optional[str]): The symbol to query (query parameter, fallback).

    Response:
        Dict[str, Any]: {'bid': float, 'ask': float, 'last': float, 'volume': int, 'time': datetime}.
    """
    client = request.app.state.client
    # Use path parameter if it's not the literal '{symbol_name}', otherwise use query parameter
    actual_symbol_name = symbol_name if symbol_name != "{symbol_name}" else query_symbol_name
    
    if not actual_symbol_name:
        raise HTTPException(status_code=400, detail="Symbol name must be provided")
    
    try:
        return client.market.get_symbol_price(symbol_name=actual_symbol_name)
    except MT5ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/price", response_model=Dict[str, Any])
async def symbol_price_query(
    request: Request,
    symbol_name: str = Query(..., description="Symbol name, e.g., 'EURUSD'")
):
    """Get the latest price and tick data for a symbol using query parameter.

    Input:
        symbol_name (str): The symbol to query.

    Response:
        Dict[str, Any]: {'bid': float, 'ask': float, 'last': float, 'volume': int, 'time': datetime}.
    """
    client = request.app.state.client
    try:
        return client.market.get_symbol_price(symbol_name=symbol_name)
    except MT5ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols", response_model=List[str])
async def all_symbols(request: Request):
    """Get a list of all available market symbols.

    Input:
        None

    Response:
        List[str]: List of symbol names.
    """
    client = request.app.state.client
    try:
        return client.market.get_symbols()
    except MT5ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols/filter", response_model=List[str])
async def filter_symbols(
    request: Request,
    group: Optional[str] = Query(None, description="Filter pattern, e.g., '*USD*'")
):
    """Get a list of all available market symbols, optionally filtered by group.

    Input:
        group (Optional[str]): Filter pattern, e.g., '*USD*'.

    Response:
        List[str]: List of symbol names.
    """
    client = request.app.state.client
    try:
        return client.market.get_symbols(group=group)
    except MT5ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
