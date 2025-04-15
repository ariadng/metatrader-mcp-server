from .get_all_positions import get_all_positions
from .close_position import close_position

def close_all_profittable_positions(connection):
    """
    Close all open positions that are currently profittable.

    Args:
        connection: The connection object to the MetaTrader platform.

    Returns:
        A dictionary containing an error flag, a message, and the number of positions closed.
    """
    
    positions = get_all_positions(connection)
    positions = positions[positions["profit"] >= 0]
    count = 0
    for id in positions["id"]:
        close_position(connection, id)
        count += 1
    return { "error": False, "message": f"Close {count} profittable positions success", "data": None }
