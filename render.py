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
    """Fetches the current time for the given timezone using the WorldTimeAPI."""
    
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}")
    
    if response.status_code != 200:
        raise Exception("Failed to fetch time from the API")
    
    data = response.json()
    current_datetime = data['datetime']  
    
    # Extract just the date and time (without milliseconds)
    date_str, time_str = current_datetime.split('T')
    time_str = time_str.split('.')[0]
    
    hour, minute = time_str.split(":")[:2]
    return hour, minute

def render_time_and_weather_on_matrix():
    with WandImage(width=width, height=height, background=Color('black')) as matrix_img:
        with Drawing() as draw:
#            draw.font = 'DinaRemaster-Regular'  # Replace this with the exact name from ImageMagick if different
#            draw.font_size = time_font_size
#            
#            # Display the time
#            hour, minute = get_time_from_api()
#            full_time = f"{hour}:{minute}"
#            text_metrics = draw.get_font_metrics(matrix_img, full_time)
#            text_width = text_metrics.text_width
#            x_position_time = (width - text_width) / 2
#            y_position_time = 2  # Small offset from the top
#            draw.text(int(x_position_time), int(y_position_time + text_metrics.text_height), full_time)
            
            matrix_img = Image(width=width, height=height, background=Color('black'))
            draw = Drawing()
            draw.font = "DinaRemaster-Regular-01"  # We're trying without the path to check if Wand recognizes the font.
            draw.font_size = 12
            draw.fill_color = Color('white')
            
            hour, minute = get_time_from_api()
            full_time = f"{hour}:{minute}"
            text_width = int(draw.get_font_metrics(matrix_img, full_time).text_width)
              
            x_position_time = (width - text_width) // 2
            y_position_time = 2  # Small offset from the top
             
            draw.text(x_position_time, y_position_time, full_time)
            draw(matrix_img)
              
              # Convert Wand image to PIL image for the matrix
            with io.BytesIO() as output:
             matrix_img.save(file=output, format="PNG")
             output.seek(0)
             pil_image = PILImage.open(output)
            pil_image = pil_image.convert('RGB')
              
            frame_canvas = matrix.CreateFrameCanvas()
            frame_canvas.SetImage(pil_image)
            matrix.SwapOnVSync(frame_canvas)
#            # Fetch and display the weather information
#            weather_icon_path, temperature = get_weather()
#            with WandImage(filename=weather_icon_path) as icon:
#                icon_width = icon.width
#                icon_height = icon.height
#
#                temperature_str = f"{temperature}°C"
#                temp_text_metrics = draw.get_font_metrics(matrix_img, temperature_str)
#                temp_text_width = temp_text_metrics.text_width
#                
#                gap = 2  # Gap between icon and temperature text
#                combined_width = icon_width + temp_text_width + gap
#                
#                x_position_combined = (width - combined_width) / 2
#                y_position_icon = (height + y_position_time + text_metrics.text_height - icon_height) / 2
#                
#                matrix_img.composite(icon, left=int(x_position_combined), top=int(y_position_icon))
#                
#                x_position_temp = x_position_combined + icon_width + gap
#                y_position_temp = y_position_icon + (icon_height - temp_text_metrics.text_height) / 2
#                draw.text(int(x_position_temp), int(y_position_temp + temp_text_metrics.text_height), temperature_str)
#                
#            draw(matrix_img)
#            pil_image = matrix_img.make_blob('RGB')
#            pil_image = PILImage.open(io.BytesIO(pil_image))
#
#            frame_canvas = matrix.CreateFrameCanvas()
#            frame_canvas.SetImage(pil_image)
#
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

