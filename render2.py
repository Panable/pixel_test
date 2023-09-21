from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from datetime import datetime
from rgbmatrix import RGBMatrix, RGBMatrixOptions

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

def get_current_time():
    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    return str(hour).zfill(2), str(minute).zfill(2)

def render_time_with_wand():
    hour, minute = get_current_time()
    full_time = f"{hour}:{minute}"
    
    with Image(width=width, height=height, background=Color('black')) as img:
        with Drawing() as draw:
            draw.font = '/usr/local/share/fonts/DinaRemaster-Regular-01.ttf'  # Adjust path as necessary
            draw.font_size = 12
            draw.fill_color = Color('white')
            draw.text_alignment = 'center'
            draw.text(int(width/2), 14, full_time)
            draw(img)

        # Save to a temporary file because the RGBMatrix library reads from a file path
        temp_path = "/tmp/current_time.png"
        img.save(filename=temp_path)
        matrix.SetImage(temp_path)

if __name__ == "__main__":
    try:
        while True:
            render_time_with_wand()
            time.sleep(30)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        matrix.Clear()

