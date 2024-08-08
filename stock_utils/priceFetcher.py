import yfinance as yf
from typing import Optional

def get_stock_price(ticker_symbol: str) -> Optional[float]:
    """
    Fetches the latest available stock price for the given ticker symbol using the Yahoo Finance API.

    Note:
        This function uses the `yfinance` library to access stock data from Yahoo Finance, which is a free tool.
        Please be aware that while the data provided by `yfinance` is updated frequently, it may not be as reliable
        as other premium financial data services. For more accurate and real-time stock prices, consider using
        professional APIs that are available at a cost.

    :param ticker_symbol: Stock ticker symbol (e.g., 'AMD')
    :return: Latest stock price as a float, or None if data is unavailable or an error occurs.
    """
    try:
        # Create a Ticker object
        ticker = yf.Ticker(ticker_symbol)

        # Retrieve the latest market price
        stock_history = ticker.history(period='1d')
        if stock_history.empty:
            print(f"No data available for {ticker_symbol}.")
            return None

        current_price = stock_history['Close'][0]
        return round(float(current_price), 2)

    except Exception as e:
        print(f"Error: {e}")
        return None
