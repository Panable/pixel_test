
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.compat import nested
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

width, height = 64, 32
font_path = "/usr/local/share/fonts/DinaRemaster-Regular-01.ttf"

def get_time_from_api(timezone="Australia/Sydney"):
    """Fetches the current time for the given timezone using the WorldTimeAPI."""
    
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}")
    
    if response.status_code != 200:
        raise Exception("Failed to fetch time from the API")
    
    data = response.json()
    current_datetime = data['datetime']  
    
    date_str, time_str = current_datetime.split('T')
    time_str = time_str.split('.')[0]
    
    hour, minute = time_str.split(":")[:2]
    return hour, minute


def render_time_and_weather_on_matrix():
    matrix_img = Image.new('RGB', (width, height))
    draw = Drawing()
    draw.font = font_path
    draw.font_size = time_font_size

    # Display the time ...
    hour, minute = get_time_from_api()
    full_time = f"{hour}:{minute}"
    text_width = draw.get_font_metrics(matrix_img, full_time).text_width
    x_position_time = int((width - text_width) / 2)
    y_position_time = int(draw.get_font_metrics(matrix_img, full_time).ascender)
    draw.text(x_position_time, y_position_time, full_time)
    draw(matrix_img)

    # Fetch and display the weather information
    weather_icon_path, temperature = get_weather()
    
    with WandImage(filename=weather_icon_path) as icon:
        icon_width = icon.width
        icon_height = icon.height

        temperature_str = f"{temperature}°C"
        temp_text_width = draw.get_font_metrics(matrix_img, temperature_str).text_width
        gap = 2  # Gap between icon and temperature text
        combined_width = icon_width + temp_text_width + gap
        
        x_position_combined = (width - combined_width) / 2
        y_position_icon = int((height + y_position_time - icon_height) / 2)
        
        matrix_img.composite(icon, left=int(x_position_combined), top=int(y_position_icon))

        x_position_temp = int(x_position_combined + icon_width + gap)
        y_position_temp = int(y_position_icon + (icon_height - time_font_size) / 2)
        draw.text(x_position_temp, y_position_temp, temperature_str)
        draw(matrix_img)

    # Update the matrix ...
    pil_image = Image.fromarray(np.array(matrix_img))
    frame_canvas = matrix.CreateFrameCanvas()
    frame_canvas.SetImage(pil_image)
    matrix.SwapOnVSync(frame_canvas)
       pil_image = Image(image=pil_image) 
        frame_canvas = matrix.CreateFrameCanvas()
        frame_canvas.SetImage(pil_image)
        matrix.SwapOnVSync(frame_canvas)

# Main loop ...

if __name__ == "__main__":
    try:
        while True:
            render_time_and_weather_on_matrix()
            time.sleep(30)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        matrix.Clear()

