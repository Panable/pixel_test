from PIL import Image, ImageDraw, ImageFont
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from gettime import get_current_time
import time
from getweather import get_weather

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


def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)


def render_time_and_weather_on_matrix():
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    # Display the time ...
    hour, minute = get_current_time()
    full_time = f"{hour}:{minute}"
    text_width, text_height = get_text_dimensions(full_time, time_font)
    x_position_time = (width - text_width) / 2
    y_position_time = 2  # Small offset from the top
    draw.text((x_position_time, y_position_time), full_time, font=time_font, fill=(255, 255, 255))

    # Fetch and display the weather information
    weather_icon_path, temperature = get_weather()
    icon = Image.open(weather_icon_path)
    icon_width, icon_height = icon.size
    
    x_position_icon = (width - icon_width) / 2
    y_position_icon = (height + y_position_time + text_height - icon_height) / 2
    matrix_img.paste(icon, (int(x_position_icon), int(y_position_icon)))

    temperature_str = f"{temperature}°C"  # Change to °F if you use Fahrenheit
    temp_text_width, temp_text_height = get_text_dimensions(temperature_str, time_font)
    x_position_temp = x_position_icon + icon_width + 2  # 2 pixels gap
    y_position_temp = y_position_icon + (icon_height - temp_text_height) / 2
    draw.text((x_position_temp, y_position_temp), temperature_str, font=time_font, fill=(255, 255, 255))

    # Update the matrix
    frame_canvas = matrix.CreateFrameCanvas()
    frame_canvas.SetImage(matrix_img)
    matrix.SwapOnVSync(frame_canvas)

# Main loop ...

if __name__ == "__main__":
    try:
        while True:
            render_time_and_weather_on_matrix()
            time.sleep(30)  # Update every 30 seconds. Adjust as needed.
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        matrix.Clear()
