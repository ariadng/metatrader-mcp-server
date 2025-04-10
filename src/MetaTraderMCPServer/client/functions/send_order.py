"""
MetaTrader 5 order sending function.

This module provides functionality to send trading orders to MetaTrader 5.
It supports various trading operations including market orders, pending orders,
modification of positions and orders, and position closing.
"""

import MetaTrader5 as mt5
import pandas as pd
from typing import Optional, Union, Dict
from datetime import datetime

from ..market import MT5Market
from ..types import (
	TradeRequest,
	TradeRequestActions,
	OrderType,
	OrderFilling,
	OrderTime
)


def send_order(
	connection,
	action: Union[str, int, TradeRequestActions],
	symbol: str,
	volume: float,
	order_type: Union[str, int, OrderType],
	price: float = 0.0,
	stop_loss: float = 0.0,
	take_profit: float = 0.0,
	deviation: int = 20,
	magic: int = 0,
	comment: str = "",
	position: int = 0,
	position_by: int = 0,
	order: int = 0,
	expiration: Optional[datetime] = None,
	type_filling: Optional[Union[str, int, OrderFilling]] = None,
	type_time: Optional[Union[str, int, OrderTime]] = None,
	stoplimit: float = 0.0
) -> Dict:
	"""
	Send a trading order to MetaTrader 5.
	
	This function creates and sends a trading request to MetaTrader 5 using the order_send
	function. It supports all types of trading operations including market orders, pending
	orders, position modifications, and order cancellations.
	
	Args:
		connection: MetaTrader 5 connection object
		action: Trading operation type (DEAL, PENDING, SLTP, MODIFY, REMOVE, CLOSE_BY)
		symbol: Trading instrument name (e.g., "EURUSD")
		volume: Trade volume in lots
		order_type: Order type (BUY, SELL, BUY_LIMIT, etc.)
		price: Order price (required for pending orders, ignored for market in some execution modes)
		stop_loss: Stop Loss level (optional)
		take_profit: Take Profit level (optional)
		deviation: Maximum acceptable price deviation in points (for market orders)
		magic: Expert Advisor ID (magic number)
		comment: Order comment
		position: Position ticket (required for position operations)
		position_by: Opposite position ticket (for CLOSE_BY operations)
		order: Order ticket (required for order modification)
		expiration: Order expiration time (for orders with type_time=SPECIFIED)
		type_filling: Order filling type (FOK, IOC, RETURN)
		type_time: Order lifetime type (GTC, DAY, SPECIFIED)
		stoplimit: Stop limit price (for STOP_LIMIT orders)
	
	Returns:
		Dictionary containing:
		- 'success': Boolean indicating if the operation was successful
		- 'message': Human-readable message describing the result
		
	Notes:
		Different parameters are required depending on the action:
		- DEAL (market order): symbol, volume, order_type (BUY/SELL)
		- PENDING: symbol, volume, price, order_type
		- SLTP: position, sl and/or tp
		- MODIFY: order, and new parameters to modify
		- REMOVE: order
		- CLOSE_BY: position, position_by
	"""
	# 1. Validate the input parameters based on the action type
	#   - Check if the action is valid and supported
	#   - Verify that the required parameters are provided for the given action
	#   - Validate the data types and ranges of the input parameters

	_market = MT5Market(connection)

	# Validate action
	action = TradeRequestActions.validate(action)
	
	# Validate order type
	order_type = OrderType.validate(order_type)

	# Validate symbol
	if (len(_market.get_symbols(symbol)) == 0):
		return { "success": False, "message": "Invalid symbol" }

	# Ensure symbol is available
	if not mt5.symbol_select(symbol, True):
		return { "success": False, "message": f"Failed to select {symbol}" }

	# Validate volume
	if (volume <= 0 or volume > 100):
		return { "success": False, "message": "Invalid volume" }
	else:
		volume = float(volume)

	# Validate price
	price = float(price)
	if not isinstance(price, float):
		return { "success": False, "message": "Invalid price" }

	# Validate TP and SL
	stop_loss = float(stop_loss)
	take_profit = float(take_profit)
	if not isinstance(stop_loss, float) or not isinstance(take_profit, float):
		return { "success": False, "message": "Invalid SL or TP" }
	if order_type in [OrderType.BUY, OrderType.BUY_LIMIT, OrderType.BUY_STOP]:
		if stop_loss >= price:
			return { "success": False, "message": "Stop loss must be below the price" }
		if take_profit <= price:
			return { "success": False, "message": "Take profit must be above the price" }
		if stop_loss > take_profit:
			return { "success": False, "message": "Stop loss must be below the take profit" }
		
	elif order_type in [OrderType.SELL, OrderType.SELL_LIMIT, OrderType.SELL_STOP]:
		if stop_loss <= price:
			return { "success": False, "message": "Stop loss must be above the price" }
		if take_profit >= price:
			return { "success": False, "message": "Take profit must be below the price" }
		if stop_loss < take_profit:
			return { "success": False, "message": "Stop loss must be above the take profit" }

	# Comment
	comment = comment if comment else "MCP"

	match action:

		# ------------------------------
		# Market execution (BUY or SELL)
		# ------------------------------
		case TradeRequestActions.DEAL:
			
			if order_type not in [OrderType.BUY, OrderType.SELL]:
				return { "success": False, "message": "Invalid order type, must be BUY or SELL" }

			request = {
				"symbol": symbol,
				"volume": volume,
				"type": order_type,
				"price": price,
				"action": action,
				"type_filling": mt5.ORDER_FILLING_FOK,
				"comment": comment,
				"sl": sl,
				"tp": tp,
				"deviation": 20
			}
			
			mt5.order_send(request)

			error_code, error_description = mt5.last_error()
			
			if error_code < 0:
				return { "success": False, "message": f"Error {error_code}: {error_description}" }

			return { "success": True, "message": "Order sent successfully" }

		# ----------------------------------------------------------
		# Pending order (BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP)
		# ----------------------------------------------------------
		case TradeRequestActions.PENDING:

			if order_type not in [OrderType.BUY_LIMIT, OrderType.SELL_LIMIT, OrderType.BUY_STOP, OrderType.SELL_STOP]:
				return { "success": False, "message": "Invalid order type, must be BUY_LIMIT, SELL_LIMIT, BUY_STOP, or SELL_STOP" }

			tick = mt5.symbol_info_tick(symbol)
			if tick is not None:
				print(tick)
				print(price)
				match order_type:
					case OrderType.BUY_LIMIT:
						if price > tick.ask:
							return { "success": False, "message": "Invalid price, must be above current ask" }
					case OrderType.SELL_LIMIT:
						if price < tick.bid:
							return { "success": False, "message": "Invalid price, must be below current bid" }
					case OrderType.BUY_STOP:
						if price < tick.ask:
							return { "success": False, "message": "Invalid price, must be above current ask" }
					case OrderType.SELL_STOP:
						if price > tick.bid:
							return { "success": False, "message": "Invalid price, must be below current bid" }

			request = {
				"action": action,
				"symbol": symbol,
				"volume": volume,
				"type": order_type,
				"price": price,
				"sl": stop_loss,
				"tp": take_profit,
				"deviation": deviation,
				"comment": comment,
				"type_time": OrderTime.SPECIFIED.value if expiration else OrderTime.GTC.value,
				"expiration": expiration if expiration else 0,
				"type_filling": OrderFilling.FOK.value,
			}

			mt5.order_send(request)

			error_code, error_description = mt5.last_error()
			
			if error_code < 0:
				return { "success": False, "message": f"Error {error_code}: {error_description}" }

			return { "success": True, "message": "Order sent successfully" }

		# --------------------
		# Modify order (SL/TP)
		# --------------------    
		case TradeRequestActions.SLTP:
			print("MODIFY SL/TP")
			
		# ------------
		# Modify order
		# ------------
		case TradeRequestActions.MODIFY:
			print("MODIFY")

		# --------
		# Close by
		# --------   
		case TradeRequestActions.CLOSE_BY:
			print("CLOSE BY")

	# HANDLE BASED ON THE ACTION TYPE

	# 2. If order type is BUY or SELL: Check the margin requirement based on account information
	#   - Use get_account_info function from MT5Account
	#   - Use calculate_margin function to determine whether the margin req is satisfied
	
	# Etc...

	# CONTINUE

	# 3. Create a TradeRequest object with the provided parameters
	#   - Initialize a TradeRequest object with the given action and symbol
	#   - Set the order type, volume, price, and other parameters as needed
	#   - Add any additional parameters required for the specific action

	# 4. Check the request validation before sending it.
	#   - Use order_check function from MetaTrader5 library
	#   - Validate the request parameters and return an error message if invalid
	
	# 5. Use the connection object to send the TradeRequest to MetaTrader 5
	#   - Establish a connection to the MetaTrader 5 server using the provided connection object
	#   - Send the TradeRequest object to the server using the order_send function
	#   - Handle any exceptions or errors that may occur during the sending process
	
	# 6. Handle the response from MetaTrader 5 and extract the result
	#   - Receive the response from the MetaTrader 5 server
	#   - Extract the result object from the response, which contains the outcome of the operation
	#   - Check the result object for any errors or warnings
	
	# 7. Create a dictionary with the result and return it
	#   - Initialize a dictionary to store the result of the operation
	#   - Add the success flag, return code, and return message to the dictionary
	#   - Include the original request and result object in the dictionary for further reference
	#   - Return the dictionary containing the result of the operation
	
	# 8. Return the result dictionary
	return {
		'success': False,
		'return_code': -1,
		'return_message': 'Unknown error',
		'request': None,
		'result': None
	}
