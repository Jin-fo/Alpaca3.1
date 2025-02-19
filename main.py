from API_client import *
from AI_model import *
from Data_stats import *
import asyncio
import pandas as pd


# API Credentials
API_KEY = "PKE1B8WAV2KJ324ZKQKC"
SECRET_KEY = "Ro7nFRclHQekQSf5Tt3zbpJAr9AaXhQ7r67sJJDy"

async def get_history(account: Account, symbol: str, days: int = 1, interval: int = 5):
    """Get historical market data."""
    asset = account.focus(symbol)
    if not asset:
        return None
    return account.history(type="BAR", time=days, step=interval)

async def start_stream(account: Account, symbol: str, stats: Statistic):
    """Start real-time market data stream."""
    try:
        # Store Statistic instance in account for stream updates
        account.stats = stats
        await account.stream("BAR")
    except KeyboardInterrupt:
        pass

async def task(account: Account, symbol: str):
    """Execute complete trading operation sequence."""
    hist_data = await get_history(account, symbol)
    if hist_data is not None:
        stats = Statistic(symbol)
        stats.clear()
        print(f"\nSaving historical data for {symbol}...")
        
        hist_data = hist_data.reset_index()
        
        for _, row in hist_data.iterrows():
            stats.append({
                'price': row['close'],
                'timestamp': account.time(row['timestamp'], return_format=True)
            })
        
        print(f"\nStarting live data stream for {symbol}...")
        await start_stream(account, symbol, stats)

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