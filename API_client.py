from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Union, List

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

# Function Declarations
def time_now(country: str = "America", city: str = "New_York") -> datetime:
    """Get current time in specified timezone."""
    return datetime.now(ZoneInfo(f"{country}/{city}"))

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

    def __init__(self, api_key: str, secret_key: str, paper: bool, name: str):
        """Initialize Account with API credentials and verify connection.
        
        Raises:
            ValueError: If credentials are invalid
            APIError: If unable to connect to the trading API
        """
        # Initialize parent Client class
        super().__init__(api_key, secret_key, paper, name)
        
        # Initialize account-specific attributes
        self.positions = {}
        self.orders = []
        
        try:
            # Initialize trading client
            self.client = TradingClient(self.API_KEY, self.SECRET_KEY, paper=self.paper)
            
            # Verify connection by getting account info
            account_info = self.client.get_account()
            
            print(f"Successfully created trading account: {self.name}")
            print(f"Account ID: {account_info.id}")
            print(f"Account Status: {account_info.status}")
            if self.paper:
                print("Paper trading mode enabled")
                
        except APIError as e:
            raise APIError(f"Failed to connect to trading account: {str(e)}")

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
    now = time_now()
    
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
        print("[!][INVALID Exchange Type Error]")
        return None
    
    print(f"[o][{type.upper()} History from {time} days, by {step} minutes]")
    return bar

async def Client_stream(self, type: str):
    """Stream real-time market data."""
    print("[o][BAR Stream]")
    
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    
    for attempt in range(MAX_RETRIES):
        try:
            # Set up stream URL based on asset type
            if self.symbol.exchange == 'CRYPTO':
                url = BaseURL.MARKET_DATA_STREAM.value + "/v1beta3/crypto/" + CryptoFeed.US
            elif self.symbol.exchange != 'CRYPTO':
                url = BaseURL.MARKET_DATA_STREAM.value + "/v2/" + DataFeed.IEX
                
            # Initialize and configure stream
            stream = DataStream(url, self.API_KEY, self.SECRET_KEY)
            
            # Subscribe to appropriate data type
            if type.upper() == "BAR":
                handler_type = "trades"
            else:
                handler_type = type.lower()
                
            stream._subscribe(
                handler=self.on_update,
                symbols=((self.symbol).symbol,),
                handlers=stream._handlers[handler_type]
            )
            
            print("[~][Retrieving...]")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, stream.run)
            break  # If successful, exit retry loop
                
        except Exception as e:
            print(f"Stream error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Stream failed to start.")

async def Client_on_update(self, data):
    """Handle incoming stream data."""
    try:
        if hasattr(data, 'close'):
            # Bar data
            print(f"[{time_now()}] Bar Price: {data.close}")
        elif hasattr(data, 'price'):
            # Trade data
            print(f"[{time_now()}] Trade Price: {data.price}")
        else:
            # Other data types
            print(f"[{time_now()}] Data: {data}")
    except Exception as e:
        print(f"Update error: {e}")

# Bind method implementations to Client class
Client.show_symbol = Client_show_symbol
Client.focus = Client_focus
Client.history = Client_history
Client.stream = Client_stream
Client.on_update = Client_on_update

# Update the main task function
async def task(account: Account, symbols: Union[str, List[str]], data_type: str):
    """Execute trading operations for given symbols."""
    try:
        # Your trading logic here
        pass
        
    finally:
        # Cleanup account resources when task ends
        await account.cleanup()