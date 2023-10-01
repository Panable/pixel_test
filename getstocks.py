
import yfinance as yf
import yfinance.utils

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
    # Fetching the stock data
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period="5d")

    # If there's no stock data, return a default structure
    if hist.empty:
        return {
            'ticker': ticker_symbol,
            'daily_close_prices': [0, 0, 0, 0, 0],
            'current_price': 0,
            'percent_change': 0,
            'dollar_change': 0
        }

    # Extracting daily close prices
    daily_close_prices = hist['Close'].tolist()

    # Calculate the current price, percent change, and dollar change
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

