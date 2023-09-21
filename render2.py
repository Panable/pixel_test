import time
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from datetime import datetime
import io
from PIL import Image as PILImage
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Configuration for the matrix
OPTIONS = RGBMatrixOptions()
OPTIONS.rows = 64
OPTIONS.chain_length = 1
OPTIONS.parallel = 1
OPTIONS.hardware_mapping = 'adafruit-hat'
OPTIONS.gpio_slowdown = 2
matrix = RGBMatrix(options=OPTIONS)

# Configuration constants for the script
WIDTH = matrix.width
HEIGHT = matrix.height
FONT_PATH = "/usr/local/share/fonts/DinaRemaster-Regular-01.ttf"

def render_time_with_wand():
    with Image(width=WIDTH, height=HEIGHT, background=Color("black")) as img:
        # Configure the draw settings
        draw = Drawing()
        draw.font = FONT_PATH
        draw.font_size = 30
        draw.fill_color = Color("white")

        # Get the current time
        time_str = datetime.now().strftime("%H:%M:%S")

        # Calculate the position to center the text
        metrics = draw.get_font_metrics(img, time_str)
        x_position_time = max(0, int((WIDTH - metrics.text_width) / 2))
        y_position_time = int((HEIGHT - metrics.text_height) / 2 + metrics.ascender)  # Centred vertically

        # Draw the time
        draw.text(x_position_time, y_position_time, time_str)
        draw(img)

        # Convert the Wand Image to a blob (byte stream)
        img.format = 'png'  # Set the format explicitly to PNG
        img_blob = img.make_blob()

        # Use Pillow to convert the blob to an RGB mode image
        with io.BytesIO(img_blob) as temp_buffer:
            pil_image = PILImage.open(temp_buffer).convert('RGB')
            matrix.SetImage(pil_image)

    time.sleep(1)

while True:
    render_time_with_wand()
