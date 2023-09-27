from PIL import Image, ImageDraw, ImageFont
from getstocks import get_stock_data
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
max_chart_height = 20
chart_start_y = height - max_chart_height


font = graphics.Font()
font.LoadFont("/usr/local/share/fonts/7x13.bdf")
color = graphics.Color(255, 255, 255)





def draw_chart_on_matrix(matrix_img, draw, daily_close_prices, start_y, polygon_color, line_color):
    max_price = max(daily_close_prices)
    min_price = min(daily_close_prices)

    chart_end_y = height - 1 
    chart_area_height = chart_end_y - start_y
    chart_area_width = width

    padding = 0.10  # 10% padding
    padded_min_price = min_price - padding * (max_price - min_price)
    padded_max_price = max_price + padding * (max_price - min_price)
    
    raw_scaled_prices = [
        chart_area_height - int(((price - padded_min_price) / (padded_max_price - padded_min_price)) * chart_area_height)
        for price in daily_close_prices
    ]

    scaled_prices = [start_y + price for price in raw_scaled_prices]
    x_interval = chart_area_width / (len(scaled_prices) - 1)

    polygon_points = [(0, chart_end_y)]
    for i, price in enumerate(scaled_prices):
        x_pos = i * x_interval
        polygon_points.append((x_pos, price))
    polygon_points.append((width-1, chart_end_y))

    draw.polygon(polygon_points, fill=polygon_color)

    for i in range(1, len(scaled_prices)):
        start_point = ((i-1) * x_interval, scaled_prices[i-1])
        end_point = (i * x_interval, scaled_prices[i])
        draw.line([start_point, end_point], fill=line_color, width=1)

    print("First polygon point:", polygon_points[0])
    print("Some polygon y-values:", [p[1] for p in polygon_points[:5]])
    return draw


def render_stock_on_matrix(ticker='AAPL'):
    # Using hzeller's library to render text
    offscreen_canvas = matrix.CreateFrameCanvas()
    offscreen_canvas.Clear()  # Clear any previous content

    debug_color = graphics.Color(0, 255, 0)  # Bright green for visibility

    # Render stock ticker at the top left of the matrix
    graphics.DrawText(offscreen_canvas, font, 2, font.height, debug_color, ticker)

    # Render % change in the middle of the matrix
    graphics.DrawText(offscreen_canvas, font, 2, height // 2, debug_color, "50%")

    # Swap the canvas
    matrix.SwapOnVSync(offscreen_canvas)

if __name__ == "__main__":
    render_stock_on_matrix('AAPL')

