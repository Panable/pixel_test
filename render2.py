from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions
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
time_font_size = 12
time_font = ImageFont.truetype(font_path, time_font_size)

matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
draw = ImageDraw.Draw(matrix_img)

# Display the time ...
full_time = "12:34"  # Static time for testing
text_width, text_height = draw.textsize(full_time, font=time_font)
x_position_time = (width - text_width) / 2
y_position_time = (height - text_height) / 2

draw.text((x_position_time, y_position_time), full_time, font=time_font, fill=(255, 255, 255))
matrix.SetImage(matrix_img)

try:
    while True:
        time.sleep(10)  # Just keeping the loop running without doing anything
except KeyboardInterrupt:
    print("Exiting...")
finally:
    matrix.Clear()

