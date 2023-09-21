from wand.image import Image as WandImage
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.compat import nested
from wand.font import Font
import numpy as np
from PIL import Image as PILImage, ImageDraw, ImageFont
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
time_font_size = 12  # as a test
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
    with WandImage(wi
    matrix_img = Image(width=width, height=height, background=Color('black'))
    draw = Drawing()
    draw.font = time_font

    # Display the time ...
    hour, minute = get_time_from_api()
    full_time = f"{hour}:{minute}"

    text_width = draw.get_font_metrics(matrix_img, full_time).text_width
    x_position_time = (width - text_width) / 2
    y_position_time = 2  # Small offset from the top

    draw.text(x_position_time, y_position_time + text_height, full_time)
    draw(matrix_img)

    # Fetch and display the weather information
    weather_icon_path, temperature = get_weather()
    icon = Image(filename=weather_icon_path)
    icon_width, icon_height = icon.width, icon.height
    
    temperature_str = f"{temperature}°C"
    temp_text_width = draw.get_font_metrics(matrix_img, temperature_str).text_width

    gap = 2  # Gap between icon and temperature text
    combined_width = icon_width + temp_text_width + gap

    x_position_combined = (width - combined_width) / 2
    y_position_icon = (height + y_position_time + text_height - icon_height) / 2

    matrix_img.composite(icon, left=int(x_position_combined), top=int(y_position_icon))

    x_position_temp = x_position_combined + icon_width + gap
    y_position_temp = y_position_icon + (icon_height - temp_text_height) / 2
    draw.text(x_position_temp, y_position_temp + temp_text_height, temperature_str)
    draw(matrix_img)

    # Convert Wand image to PIL image for matrix display
    wand_img_blob = matrix_img.make_blob('RGB')
    pil_image = PILImage.open(io.BytesIO(wand_img_blob))

    # Update the matrix ...
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

