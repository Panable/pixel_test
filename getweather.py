import requests
import subprocess
import os

#def get_api_key():
#    # Lastpass CLI to fetch API Key
#    try:
#        result = subprocess.run(['lpass', 'show', 'OpenWeatherMap API Key', '--notes', '--quiet'], stdout=subprocess.PIPE, text=True, check=True)
#        return result.stdout.strip()
#    except subprocess.CalledProcessError as e:
#        print(f"Error fetching API key from LastPass: {e}")
#        return None

# Fetch API key
API_KEY = "c0d72699800845e7764a1550b079eb58"

#if API_KEY:
#    print(f"API Key: {API_KEY}")
#else:
#    print("API Key not found.")

BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?units=metric&'

ICON_MAPPING = {
    '01d': os.path.expanduser("/home/mason/pixel_test/icons/sun.png"),
    '02d': os.path.expanduser("/home/mason/pixel_test/icons/sunnycloud.png"),
    '03d': os.path.expanduser("/home/mason/pixel_test/icons/overcast.png"),
    '04d': os.path.expanduser("/home/mason/pixel_test/icons/overcast.png"),
    '09d': os.path.expanduser("/home/mason/pixel_test/icons/raincloud.png"),
    '10d': os.path.expanduser("/home/mason/pixel_test/icons/raincloud.png"),
    '11d': os.path.expanduser("/home/mason/pixel_test/icons/thundercloud.png"),
    '01n': os.path.expanduser("/home/mason/pixel_test/icons/nightclear.png"),
    '02n': os.path.expanduser("/home/mason/pixel_test/icons/sunnycloud.png"),  # Adjust if needed for night
    # ... any additional mappings ...
}

def get_weather(city_id="2147714"):
    """Get weather details for a given city (Syd rn)"""
    url = f"{BASE_URL}id={city_id}&appid={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

    data = response.json()
    icon_code = data['weather'][0]['icon']

    weather_icon_path = ICON_MAPPING.get(icon_code, os.path.expanduser("/home/mason/pixel_test/icons/sunnycloud.png"))  # default to sunnycloud.png
    temperature = round(data['main']['temp'])

    return weather_icon_path, temperature

