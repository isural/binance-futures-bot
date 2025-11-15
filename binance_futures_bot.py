"""
Binance USDⓈ-M Futures Trading Bot
Supports buying and selling cryptocurrency pairs with configurable parameters.
"""

import hashlib
import hmac
import time
import requests
import urllib.parse
from typing import Dict, Optional, Any
from enum import Enum


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
    TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"


class TimeInForce(Enum):
    """Time in force enumeration"""
    GTC = "GTC"  # Good Till Cancel
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill
    GTX = "GTX"  # Good Till Crossing (Post Only)


class BinanceFuturesBot:
    """
    Binance USDⓈ-M Futures Trading Bot
    
    Base URL: https://fapi.binance.com
    Testnet URL: https://demo-fapi.binance.com
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = False,
        recv_window: int = 5000
    ):
        """
        Initialize the Binance Futures Bot
        
        Args:
            api_key: Your Binance API key
            api_secret: Your Binance API secret
            testnet: Use testnet if True
            recv_window: Receive window for requests (default: 5000ms)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.recv_window = recv_window
        self.base_url = "https://demo-fapi.binance.com" if testnet else "https://fapi.binance.com"
        
    def _generate_signature(self, query_string: str) -> str:
        """
        Generate HMAC SHA256 signature for authenticated requests
        
        Args:
            query_string: The query string to sign
            
        Returns:
            The signature as a hexadecimal string
        """
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Binance API
        
        Args:
            method: HTTP method (GET, POST, DELETE, PUT)
            endpoint: API endpoint (e.g., '/fapi/v1/order')
            params: Request parameters
            signed: Whether the request requires authentication
            
        Returns:
            JSON response from the API
            
        Raises:
            Exception: If the API request fails
        """
        if params is None:
            params = {}
            
        # Add timestamp for signed requests
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['recvWindow'] = self.recv_window
        
        # Create query string
        query_string = urllib.parse.urlencode(params)
        
        # Generate signature for signed requests
        if signed:
            signature = self._generate_signature(query_string)
            query_string += f"&signature={signature}"
        
        # Construct full URL
        url = f"{self.base_url}{endpoint}?{query_string}" if query_string else f"{self.base_url}{endpoint}"
        
        # Set headers
        headers = {"X-MBX-APIKEY": self.api_key}
        
        # Make the request
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_data = {}
            try:
                error_data = response.json()
            except:
                error_data = {"msg": str(e)}
            raise Exception(f"HTTP Error {response.status_code}: {error_data.get('msg', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get current account information
        
        Returns:
            Account information dictionary
        """
        return self._make_request("GET", "/fapi/v2/account")
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance
        
        Returns:
            Dictionary with account balance information
        """
        account_info = self.get_account_info()
        return {
            "total_wallet_balance": account_info.get("totalWalletBalance"),
            "total_unrealized_profit": account_info.get("totalUnrealizedProfit"),
            "available_balance": account_info.get("availableBalance"),
            "assets": account_info.get("assets", [])
        }
    
    def get_position_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get position information
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT'). If None, returns all positions
            
        Returns:
            Position information
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._make_request("GET", "/fapi/v2/positionRisk", params)
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get exchange trading rules and symbol information
        
        Returns:
            Exchange information including symbols, filters, rate limits, etc.
        """
        return self._make_request("GET", "/fapi/v1/exchangeInfo", signed=False)
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific trading symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Symbol information or None if not found
        """
        exchange_info = self.get_exchange_info()
        for s in exchange_info.get("symbols", []):
            if s["symbol"] == symbol:
                return s
        return None
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Current price as float
        """
        endpoint = "/fapi/v1/ticker/price"
        params = {"symbol": symbol}
        response = self._make_request("GET", endpoint, params, signed=False)
        return float(response["price"])
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        time_in_force: Optional[str] = None,
        reduce_only: Optional[bool] = None,
        close_position: Optional[bool] = None,
        stop_price: Optional[float] = None,
        working_type: Optional[str] = None,
        price_protect: Optional[bool] = None,
        new_order_resp_type: Optional[str] = None,
        position_side: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Place an order on Binance Futures
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side - 'BUY' or 'SELL'
            order_type: Order type - 'MARKET', 'LIMIT', 'STOP', etc.
            quantity: Order quantity (required for most order types)
            price: Order price (required for LIMIT orders)
            time_in_force: Time in force - 'GTC', 'IOC', 'FOK', 'GTX' (required for LIMIT orders)
            reduce_only: 'true' or 'false'. Used with Hedge Mode. If 'true', the order can only reduce position
            close_position: If 'true', close all positions for the symbol
            stop_price: Used with STOP/STOP_MARKET orders
            working_type: 'MARK_PRICE' or 'CONTRACT_PRICE' (for conditional orders)
            price_protect: 'true' or 'false' - for stop orders
            new_order_resp_type: 'ACK', 'RESULT', 'FULL'
            position_side: 'BOTH', 'LONG', or 'SHORT' (for Hedge Mode)
            
        Returns:
            Order response dictionary
            
        Example:
            # Market buy order
            bot.place_order(
                symbol="BTCUSDT",
                side="BUY",
                order_type="MARKET",
                quantity=0.001
            )
            
            # Limit sell order
            bot.place_order(
                symbol="BTCUSDT",
                side="SELL",
                order_type="LIMIT",
                quantity=0.001,
                price=50000.0,
                time_in_force="GTC"
            )
        """
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
        }
        
        # Add optional parameters
        if quantity is not None:
            params["quantity"] = quantity
        if price is not None:
            params["price"] = price
        if time_in_force is not None:
            params["timeInForce"] = time_in_force.upper()
        if reduce_only is not None:
            params["reduceOnly"] = str(reduce_only).lower()
        if close_position is not None:
            params["closePosition"] = str(close_position).lower()
        if stop_price is not None:
            params["stopPrice"] = stop_price
        if working_type is not None:
            params["workingType"] = working_type.upper()
        if price_protect is not None:
            params["priceProtect"] = str(price_protect).lower()
        if new_order_resp_type is not None:
            params["newOrderRespType"] = new_order_resp_type.upper()
        if position_side is not None:
            params["positionSide"] = position_side.upper()
        
        return self._make_request("POST", "/fapi/v1/order", params)
    
    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        orig_client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel an active order
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            order_id: Order ID (either order_id or orig_client_order_id must be provided)
            orig_client_order_id: Original client order ID
            
        Returns:
            Cancellation response
        """
        params = {"symbol": symbol.upper()}
        if order_id is not None:
            params["orderId"] = order_id
        elif orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        else:
            raise ValueError("Either order_id or orig_client_order_id must be provided")
        
        return self._make_request("DELETE", "/fapi/v1/order", params)
    
    def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """
        Cancel all active orders for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Cancellation response
        """
        params = {"symbol": symbol.upper()}
        return self._make_request("DELETE", "/fapi/v1/allOpenOrders", params)
    
    def get_order_status(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        orig_client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get order status
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            order_id: Order ID
            orig_client_order_id: Original client order ID
            
        Returns:
            Order status information
        """
        params = {"symbol": symbol.upper()}
        if order_id is not None:
            params["orderId"] = order_id
        elif orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        else:
            raise ValueError("Either order_id or orig_client_order_id must be provided")
        
        return self._make_request("GET", "/fapi/v1/order", params)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Get all open orders
        
        Args:
            symbol: Trading pair symbol (optional). If None, returns all open orders
            
        Returns:
            List of open orders
        """
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        return self._make_request("GET", "/fapi/v1/openOrders", params)
    
    def buy_market(
        self,
        symbol: str,
        quantity: float
    ) -> Dict[str, Any]:
        """
        Place a market buy order (convenience method)
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            quantity: Quantity to buy
            
        Returns:
            Order response
        """
        return self.place_order(
            symbol=symbol,
            side="BUY",
            order_type="MARKET",
            quantity=quantity
        )
    
    def sell_market(
        self,
        symbol: str,
        quantity: float
    ) -> Dict[str, Any]:
        """
        Place a market sell order (convenience method)
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            quantity: Quantity to sell
            
        Returns:
            Order response
        """
        return self.place_order(
            symbol=symbol,
            side="SELL",
            order_type="MARKET",
            quantity=quantity
        )
    
    def buy_limit(
        self,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place a limit buy order (convenience method)
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            quantity: Quantity to buy
            price: Limit price
            time_in_force: Time in force (default: 'GTC')
            
        Returns:
            Order response
        """
        return self.place_order(
            symbol=symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force
        )
    
    def sell_limit(
        self,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place a limit sell order (convenience method)
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            quantity: Quantity to sell
            price: Limit price
            time_in_force: Time in force (default: 'GTC')
            
        Returns:
            Order response
        """
        return self.place_order(
            symbol=symbol,
            side="SELL",
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force
        )

