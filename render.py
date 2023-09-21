from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Initialization
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
matrix = RGBMatrix(options=options)

while True:
    # Create a blank canvas
    matrix_img = Image.new('RGB', (64, 32), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    # Use a different font or check if the font path is correct
    font_path = "/usr/local/share/fonts/DinaRemaster-Regular-01.ttf"
    font = ImageFont.truetype(font_path, 12) 

    # Draw static text
    draw.text((0, 0), "12:34", font=font, fill=(255, 255, 255))

    # Display on matrix
    frame_canvas = matrix.CreateFrameCanvas()
    frame_canvas.SetImage(matrix_img)
    matrix.SwapOnVSync(frame_canvas)

