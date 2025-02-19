from API_client import *
from AI_model import *
from Data_stats import *
import asyncio


# API Credentials
API_KEY = "PKE1B8WAV2KJ324ZKQKC"
SECRET_KEY = "Ro7nFRclHQekQSf5Tt3zbpJAr9AaXhQ7r67sJJDy"

async def get_history(account: Account, symbol: str, days: int = 1, interval: int = 5):
    """
    Get historical market data.
    
    Args:
        account: Trading account
        symbol: Trading symbol (e.g., 'BTC/USD')
        days: Days of history to retrieve
        interval: Bar interval in minutes
    """
    asset = account.focus(symbol)
    if not asset:
        return None
        
    hist_data = account.history(type="BAR", time=days, step=interval)
    if hist_data is not None:
        print(f"\nLast {interval} bars for {symbol}:")
        print(hist_data.tail())
    return hist_data

async def start_stream(account: Account, symbol: str):
    """
    Start real-time market data stream.
    
    Args:
        account: Trading account
        symbol: Trading symbol to stream
    """
    print("\nStarting real-time stream...")
    try:
        await account.stream("BAR")
    except KeyboardInterrupt:
        print("\nStream stopped by user")

async def task(account: Account, symbol: str):
    """
    Execute complete trading operation sequence.
    
    Args:
        account: Trading account
        symbol: Trading symbol
    """
    # Get historical data
    hist_data = await get_history(account, symbol)
    
    # Start streaming if we have historical data
    if hist_data is not None:
        await start_stream(account, symbol)

async def main():
    """Main application entry point."""
    try:
        # Create trading account
        account = Account(
            api_key=API_KEY,
            secret_key=SECRET_KEY,
            paper=True,
            name="main_trading_account"
        )
        account.info()
        # Execute trading operations
        symbol = "BTC/USD"
        await task(account, symbol)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())