import requests

def get_time_from_api(timezone="Australia/Sydney"):
    """Fetches the current time for the given timezone using the WorldTimeAPI."""
    
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}")
    
    if response.status_code != 200:
        raise Exception("Failed to fetch time from the API")
    
    data = response.json()
    current_datetime = data['datetime']  # This returns time in the format: '2023-09-20T12:34:56.789+10:00'
    
    # Extract just the date and time (without milliseconds)
    date_str, time_str = current_datetime.split('T')
    time_str = time_str.split('.')[0]
    
    return date_str, time_str

