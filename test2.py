import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

width, height = 64, 32

def render_static_content():
    matrix_img = Image.new('RGB', (width, height), color=(255, 0, 0))
    frame_canvas = matrix.CreateFrameCanvas()
    frame_canvas.SetImage(matrix_img)
    matrix.SwapOnVSync(frame_canvas)

if __name__ == "__main__":
    try:
        while True:
            render_static_content()
            time.sleep(1)
    except KeyboardInterrupt:
        print("exiting")
    finally:
        matrix.Clear()
