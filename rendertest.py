from PIL import Image, ImageDraw, ImageFont
import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

# Initialize matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

width, height = 64, 32

def draw_line_between_points(canvas, x1, y1, x2, y2, color):
    """Utility function to draw a line between two points."""
    # We'll use Bresenham's line algorithm for this.
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        canvas.SetPixel(x1, y1, color[0], color[1], color[2])
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def draw_simple_line(canvas):
    """Draws a simple line graph."""
    y_start = (2 * height) // 3
    y_end = height // 3
    x_interval = width // 4
    points = [(i * x_interval, y_start - (i * (y_start - y_end) // 4)) for i in range(5)]

    color = (255, 255, 255)  # White

    # Now, we'll iterate through each pair of points and draw lines between them
    for i in range(len(points) - 1):
        draw_line_between_points(canvas, points[i][0], points[i][1], points[i+1][0], points[i+1][1], color)
def render_simple_line_test():
    offscreen_canvas = matrix.CreateFrameCanvas()
    draw_simple_line(offscreen_canvas)
    matrix.SwapOnVSync(offscreen_canvas)

if __name__ == "__main__":
    try:
        while True:
            render_simple_line_test()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
