import yfinance as yf
import yfinance.utils
from datetime import datetime, timedelta
import pytz


# Monkey-patch yfinance to disable caching
def no_op(*args, **kwargs):
    class DummyCache:
        def __getattribute__(self, name):
            return no_op
        def __setattr__(self, name, value):
            pass
    return DummyCache()

yfinance.utils._TzCache = no_op
def get_stock_data(ticker_symbol='AAPL'):
    ticker_symbol = ticker_symbol.strip()  # Remove trailing whitespace
    stock = yf.Ticker(ticker_symbol)

    # Get the last available intraday data
    hist = stock.history(period="1d", interval="1m")

    if hist.empty:
        print(f"No intraday data available for {ticker_symbol}.")
        return {
            'ticker': ticker_symbol,
            'daily_close_prices': [0],
            'current_price': 0,
            'percent_change': 0,
            'dollar_change': 0
        }

    daily_close_prices = hist['Close'].tolist()
    print(f"Data for {ticker_symbol}: {daily_close_prices}")

    if len(daily_close_prices) < 1:
        print(f"Warning: Only {len(daily_close_prices)} data point(s) retrieved for {ticker_symbol}.")

    current_price = daily_close_prices[-1]
    previous_price = daily_close_prices[-2] if len(daily_close_prices) > 1 else daily_close_prices[0]
    dollar_change = current_price - previous_price
    percent_change = (dollar_change / previous_price) * 100 if previous_price != 0 else 0

    return {
        'ticker': ticker_symbol,
        'daily_close_prices': daily_close_prices,
        'current_price': current_price,
        'percent_change': percent_change,
        'dollar_change': dollar_change
    }
