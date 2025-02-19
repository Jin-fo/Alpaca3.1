import os
import csv
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class Statistic:
    """Statistical analysis and visualization for market data."""
    data = None
    symbol = str
    filename = str

    # Method Declarations
    def __init__(self, symbol: str, data: pd.DataFrame = None): pass
    def append(self, data: dict): pass
    def read(self) -> pd.DataFrame: pass
    def format_graph(self, title: str, xlabel: str, ylabel: str, grid: bool = True): pass
    def graph(self): pass
    def clear(self): pass
    def read_last_price(self) -> float: pass

# Method Implementations
def Statistic__init__(self, symbol: str, data: pd.DataFrame = None):
    """Initialize statistics object with symbol and data."""
    self.symbol = symbol
    self.data = data
    self.filename = f"data/{symbol.replace('/', '_')}_stream.csv"
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

def Statistic_append(self, data: dict):
    """Append new data to existing CSV file."""
    try:
        # Create file with headers if it doesn't exist
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'price'])
        
        # Get timestamp and price
        timestamp = data.get('timestamp')
        price = data.get('price')
        
        # Append new data
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, price])
            
    except Exception as e:
        print(f"\nError appending stream data: {e}")

def Statistic_read(self) -> pd.DataFrame:
    """Read and process data from CSV file."""
    if os.path.exists(self.filename):
        return pd.read_csv(self.filename)
    return None

def Statistic_format_graph(self, title: str, xlabel: str, ylabel: str, grid: bool = True):
    """Set up graph formatting and style."""
    pass

def Statistic_graph(self):
    """Generate and display price chart."""
    pass

def Statistic_clear(self):
    """Clear existing data file."""
    try:
        if os.path.exists(self.filename):
            os.remove(self.filename)
    except Exception as e:
        print(f"Error clearing data: {e}")

def Statistic_read_last_price(self) -> float:
    """Read the last price from the CSV file."""
    try:
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:  # Check if we have data beyond headers
                    last_line = lines[-1]
                    return float(last_line.split(',')[1])
    except:
        pass
    return None

# Bind method implementations to Statistic class
Statistic.__init__ = Statistic__init__
Statistic.append = Statistic_append
Statistic.read = Statistic_read
Statistic.format_graph = Statistic_format_graph
Statistic.graph = Statistic_graph
Statistic.clear = Statistic_clear
Statistic.read_last_price = Statistic_read_last_price