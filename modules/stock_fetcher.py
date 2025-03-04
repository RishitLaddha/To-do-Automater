# modules/stock_fetcher.py

import yfinance as yf

def get_stock_price(ticker: str):
    """
    Fetch the current stock price for a given ticker symbol using the yfinance library.

    This function creates a yfinance Ticker object for the specified stock symbol and then attempts
    to retrieve the 'regularMarketPrice' from the stock's information. If the price is not available,
    it returns a message indicating that the price is not available.

    Args:
        ticker (str): The stock ticker symbol (e.g., "AAPL" for Apple Inc.).

    Returns:
        float or str: The current stock price as a float if available; otherwise, returns the string 
                      "Price not available".

    Example:
        >>> price = get_stock_price("AAPL")
        >>> print(price)
    """
    # Create a Ticker object for the given stock symbol.
    stock = yf.Ticker(ticker)
    
    # Retrieve the regular market price from the stock info dictionary.
    price = stock.info.get('regularMarketPrice', None)
    
    # If the price is not available, return a default message.
    if price is None:
        return "Price not available"
    
    # Return the fetched stock price.
    return price
