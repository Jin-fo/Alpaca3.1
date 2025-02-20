from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Union, List
import pandas as pd

# Alpaca imports
from alpaca.data.live.crypto import *
from alpaca.data.historical.crypto import *
from alpaca.data.live.stock import *
from alpaca.data.historical.stock import *

#from alpaca.data.live.option import *
#from alpaca.data.historical.option import *

from alpaca.data.requests import *
from alpaca.data.timeframe import *
from alpaca.trading.client import *
from alpaca.trading.stream import *
from alpaca.trading.requests import *
from alpaca.trading.enums import *
from alpaca.common.exceptions import APIError
import asyncio

class Client:
    """Base trading client wrapper for Alpaca API."""
    stack = []
    API_KEY = str
    SECRET_KEY = str
    paper = bool
    name = str
    client = None

    def __init__(self, api_key: str, secret_key: str, paper: bool, name: str):
        """Initialize trading client with API credentials."""
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key
        self.paper = paper
        self.name = name
        self.client = None

    def show_symbol(self, exchange: str) -> list: pass
    def focus(self, symbol: str): pass
    def history(self, type: str, time: int, step: int): pass
    async def stream(self, type: str): pass
    async def on_update(self, data): pass

class Account(Client):
    """Trading account with market data and trading capabilities."""
    positions = {}
    orders = []
    timezone = None  # Initialize timezone as None

    def __init__(self, api_key: str, secret_key: str, paper: bool, name: str):
        """Initialize Account with API credentials."""
        # Initialize parent Client class
        super().__init__(api_key, secret_key, paper, name)
        
        # Initialize account-specific attributes
        self.positions = {}
        self.orders = []
        
        # Set default timezone
        self.time(timezone_str="America/New_York")
        
        # Initialize trading client
        try:
            self.client = TradingClient(self.API_KEY, self.SECRET_KEY, paper=self.paper)
            account_info = self.client.get_account()
            print(f"Successfully created trading account: {self.name}")
            print(f"Account ID: {account_info.id}")
            print(f"Account Status: {account_info.status}")
            if self.paper:
                print("Paper trading mode enabled")
        except APIError as e:
            raise APIError(f"Failed to connect to trading account: {str(e)}")

    def time(self, timestamp=None, timezone_str: str = None, return_format: bool = False) -> Union[datetime, str]:
        """
        Get or convert time with timezone handling.
        
        Args:
            timestamp: Optional timestamp to convert
            timezone_str: Optional timezone to set (e.g., "America/New_York")
            return_format: If True, returns formatted string, else returns datetime
            
        Returns:
            datetime or formatted string in specified timezone
        """
        # Update timezone if specified
        if timezone_str:
            try:
                self.timezone = ZoneInfo(timezone_str)
                print(f"Timezone set to: {timezone_str}")
            except Exception as e:
                print(f"Error setting timezone {timezone_str}: {e}")
                self.timezone = ZoneInfo("UTC")
                print("Defaulting to UTC")

        # Ensure we have a timezone set
        if self.timezone is None:
            self.timezone = ZoneInfo("UTC")
            print("Timezone not set, using UTC")

        # Get or convert time
        if timestamp is None:
            time = datetime.now(self.timezone)
        else:
            # Convert timestamp to datetime with timezone
            if isinstance(timestamp, pd.Timestamp):
                timestamp = timestamp.to_pydatetime()
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=ZoneInfo("UTC"))
            time = timestamp.astimezone(self.timezone)

        # Return formatted string or datetime
        return time.strftime('%Y-%m-%d %H:%M:%S %Z') if return_format else time

    def order(self, side: str, qty: float):
        """Place a trading order."""
        pass

    def info(self):
        """Display essential account information including balance and positions."""
        try:
            # Get account information
            account = self.client.get_account()
            
            # Print essential account info
            print("\n=== Account Summary ===")
            print(f"Cash Balance: ${float(account.cash):,.2f}")
            print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
            print(f"Buying Power: ${float(account.buying_power):,.2f}")
            
            # Get and print positions
            positions = self.client.get_all_positions()
            if positions:
                print("\n=== Current Positions ===")
                for position in positions:
                    print(f"\n{position.symbol}:")
                    print(f"  Quantity: {position.qty}")
                    print(f"  Current Value: ${float(position.market_value):,.2f}")
                    print(f"  Profit/Loss: ${float(position.unrealized_pl):,.2f}")
            else:
                print("\nNo open positions")
            
            # Get and print active orders
            orders = self.client.get_orders()
            if orders:
                print("\n=== Active Orders ===")
                for order in orders:
                    print(f"\n{order.symbol}: {order.side.title()} {order.qty} @ {order.type}")
            else:
                print("\nNo active orders")

        except APIError as e:
            print(f"Error fetching account information: {e}")

    async def cleanup(self):
        """Remove access to account resources without modifying positions or orders."""
        try:
            # Clear local references
            self.positions = {}
            self.orders = []
            self.client = None
            self.symbol = None
            
            print(f"Successfully removed access to account: {self.name}")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Function Implementations
def Client_show_symbol(self, exchange: str) -> list:
    """Display available symbols for given exchange."""
    pass

def Client_focus(self, symbols: Union[str, List[str]]):
    """Set focus to one or more trading symbols and verify their availability.
    
    Args:
        symbols: Single symbol string or list of symbols (e.g., 'BTC/USD' or ['BTC/USD', 'ETH/USD'])
        
    Returns:
        Single asset object or list of assets if successful, None for failures
    """
    # Convert single symbol to list for consistent processing
    if isinstance(symbols, str):
        symbols = [symbols]
    
    assets = []
    for symbol in symbols:
        try:
            # Clean up symbol format (remove '/' for crypto pairs)
            clean_symbol = symbol.replace('/', '')
            
            # Get asset information
            asset = self.client.get_asset(symbol_or_asset_id=clean_symbol)
            assets.append(asset)
            
            # Print success message with asset details
            print(f"\n=== Asset Focus ===")
            print(f"Symbol: {asset.symbol}")
            print(f"Name: {asset.name}")
            print(f"Asset Class: {asset.asset_class}")
            print(f"Tradable: {asset.tradable}")
            
        except APIError as e:
            print(f"\n[!] Error focusing symbol {symbol}: {str(e)}")
            print("Please check if the symbol is correct and available for trading.")
            assets.append(None)
    
    # Store the last focused symbol for single symbol requests
    if len(assets) == 1:
        self.symbol = assets[0]
        return self.symbol
    
    # Store all symbols for multiple symbol requests
    self.symbols = [a for a in assets if a is not None]
    return self.symbols

def Client_history(self, type: str, time: int, step: int):
    """Retrieve historical data for focused symbol."""
    now = self.time()
    
    if self.symbol.exchange == "CRYPTO":
        if type.upper() == "BAR":
            data = CryptoBarsRequest(
                symbol_or_symbols = self.symbol.symbol,
                timeframe = TimeFrame(amount = step, unit = TimeFrameUnit.Minute),
                start = now - timedelta(days = time),
                limit = 1000000
            )
            crypto_history = CryptoHistoricalDataClient(api_key=self.API_KEY, secret_key=self.SECRET_KEY)
            bar = crypto_history.get_crypto_bars(data).df

    elif self.symbol.exchange != "CRYPTO":
        if type.upper() == "BAR":
            data = StockBarsRequest(
                symbol_or_symbols = self.symbol.symbol,
                timeframe = TimeFrame(amount = step, unit = TimeFrameUnit.Minute),
                start = now - timedelta(days = time),
                limit = 1000000
            )
            stock_history = StockHistoricalDataClient(api_key=self.API_KEY, secret_key=self.SECRET_KEY)
            bar = stock_history.get_stock_bars(data).df

    else:
        return None
    
    return bar

async def Client_stream(self, type:str):
    """Stream bar data."""
    print("[o][BAR Stream]")
    
    try:
        # Set up stream URL based on asset type
        if self.symbol.exchange == 'CRYPTO':
            url = BaseURL.MARKET_DATA_STREAM.value + "/v1beta3/crypto/" + CryptoFeed.US
        elif self.symbol.exchange != 'CRYPTO':
            url = BaseURL.MARKET_DATA_STREAM.value + "/v2/" + DataFeed.IEX
            
        # Initialize and configure stream
        stream = DataStream(url, self.API_KEY, self.SECRET_KEY)
        
        # Subscribe to trades for bar data
        stream._subscribe(
            handler=self.on_update,
            symbols=((self.symbol).symbol,),
            handlers=stream._handlers[type]
        )
        
        print("[~][Retrieving bar data...]")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, stream.run)
            
    except Exception as e:
        print(f"Stream error: {e}")

async def Client_on_update(self, data):
    """Handle incoming bar data and save to CSV."""
    try:
        if hasattr(self, 'stats'):
            # Get timestamp from data or current time
            timestamp = (self.time(data.timestamp) 
                        if hasattr(data, 'timestamp') 
                        else self.time())
            
            price_data = {
                'price': data.price if hasattr(data, 'price') else data.close if hasattr(data, 'close') else None,
                'timestamp': self.time(timestamp, return_format=True)
            }
            
            if price_data['price'] is not None:
                self.stats.append(price_data)
                print(f"Stream data: ${price_data['price']:.2f} at {price_data['timestamp']}", end='\r')
        return data
    except Exception as e:
        print(f"\nStream error: {e}")
        import traceback
        print(traceback.format_exc())

# Bind method implementations to Client class
Client.show_symbol = Client_show_symbol
Client.focus = Client_focus
Client.history = Client_history
Client.stream = Client_stream
Client.on_update = Client_on_update