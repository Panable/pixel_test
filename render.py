from PIL import Image, ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import numpy as np
import time

# Init matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
matrix = RGBMatrix(options=options)

# Always render in 64x32
width, height = 64, 32

def render_square_on_matrix():
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    # Define square dimensions
    square_size = 20
    x_position = (width - square_size) / 2
    y_position = (height - square_size) / 2

    # Draw the square
    draw.rectangle([(x_position, y_position), (x_position + square_size, y_position + square_size)], fill=(255, 255, 255))

    # Convert the PIL Image to a numpy array
    image_np = np.array(matrix_img)
    
    frame_canvas = matrix.CreateFrameCanvas()
    frame_canvas.SetImage(Image.fromarray(image_np))
    matrix.SwapOnVSync(frame_canvas)

if __name__ == "__main__":
    try:
        while True:
            render_square_on_matrix()
            time.sleep(1)  # Render a new square every second
    except KeyboardInterrupt:
        print("Rendering terminated by user.")

