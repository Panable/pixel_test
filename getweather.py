import requests
import subprocess

def get_api_key():
    # Lastpass CLI to fetch API Key
    try:
        result = subprocess.run(['lpass', 'show', 'OpenWeatherMap API Key', '--notes', '--quiet'], stdout=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching API key from LastPass: {e}")
        return None

# Fetch the API key
API_KEY = get_api_key()

if API_KEY:
    print(f"API Key: {API_KEY}")
# Debug for testing
else:
    print("API Key not found.")

BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?units=metric&'

#TODO - fix icons
ICON_MAPPING = {
    '01d': '󰖐',  # clear sky (day)
    '01n': '󰖑',  # clear sky (night)
    '02d': '󰖐',  # few clouds (day)
    '02n': '󰖑',  # few clouds (night)
    '03d': '󰖐',  # scattered clouds
    '03n': '󰖑',  # scattered clouds
    '04d': '󰖐',  # broken clouds
    '04n': '󰖑',  # broken clouds
    '09d': '󰖕',  # shower rain (day)
    '09n': '󰖕',  # shower rain (night)
    '10d': '󰖖',  # rain (day)
    '10n': '󰖖',  # rain (night)
    '11d': '󰖒',  # thunderstorm (day)
    '11n': '󰖒',  # thunderstorm (night)
    '13d': '󰖖',  # snow (day)
    '13n': '󰖖',  # snow (night)
    '50d': '󰖗',  # mist (day)
    '50n': '󰖗'   # mist (night)
}

def get_weather(city="Sydney"):
    """Get weather details for a given city (Set to Sydney for now because I have no clue how I'll change any of this later)"""
    url = f"{BASE_URL}q={city}&appid={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

    data = response.json()
    weather_icon = ICON_MAPPING.get(data['weather'][0]['icon'], '?')  # Get the icon - currently all the same icon for testing (I broke some stuff). #TODO - add all the icons.
    temperature = round(data['main']['temp'])  # Print only rounded data (i.e. not 9.1 degree)

    return weather_icon, temperature

if __name__ == "__main__":
    weather_icon, temperature = get_weather()
    print(f"Weather in Sydney: {weather_icon}, {temperature}°C")
