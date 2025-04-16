from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

try:
    import MetaTrader5 as mt5
except ImportError:
    raise ImportError("MetaTrader5 package is not installed. Please install it with: pip install MetaTrader5")

from ..exceptions import DealsHistoryError, ConnectionError

logger = logging.getLogger("MT5History")

def get_deals(
    connection,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    group: Optional[str] = None,
    ticket: Optional[int] = None,
    position: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get historical deals.
    """
    if not connection.is_connected():
        raise ConnectionError("Not connected to MetaTrader 5 terminal.")
    deals = None
    logger.debug(f"Retrieving deals with parameters: from_date={from_date}, to_date={to_date}, group={group}, ticket={ticket}, position={position}")
    try:
        if ticket is not None:
            logger.debug(f"Retrieving deals by ticket: {ticket}")
            deals = mt5.history_deals_get(ticket=ticket)
        elif position is not None:
            logger.debug(f"Retrieving deals by position: {position}")
            deals = mt5.history_deals_get(position=position)
        else:
            if from_date is None:
                from_date = datetime.now() - timedelta(days=30)
            if to_date is None:
                to_date = datetime.now()
            logger.debug(f"Retrieving deals by date range: {from_date} to {to_date}")
            if group is not None:
                deals = mt5.history_deals_get(from_date, to_date, group=group)
            else:
                deals = mt5.history_deals_get(from_date, to_date)
    except Exception as e:
        error_code = -1
        if hasattr(mt5, 'last_error'):
            error = mt5.last_error()
            if error and len(error) > 1:
                error_code = error[0]
        msg = f"Failed to retrieve deals history: {str(e)}"
        logger.error(msg)
        raise DealsHistoryError(msg, error_code)
    if deals is None:
        error = mt5.last_error()
        msg = f"Failed to retrieve deals history: {error[1]}"
        logger.error(msg)
        raise DealsHistoryError(msg, error[0])
    if len(deals) == 0:
        logger.info("No deals found with the specified parameters.")
        return []
    result = [deal._asdict() for deal in deals]
    logger.debug(f"Retrieved {len(result)} deals.")
    return result
