from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
import datetime
import io
from PIL import Image as PILImage

# Init matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

# Settings
width, height = 64, 32
font_path = "/usr/local/share/fonts/DinaRemaster-Regular-01.ttf"

def render_time_on_matrix():
    current_time = datetime.datetime.now().strftime('%H:%M')
    
    with Image(width=width, height=height, background=Color('black')) as img:
        with Drawing() as draw:
            draw.font = font_path
            draw.font_size = 12
            draw.fill_color = Color('white')
            
            # Calculate the position to center the text
            text_metrics = draw.get_font_metrics(img, current_time, True)
            x_position = (width - text_metrics.text_width) / 2
            y_position = (height - text_metrics.text_height) / 2
            
            draw.text(int(x_position), int(y_position + text_metrics.text_height), current_time)
            draw(img)
            
            # Convert Wand image to PIL image for the matrix
            with io.BytesIO() as output:
                img.save(output)
                output.seek(0)
                pil_image = PILImage.open(output)
            
            frame_canvas = matrix.CreateFrameCanvas()
            frame_canvas.SetImage(pil_image)
            matrix.SwapOnVSync(frame_canvas)

# Main loop
if __name__ == "__main__":
    try:
        while True:
            render_time_on_matrix()
            time.sleep(30)  # Update every 30 seconds. Adjust as needed.
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        matrix.Clear()

