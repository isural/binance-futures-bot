"""
Example usage of Binance Futures Trading Bot
This script demonstrates how to use the bot to place orders and check account information.
"""

from binance_futures_bot import BinanceFuturesBot
import config


def main():
    """
    Example usage of the Binance Futures Trading Bot
    """
    
    # Initialize the bot
    print("Initializing Binance Futures Bot...")
    bot = BinanceFuturesBot(
        api_key=config.API_KEY,
        api_secret=config.API_SECRET,
        testnet=config.USE_TESTNET,
        recv_window=config.RECV_WINDOW
    )
    
    # Example 1: Get account information
    print("\n" + "="*50)
    print("Example 1: Getting Account Information")
    print("="*50)
    try:
        balance = bot.get_balance()
        print(f"Total Wallet Balance: {balance['total_wallet_balance']}")
        print(f"Available Balance: {balance['available_balance']}")
        print(f"Total Unrealized Profit: {balance['total_unrealized_profit']}")
    except Exception as e:
        print(f"Error getting account info: {e}")
    
    # Example 2: Get current price
    print("\n" + "="*50)
    print("Example 2: Getting Current Price")
    print("="*50)
    symbol = "BTCUSDT"
    try:
        price = bot.get_current_price(symbol)
        print(f"Current {symbol} price: ${price:,.2f}")
    except Exception as e:
        print(f"Error getting price: {e}")
    
    # Example 3: Get symbol information
    print("\n" + "="*50)
    print("Example 3: Getting Symbol Information")
    print("="*50)
    try:
        symbol_info = bot.get_symbol_info(symbol)
        if symbol_info:
            print(f"Symbol: {symbol_info['symbol']}")
            print(f"Status: {symbol_info['status']}")
            print(f"Base Asset: {symbol_info['baseAsset']}")
            print(f"Quote Asset: {symbol_info['quoteAsset']}")
            print(f"Price Precision: {symbol_info.get('pricePrecision', 'N/A')}")
            print(f"Quantity Precision: {symbol_info.get('quantityPrecision', 'N/A')}")
    except Exception as e:
        print(f"Error getting symbol info: {e}")
    
    # Example 4: Get position information
    print("\n" + "="*50)
    print("Example 4: Getting Position Information")
    print("="*50)
    try:
        positions = bot.get_position_info(symbol)
        if positions:
            for pos in positions:
                if float(pos.get('positionAmt', 0)) != 0:
                    print(f"Symbol: {pos['symbol']}")
                    print(f"Position Amount: {pos['positionAmt']}")
                    print(f"Entry Price: {pos['entryPrice']}")
                    print(f"Unrealized PnL: {pos['unRealizedProfit']}")
                    print(f"Leverage: {pos['leverage']}x")
        else:
            print("No open positions")
    except Exception as e:
        print(f"Error getting position info: {e}")
    
    # Example 5: Place a market buy order (UNCOMMENT TO USE)
    print("\n" + "="*50)
    print("Example 5: Market Buy Order (COMMENTED OUT FOR SAFETY)")
    print("="*50)
    print("Uncomment the code below to place a real order")
    """
    try:
        quantity = 0.001  # Adjust this to your desired quantity
        print(f"Placing market BUY order for {quantity} {symbol}...")
        result = bot.buy_market(symbol=symbol, quantity=quantity)
        print(f"Order placed successfully!")
        print(f"Order ID: {result.get('orderId')}")
        print(f"Status: {result.get('status')}")
        print(f"Executed Quantity: {result.get('executedQty')}")
    except Exception as e:
        print(f"Error placing order: {e}")
    """
    
    # Example 6: Place a limit sell order (UNCOMMENT TO USE)
    print("\n" + "="*50)
    print("Example 6: Limit Sell Order (COMMENTED OUT FOR SAFETY)")
    print("="*50)
    print("Uncomment the code below to place a real order")
    """
    try:
        quantity = 0.001  # Adjust this to your desired quantity
        limit_price = 50000.0  # Adjust this to your desired price
        print(f"Placing limit SELL order for {quantity} {symbol} at ${limit_price}...")
        result = bot.sell_limit(
            symbol=symbol,
            quantity=quantity,
            price=limit_price,
            time_in_force="GTC"
        )
        print(f"Order placed successfully!")
        print(f"Order ID: {result.get('orderId')}")
        print(f"Status: {result.get('status')}")
    except Exception as e:
        print(f"Error placing order: {e}")
    """
    
    # Example 7: Get open orders
    print("\n" + "="*50)
    print("Example 7: Getting Open Orders")
    print("="*50)
    try:
        open_orders = bot.get_open_orders(symbol)
        if open_orders:
            print(f"Found {len(open_orders)} open order(s):")
            for order in open_orders:
                print(f"  Order ID: {order['orderId']}")
                print(f"  Symbol: {order['symbol']}")
                print(f"  Side: {order['side']}")
                print(f"  Type: {order['type']}")
                print(f"  Quantity: {order['origQty']}")
                print(f"  Price: {order.get('price', 'N/A')}")
                print(f"  Status: {order['status']}")
                print()
        else:
            print("No open orders")
    except Exception as e:
        print(f"Error getting open orders: {e}")
    
    # Example 8: Advanced order placement
    print("\n" + "="*50)
    print("Example 8: Advanced Order Placement")
    print("="*50)
    print("You can use the place_order method directly for full control:")
    print("""
    # Example: Place a stop-loss order
    result = bot.place_order(
        symbol="BTCUSDT",
        side="SELL",
        order_type="STOP_MARKET",
        quantity=0.001,
        stop_price=45000.0,
        close_position=False,
        working_type="MARK_PRICE"
    )
    """)


def interactive_trading():
    """
    Interactive trading function - allows user to input parameters
    """
    print("\n" + "="*50)
    print("Interactive Trading Mode")
    print("="*50)
    
    # Initialize bot
    bot = BinanceFuturesBot(
        api_key=config.API_KEY,
        api_secret=config.API_SECRET,
        testnet=config.USE_TESTNET,
        recv_window=config.RECV_WINDOW
    )
    
    # Get user inputs
    symbol = input("Enter trading symbol (e.g., BTCUSDT): ").upper().strip()
    side = input("Enter side (BUY/SELL): ").upper().strip()
    order_type = input("Enter order type (MARKET/LIMIT): ").upper().strip()
    quantity = float(input("Enter quantity: "))
    
    price = None
    time_in_force = None
    
    if order_type == "LIMIT":
        price = float(input("Enter limit price: "))
        time_in_force = input("Enter time in force (GTC/IOC/FOK/GTX) [default: GTC]: ").upper().strip() or "GTC"
    
    # Display order details for confirmation
    print("\n" + "-"*50)
    print("Order Details:")
    print(f"Symbol: {symbol}")
    print(f"Side: {side}")
    print(f"Type: {order_type}")
    print(f"Quantity: {quantity}")
    if price:
        print(f"Price: {price}")
    if time_in_force:
        print(f"Time in Force: {time_in_force}")
    print("-"*50)
    
    confirm = input("\nConfirm order? (yes/no): ").lower().strip()
    
    if confirm != "yes":
        print("Order cancelled.")
        return
    
    # Place the order
    try:
        print("\nPlacing order...")
        if order_type == "MARKET":
            if side == "BUY":
                result = bot.buy_market(symbol, quantity)
            else:
                result = bot.sell_market(symbol, quantity)
        else:
            if side == "BUY":
                result = bot.buy_limit(symbol, quantity, price, time_in_force)
            else:
                result = bot.sell_limit(symbol, quantity, price, time_in_force)
        
        print("\nOrder placed successfully!")
        print(f"Order ID: {result.get('orderId')}")
        print(f"Status: {result.get('status')}")
        print(f"Symbol: {result.get('symbol')}")
        print(f"Side: {result.get('side')}")
        print(f"Type: {result.get('type')}")
        print(f"Quantity: {result.get('origQty')}")
        if result.get('price'):
            print(f"Price: {result.get('price')}")
        
    except Exception as e:
        print(f"\nError placing order: {e}")


if __name__ == "__main__":
    # Run examples
    main()
    
    # Uncomment to run interactive trading mode
    # interactive_trading()

