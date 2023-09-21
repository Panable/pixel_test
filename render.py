from PIL import Image, ImageDraw, ImageFont
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from gettime import get_current_time
import time

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


def render_time_on_matrix():
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    hour, minute = get_current_time()
    full_time = f"{hour}:{minute}"

    text_width, text_height = get_text_dimensions(full_time, time_font)

    x_position = (width - text_width) / 2
    y_position = (height - text_height) / 2

    draw.text((x_position, y_position), full_time, font=time_font, fill=(255, 255, 255))

    frame_canvas = matrix.CreateFrameCanvas()
    frame_canvas.SetImage(matrix_img)
    matrix.SwapOnVSync(frame_canvas)


if __name__ == "__main__":
    try:
        while True:
            render_time_on_matrix()
            time.sleep(30)  # Update every 30 seconds. Adjust as needed.
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        matrix.Clear()
