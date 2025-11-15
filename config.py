"""
Configuration file for Binance Futures Trading Bot
IMPORTANT: Keep your API keys secure. Never commit this file with real keys to version control.
"""

# Binance API Credentials
API_KEY = "YOUR_API_KEY_HERE"
API_SECRET = "YOUR_API_SECRET_HERE"

# Use testnet for testing (set to False for live trading)
USE_TESTNET = True

# Request receive window (milliseconds)
RECV_WINDOW = 5000

# Default trading parameters (can be overridden in bot usage)
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_ORDER_TYPE = "MARKET"  # MARKET, LIMIT, etc.
DEFAULT_TIME_IN_FORCE = "GTC"  # GTC, IOC, FOK, GTX

