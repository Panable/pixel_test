from wand.image import Image as WandImage
from wand.drawing import Drawing
from wand.font import Font
from wand.color import Color
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
from getweather import get_weather
import requests
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

# Always render in 64x32
width, height = 64, 32
time_font_size = 12

def get_time_from_api(timezone="Australia/Sydney"):
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}")
    
    if response.status_code != 200:
        raise Exception("Failed to fetch time from the API")
    
    data = response.json()
    current_datetime = data['datetime']  
    
    hour, minute = current_datetime.split('T')[1].split('.')[0].split(":")[:2]
    return hour, minute

def render_time_and_weather_on_matrix():
    with WandImage(width=width, height=height, background=Color('black')) as matrix_img:
        with Drawing() as draw:
            # Font and style configuration
            draw.font = "DinaRemaster-Regular-01"
            draw.font_size = time_font_size
            draw.fill_color = Color('white')
            
            # Fetch and format the current time
            hour, minute = get_time_from_api()
            full_time = f"{hour}:{minute}"
            
            # Calculate positioning for center alignment
            text_width = int(draw.get_font_metrics(matrix_img, full_time).text_width)
            x_position_time = (width - text_width) // 2
            y_position_time = 2  # Small offset from the top
            
            # Render the time text onto the image
            draw.text(x_position_time, y_position_time, full_time)
            draw(matrix_img)
            
            # Convert Wand image to PIL image for the matrix display
            with io.BytesIO() as output:
                matrix_img.save(file=output, format="PNG")
                output.seek(0)
                pil_image = PILImage.open(output).convert('RGB')
              
            frame_canvas = matrix.CreateFrameCanvas()
            frame_canvas.SetImage(pil_image)
            matrix.SwapOnVSync(frame_canvas)

# Main loop
if __name__ == "__main__":
    try:
        while True:
            render_time_and_weather_on_matrix()
            time.sleep(30)  # Update every 30 seconds. Adjust as needed.
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        matrix.Clear()

