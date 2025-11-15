# Binance USDⓈ-M Futures Trading Bot

A Python trading bot for Binance USDⓈ-M Futures that allows you to buy and sell cryptocurrency pairs with full control over trading parameters.

## Features

- ✅ Market and Limit orders (BUY/SELL)
- ✅ Support for all order types (MARKET, LIMIT, STOP, STOP_MARKET, TAKE_PROFIT, etc.)
- ✅ Account balance and position information
- ✅ Order management (place, cancel, check status)
- ✅ Testnet support for safe testing
- ✅ Full parameter customization
- ✅ Comprehensive error handling

## Prerequisites

- Python 3.7 or higher
- Binance API Key and Secret Key
- Binance Futures account with USDⓈ-M Futures enabled

## Installation

1. **Clone or download this repository**

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API credentials:**
   
   Edit `config.py` and add your Binance API credentials:
   ```python
   API_KEY = "your_api_key_here"
   API_SECRET = "your_api_secret_here"
   USE_TESTNET = True  # Set to False for live trading
   ```

   **⚠️ IMPORTANT SECURITY NOTE:**
   - Never share your API keys
   - Never commit your `config.py` with real keys to version control
   - Consider using environment variables for production
   - Start with testnet to practice safely

## Getting Binance API Keys

1. Log in to your Binance account
2. Go to API Management
3. Create a new API key
4. **Important**: Enable Futures trading permissions
5. **Security**: Restrict API key to specific IP addresses (recommended)
6. Save your API key and secret (secret is shown only once!)

## Usage

### Basic Usage

```python
from binance_futures_bot import BinanceFuturesBot
import config

# Initialize the bot
bot = BinanceFuturesBot(
    api_key=config.API_KEY,
    api_secret=config.API_SECRET,
    testnet=config.USE_TESTNET
)

# Get current price
price = bot.get_current_price("BTCUSDT")
print(f"Current BTC price: ${price}")

# Place a market buy order
result = bot.buy_market(
    symbol="BTCUSDT",
    quantity=0.001
)
print(f"Order ID: {result['orderId']}")

# Place a limit sell order
result = bot.sell_limit(
    symbol="BTCUSDT",
    quantity=0.001,
    price=50000.0,
    time_in_force="GTC"
)
```

### Advanced Order Placement

```python
# Full control with place_order method
result = bot.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.001,
    price=49000.0,
    time_in_force="GTC",
    reduce_only=False,
    position_side="BOTH"  # For Hedge Mode
)
```

### Account Information

```python
# Get account balance
balance = bot.get_balance()
print(f"Available Balance: {balance['available_balance']}")

# Get position information
positions = bot.get_position_info("BTCUSDT")
for pos in positions:
    if float(pos['positionAmt']) != 0:
        print(f"Position: {pos['positionAmt']} @ {pos['entryPrice']}")
```

### Order Management

```python
# Get open orders
orders = bot.get_open_orders("BTCUSDT")

# Cancel a specific order
bot.cancel_order(symbol="BTCUSDT", order_id=123456)

# Cancel all orders for a symbol
bot.cancel_all_orders("BTCUSDT")

# Check order status
status = bot.get_order_status(symbol="BTCUSDT", order_id=123456)
```

### Interactive Mode

Run the example script with interactive mode:

```python
# Edit example_usage.py and uncomment interactive_trading() at the bottom
python example_usage.py
```

Or use it programmatically:

```python
from example_usage import interactive_trading
interactive_trading()
```

## Configuration Options

### Order Types

- `MARKET`: Execute immediately at market price
- `LIMIT`: Execute at a specific price or better
- `STOP`: Stop order (requires stopPrice)
- `STOP_MARKET`: Stop market order
- `TAKE_PROFIT`: Take profit order
- `TAKE_PROFIT_MARKET`: Take profit market order
- `TRAILING_STOP_MARKET`: Trailing stop market order

### Time In Force (for LIMIT orders)

- `GTC`: Good Till Cancel (default)
- `IOC`: Immediate or Cancel
- `FOK`: Fill or Kill
- `GTX`: Good Till Crossing (Post Only)

### Order Side

- `BUY`: Buy/Long position
- `SELL`: Sell/Short position or close long

## Important Parameters

### Symbol
- Format: `{BASE}{QUOTE}` (e.g., `BTCUSDT`, `ETHUSDT`)
- Must be an active futures trading pair

### Quantity
- Must respect minimum and maximum quantity limits
- Precision varies by symbol (check with `get_symbol_info()`)

### Price (for LIMIT orders)
- Must respect price precision and tick size
- Check symbol info for valid price ranges

## Example Workflows

### 1. Simple Market Order

```python
bot = BinanceFuturesBot(api_key, api_secret, testnet=True)

# Buy 0.001 BTC at market price
result = bot.buy_market("BTCUSDT", 0.001)
print(f"Order executed: {result['executedQty']} @ {result['avgPrice']}")
```

### 2. Limit Order with Price Check

```python
bot = BinanceFuturesBot(api_key, api_secret, testnet=True)

# Get current price
current_price = bot.get_current_price("BTCUSDT")
limit_price = current_price * 0.98  # 2% below market

# Place limit buy order
result = bot.buy_limit("BTCUSDT", 0.001, limit_price, "GTC")
```

### 3. Risk Management - Stop Loss

```python
bot = BinanceFuturesBot(api_key, api_secret, testnet=True)

# Place stop loss order
result = bot.place_order(
    symbol="BTCUSDT",
    side="SELL",
    order_type="STOP_MARKET",
    quantity=0.001,
    stop_price=45000.0,  # Trigger price
    working_type="MARK_PRICE",
    reduce_only=True
)
```

### 4. Check and Close Position

```python
bot = BinanceFuturesBot(api_key, api_secret, testnet=True)

# Check current positions
positions = bot.get_position_info("BTCUSDT")
for pos in positions:
    if float(pos['positionAmt']) > 0:
        # Close long position
        result = bot.place_order(
            symbol="BTCUSDT",
            side="SELL",
            order_type="MARKET",
            quantity=abs(float(pos['positionAmt'])),
            reduce_only=True
        )
```

## Error Handling

The bot includes comprehensive error handling:

```python
try:
    result = bot.buy_market("BTCUSDT", 0.001)
except Exception as e:
    print(f"Error: {e}")
    # Common errors:
    # - Insufficient balance
    # - Invalid symbol
    # - Quantity precision error
    # - Rate limit exceeded
```

## Testnet vs Live Trading

- **Testnet**: Use `USE_TESTNET = True` for safe testing
  - Testnet URL: `https://demo-fapi.binance.com`
  - Get testnet API keys from Binance Testnet
  - No real money involved

- **Live Trading**: Use `USE_TESTNET = False` for real trading
  - Live URL: `https://fapi.binance.com`
  - Uses real funds
  - ⚠️ **USE WITH CAUTION**

## Rate Limits

Binance has rate limits on API requests:
- **IP Limits**: 2400 requests per minute per IP
- **Order Rate Limits**: 300 orders per 10 seconds per symbol
- The bot respects these limits, but you should implement your own rate limiting for high-frequency trading

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for production
3. **Restrict API key IP addresses** in Binance settings
4. **Enable only necessary permissions** (Futures trading)
5. **Start with testnet** before live trading
6. **Monitor your API usage** regularly
7. **Use stop-loss orders** to manage risk
8. **Never share your API secret**

## API Documentation

For detailed API documentation, visit:
- [Binance USDⓈ-M Futures API Docs](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)

## Troubleshooting

### Common Issues

1. **"Invalid API-key"**
   - Check your API key and secret are correct
   - Ensure API key has Futures trading enabled

2. **"Insufficient balance"**
   - Check your account balance with `get_balance()`
   - Ensure you have enough margin for the position

3. **"Invalid symbol"**
   - Verify the symbol exists and is available for futures trading
   - Use `get_exchange_info()` to see available symbols

4. **"Precision is over the maximum defined"**
   - Check quantity/price precision with `get_symbol_info()`
   - Round to appropriate decimal places

5. **"Timestamp for this request is outside of the recvWindow"**
   - Check system clock synchronization
   - Increase `recv_window` if needed

## License

This project is provided as-is for educational purposes. Use at your own risk.

## Disclaimer

⚠️ **TRADING CRYPTOCURRENCIES INVOLVES RISK. THIS BOT IS PROVIDED FOR EDUCATIONAL PURPOSES ONLY.**

- Past performance does not guarantee future results
- You can lose money trading futures
- Always test thoroughly on testnet first
- Never invest more than you can afford to lose
- The authors are not responsible for any losses

## Support

For issues and questions:
- Check Binance API documentation
- Review error messages carefully
- Test on testnet first
- Check Binance status page for API issues

