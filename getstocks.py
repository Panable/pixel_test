import requests
import datetime

API_KEY = "8ff66016a4316135f02f72c9555e5449"
BASE_URL = "http://api.marketstack.com/v1/eod"
TICKER_SYMBOL = "AAPL"  # Default ticker symbol

def fetch_current_date_from_worldtimeapi():
    response = requests.get('http://worldtimeapi.org/api/ip')
    
    if response.status_code == 200:
        data = response.json()
        datetime_str = data['datetime']  # Format: '2023-09-20T09:45:12.123456+00:00'
        date_str = datetime_str.split('T')[0]
        return datetime.date.fromisoformat(date_str)
    else:
        raise Exception(f"Failed to fetch time. Status Code: {response.status_code}")

def get_stock_data(symbol=TICKER_SYMBOL):
    # Get today's date and one month ago
    today = fetch_current_date_from_worldtimeapi()
    one_month_ago = today - datetime.timedelta(days=30)

    print(f"Fetching data from {one_month_ago} to {today}")

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

    # Check if data returned is empty
    if not data['data']:
        print(f"No data found for the given range for {symbol}")
        return {}

    # Extract the relevant data
    latest_data = data['data'][0]
    close_price = latest_data['close']
    open_price = latest_data['open']
    dollar_change = close_price - open_price
    percent_change = (dollar_change / open_price) * 100
    daily_close_prices = [entry['close'] for entry in data['data']]
    
    print(f"Latest data date: {latest_data['date']}")

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

