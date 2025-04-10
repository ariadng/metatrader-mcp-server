#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MT5 Connection Playground
A simple script to demonstrate connecting to and disconnecting from MetaTrader 5
"""
import sys
import io

# Backup the original stdout
original_stdout = sys.stdout

# Redirect stdout to suppress output temporarily
sys.stdout = io.StringIO()

import MetaTrader5 as mt5
import time
from MetaTraderMCPServer.client.client import MT5Client
from MetaTraderMCPServer.client.connection import MT5Connection
from MetaTraderMCPServer.client.functions.calculate_margin import calculate_margin
from MetaTraderMCPServer.client.functions.calculate_profit import calculate_profit
from MetaTraderMCPServer.client.functions.send_order import send_order
from MetaTraderMCPServer.client.types import OrderType, TradeRequestActions
from tabulate import tabulate

# Restore the original stdout
sys.stdout = original_stdout

def init():
    config = { "login": 240294046, "password": "ExnessDemo123!", "server": "Exness-MT5Trial6" }
    try:
        client = MT5Client(config)
        client.connect()
    except Exception as e:
        print(f"❌ Error: {e}")
    return client

def main():
    client = init()
  
    # gold = client.market.get_candles_by_date("XAUUSD", "D1", "2025-04-10 00:00", "2025-01-10 23:59")
    # print(gold)

    print("\n\n")

    # # Get all pending orders
    # all_orders = client.orders.get_all_pending_orders()
    # print(tabulate(all_orders, headers='keys', tablefmt='fancy_grid'))

    # # Get pending orders for a specific symbol
    # xauusd_orders = client.orders.get_pending_orders_by_symbol("XAUUSD")
    # print(tabulate(xauusd_orders, headers='keys', tablefmt='fancy_grid'))

    # # Get pending orders for a specific currency
    # usd_orders = client.orders.get_pending_orders_by_currency("USD")
    # print(tabulate(usd_orders, headers='keys', tablefmt='fancy_grid'))

    # # Get a specific pending order by ID
    # order = client.orders.get_pending_orders_by_id(1642078070)
    # print(tabulate(order, headers='keys', tablefmt='fancy_grid'))

    # all_positions = client.orders.get_all_positions()
    # print(tabulate(all_positions, headers='keys', tablefmt='fancy_grid'))

    # print("\n\n")

    # xauusd_positions = client.orders.get_positions_by_symbol("XAUUSD")
    # print(tabulate(xauusd_positions, headers='keys', tablefmt='fancy_grid'))

    # print("\n\n")

    # position = client.orders.get_position_by_id(1651409559)
    # print(tabulate(position, headers='keys', tablefmt='fancy_grid'))

    # print("==============")
    # print("OPEN POSITIONS")
    # print("==============\n")
    # orders = client.orders.get_positions()
    # print(tabulate(orders, headers='keys', tablefmt='fancy_grid'))

    # print("\n")

    # print("==============")
    # print("PENDING ORDERS")
    # print("==============\n")
    # orders = client.orders.get_pending_orders(symbol_name="XAUUSD")
    # print(tabulate(orders, headers='keys', tablefmt='fancy_grid'))
    
    
    # print("\n\n")
    
    # # Test the calculate_margin function
    # print("====================")
    # print("💰 MARGIN CALCULATION")
    # print("====================\n")
    
    # # Test with different order types and symbols
    # symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    # volume = 0.1
    
    # margin_results = []
    
    # for symbol in symbols:
    #     # Get current price
    #     tick = mt5.symbol_info_tick(symbol)
    #     if tick is None:
    #         print(f"❌ Failed to get tick data for {symbol}")
    #         continue
            
    #     # Calculate for BUY order
    #     buy_margin = calculate_margin(OrderType.BUY, symbol, volume, tick.ask)
        
    #     # Calculate for SELL order
    #     sell_margin = calculate_margin(OrderType.SELL, symbol, volume, tick.bid)
        
    #     # Add results to table
    #     if buy_margin is not None and sell_margin is not None:
    #         margin_results.append({
    #             "Symbol": symbol,
    #             "Buy Price": tick.ask,
    #             "Buy Margin": f"{buy_margin:.2f}",
    #             "Sell Price": tick.bid,
    #             "Sell Margin": f"{sell_margin:.2f}"
    #         })
    
    # # Display results in a pretty table
    # print(tabulate(margin_results, headers='keys', tablefmt='fancy_grid'))
    
    # # Test the calculate_profit function
    # print("\n====================")
    # print("💵 PROFIT CALCULATION")
    # print("====================\n")
    
    # # Define the pip movement for profit calculation
    # pip_movement = 100  # 100 pips
    # profit_results = []
    
    # for symbol in symbols:
    #     # Get current price
    #     tick = mt5.symbol_info_tick(symbol)
    #     if tick is None:
    #         print(f"❌ Failed to get tick data for {symbol}")
    #         continue
        
    #     # Get symbol info for point value
    #     symbol_info = mt5.symbol_info(symbol)
    #     if symbol_info is None:
    #         print(f"❌ Failed to get symbol info for {symbol}")
    #         continue
            
    #     # Calculate pip value (usually 0.0001 for 4-digit symbols, 0.00001 for 5-digit)
    #     point = symbol_info.point
    #     pip_size = 10 * point  # 10 points = 1 pip for most forex pairs
        
    #     # Buy scenario (open at ask, close higher)
    #     buy_open = tick.ask
    #     buy_close = buy_open + (pip_movement * pip_size)
    #     buy_profit = calculate_profit("BUY", symbol, volume, buy_open, buy_close)
        
    #     # Sell scenario (open at bid, close lower)
    #     sell_open = tick.bid
    #     sell_close = sell_open - (pip_movement * pip_size)
    #     sell_profit = calculate_profit("SELL", symbol, volume, sell_open, sell_close)
        
    #     # Add results to table
    #     if buy_profit is not None and sell_profit is not None:
    #         profit_results.append({
    #             "Symbol": symbol,
    #             "Movement": f"{pip_movement} pips",
    #             "Buy Profit": f"{buy_profit:.2f}",
    #             "Sell Profit": f"{sell_profit:.2f}",
    #             "Profit per Pip": f"{(buy_profit/pip_movement):.2f}"
    #         })
    
    # # Display results in a pretty table
    # print(tabulate(profit_results, headers='keys', tablefmt='fancy_grid'))
    # print("\nNote: Profit calculations assume the specified pip movement in favorable direction")
    
    # Test the send_order function
    print("\n====================")
    print("📈 SEND ORDER TEST")
    print("====================\n")
    
    # # Get current price
    # tick = mt5.symbol_info_tick("XAUUSD")
    
    # if tick is None:
    #     print(f"❌ Failed to get tick data for XAUUSD")
    # else:
    #     # Send the order
    #     order_result = send_order(
    #         connection=client._connection,
    #         symbol="XAUUSD",
    #         volume=0.1,
    #         sl=3250,
    #         tp=3100,
    #         order_type="SELL",
    #         price=tick.ask,
    #         action=TradeRequestActions.DEAL
    #     )
    #     print(order_result)

    order_result = send_order(
        connection=client._connection,
        symbol="XAUUSD",
        volume=0.1,
        stop_loss=3500,
        take_profit=4500,
        order_type="SELL_LIMIT",
        price=4000,
        action=TradeRequestActions.PENDING
    )
    print(order_result)

    client.disconnect()

if __name__ == "__main__":
    main()
