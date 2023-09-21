
from PIL import Image as PILImage, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
import datetime

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
font_path = "/usr/local/share/fonts/DinaRemaster-Regular-01.ttf"  # Adjust path as needed
font_size = 12
font = ImageFont.truetype(font_path, font_size)

def render_time_on_matrix():
    current_time = datetime.datetime.now().strftime('%H:%M')
    
    # Create a new black image
    pil_image = PILImage.new('RGB', (width, height), 'black')
    draw = ImageDraw.Draw(pil_image)
    
    # Calculate the position to center the text
    text_width, text_height = draw.textsize(current_time, font=font)
    x_position = (width - text_width) / 2
    y_position = (height - text_height) / 2
    
    # Draw the text on the image
    draw.text((x_position, y_position), current_time, font=font, fill='white')
    
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

