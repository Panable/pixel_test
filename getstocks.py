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

def is_market_open(ticker):
    now = datetime.now(pytz.utc)
    if ".AX" in ticker:  # Australian Stock Exchange
        start_time = now.replace(hour=0, minute=0)  # 10:00 AM AEST
        end_time = now.replace(hour=6, minute=0)  # 4:00 PM AEST
    else:  # Default to US Stock Exchange
        start_time = now.replace(hour=14, minute=30)  # 9:30 AM ET
        end_time = now.replace(hour=21, minute=0)  # 4:00 PM ET

    return start_time <= now <= end_time

def get_stock_data(ticker_symbol='AAPL'):
    stock = yf.Ticker(ticker_symbol)
    if is_market_open(ticker_symbol):
        hist = stock.history(period="1d", interval="1h")
    else:
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        hist = stock.history(start=yesterday, end=yesterday)
        
    if hist.empty:
        return {
            'ticker': ticker_symbol,
            'daily_close_prices': [0, 0, 0, 0, 0],
            'current_price': 0,
            'percent_change': 0,
            'dollar_change': 0
        }

    daily_close_prices = hist['Close'].tolist()
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

