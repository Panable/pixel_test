from PIL import Image, ImageDraw, ImageFont
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Initialize matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

# Dimensions for rendering
width, height = 64, 32
scaling_factor = 40
adjusted_width, adjusted_height = 64 * scaling_factor, 32 * scaling_factor

# Font configuration
font_path = "/usr/local/share/fonts/Dina-Regular-01.ttf"
time_font_size = 14 * scaling_factor
time_font = ImageFont.truetype(font_path, time_font_size)

def get_text_dimensions(text_string, font):
    text_string = str(text_string)
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def format_time(current_time):
    hour_str, minute_str = current_time
    return f"{hour_str}:{minute_str}"

def render_time_on_matrix(current_time):
    matrix_img = Image.new('RGB', (adjusted_width, adjusted_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    time_str = format_time(current_time)
    hour_str, minute_str = time_str.split(":")

    hour_width, hour_height = get_text_dimensions(hour_str, time_font)
    minute_width, minute_height = get_text_dimensions(minute_str, time_font)
    total_width = hour_width + minute_width + 1

    colon_center_x = (adjusted_width - total_width) // 2 + hour_width + 1
    hour_x = colon_center_x - hour_width - 1
    minute_x = colon_center_x + 1

    draw.text((hour_x, height // 2), hour_str, font=time_font, fill=(255, 255, 255))
    draw.text((minute_x, height // 2), minute_str, font=time_font, fill=(255, 255, 255))

    # Convert the original image to numpy array
    image_np = np.array(matrix_img)
    
    # Resize numpy array to the matrix's resolution
    image_np_resized = np.array(Image.fromarray(image_np).resize((width, height), Image.ANTIALIAS))

    # Convert the resized numpy array back to a PIL image
    final_image = Image.fromarray(image_np_resized)
    frame_canvas = matrix.CreateFrameCanvas()
    frame_canvas.SetImage(final_image)
    # Display on matrix
    matrix.SwapOnVSync(frame_canvas)

if __name__ == "__main__":
    current_time = ("12", "34")  # Example time, can be fetched dynamically
    render_time_on_matrix(current_time)

