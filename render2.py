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
   with Drawing() as draw:
        with Image(width=64, height=32, background=Color("black")) as img:
            draw.text((20, 10), get_time_from_api(), font='Arial', font_size=20, fill=Color("white"))
            draw(img)
            
            # Save to a temporary path
            temp_path = "/tmp/temp_image.png"
            img.save(filename=temp_path)
            
            # Load with PIL
            pil_image = PILImage.open(temp_path)
            
            # Set the image to the matrix using PIL's Image object
            matrix.SetImage(pil_image)   

 if __name__ == "__main__":
    try:
        while True:
            render_time_with_wand()
            time.sleep(30)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        matrix.Clear()

