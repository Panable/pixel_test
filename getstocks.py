import requests
import datetime

API_KEY = "7b7e83b39ab1195a6886ec63891bb836"
BASE_URL = "http://api.marketstack.com/v1/eod"
TICKER_SYMBOL = "AAPL"  # Default ticker symbol

def get_stock_data(symbol=TICKER_SYMBOL):
    # Get today's date and one month ago
    today = datetime.date.today()
    one_month_ago = today - datetime.timedelta(days=30)

    # Make the request
    params = {
        "access_key": API_KEY,
        "symbols": symbol,
        "date_from": one_month_ago,
        "date_to": today
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    print("API Response:", data)
    
    if 'error' in data:
        raise Exception(data['error']['info'])

    # Extract the relevant data
    latest_data = data['data'][0]
    close_price = latest_data['close']
    open_price = latest_data['open']
    dollar_change = close_price - open_price
    percent_change = (dollar_change / open_price) * 100
    daily_close_prices = [entry['close'] for entry in data['data']]

    result = {
        "ticker": symbol,
        "current_price": close_price,
        "dollar_change": dollar_change,
        "percent_change": percent_change,
        "daily_close_prices": daily_close_prices
    }
    
    return result

if __name__ == "__main__":
    stock_data = get_stock_data()
    print(stock_data)

