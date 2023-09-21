from rgbmatrix import RGBMatrix, RGBMatrixOptions
from wand.image import Image as WandImage
from wand.drawing import Drawing
from wand.color import Color
from PIL import Image as PILImage
import requests
import io
import time

# Init matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

# Constants
FONT_PATH = "/usr/local/share/fonts/DinaRemaster-Regular-01.ttf"
WIDTH, HEIGHT = 64, 32

def get_time_from_api(timezone="Australia/Sydney"):
    """Fetches the current time for the given timezone using the WorldTimeAPI."""
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}")
    response.raise_for_status()
    data = response.json()
    current_datetime = data['datetime']
    date_str, time_str = current_datetime.split('T')
    time_str = time_str.split('.')[0]
    hour, minute = time_str.split(":")[:2]
    return f"{hour}:{minute}"

def render_time_with_wand():
    with WandImage(width=WIDTH, height=HEIGHT, background=Color('black')) as img:
        with Drawing() as draw:
            draw.font = FONT_PATH
            draw.font_size = 20  # Initial font size
            time_str = get_time_from_api()
            
            # Calculate the bounding box for the text
            metrics = draw.get_font_metrics(img, time_str)
            while metrics.text_width > WIDTH or metrics.text_height > HEIGHT:
                draw.font_size -= 1
                metrics = draw.get_font_metrics(img, time_str)
                
            x_position_time = (WIDTH - metrics.text_width) / 2
            y_position_time = (HEIGHT - metrics.text_height) / 2 + metrics.ascender  # Centred vertically
            
            draw.text(x_position_time, y_position_time, time_str)
            draw(img)
        
        # Convert Wand image to PIL Image for RGBMatrix
        with io.BytesIO() as temp_buffer:
            img.save(file=temp_buffer)
            temp_buffer.seek(0)
            pil_image = PILImage.open(temp_buffer)
            matrix.SetImage(pil_image)

if __name__ == "__main__":
    try:
        while True:
            render_time_with_wand()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        matrix.Clear()

