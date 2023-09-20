from PIL import Image, ImageDraw, ImageFont
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
from getweather import get_weather
import requests

# Init matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

# Always render in 64x32
width, height = 64, 32
font_path = "/usr/local/share/fonts/DinaRemaster-Regular-01.ttf"
time_font_size = 12  # as a test
time_font = ImageFont.truetype(font_path, time_font_size)

def get_time_from_api(timezone="Australia/Sydney"):
    """Fetches the current time for the given timezone using the WorldTimeAPI."""
    
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}")
    
    if response.status_code != 200:
        raise Exception("Failed to fetch time from the API")
    
    data = response.json()
    current_datetime = data['datetime']  
    
    # Extract just the date and time (without milliseconds)
    date_str, time_str = current_datetime.split('T')
    time_str = time_str.split('.')[0]
    
    hour, minute = time_str.split(":")[:2]
    return hour, minute

frame_canvas = matrix.ClearFrameCanvas()

def render_time_only():
    matrix_img = Image.new('RGB', (width, height), color = (0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    hour, minute = get_time_from_api()
    full_time = f"{hour}:{minute}"
    text_width, text_height = get_text_dimensions(full_time, time_font)
    x_position_time = (width - text_width) / 2
    y_position_time = 2
    draw.text((x_position_time, y_position_time), full_time, font=time_font, fill=(255, 255, 255))
    # Update the matrix ...
    frame_canvas.SetImage(matrix_img)
    matrix.SwapOnVSync(frame_canvas)

def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

    
# Main loop ...

if __name__ == "__main__":
    try:
        while True:
            render_time_only()
            time.sleep(1000) 
    except KeyboardInterrupt:
        print("exiting")
    finally:
        matrix.Clear()
