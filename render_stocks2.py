from getstocks import get_stock_data
from PIL import Image, ImageDraw, ImageFont
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
max_chart_height = 15
chart_start_y = height - max_chart_height

font = graphics.Font()
font.LoadFont("/usr/local/share/fonts/4x6.bdf")
color = graphics.Color(255, 255, 255)

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def draw_chart_on_matrix(matrix_img, draw, daily_close_prices, start_y, polygon_color, line_color):
    max_price = max(daily_close_prices)
    min_price = min(daily_close_prices)
    scale_factor = (height - start_y) / (max_price - min_price)
    scaled_prices = [height - (price - min_price) * scale_factor for price in daily_close_prices]
    x_interval = width / (len(scaled_prices) - 1)

    polygon_points = [(width - 1, height)]
    for i, price in enumerate(scaled_prices):
        x_pos = width - (i * x_interval)
        polygon_points.append((x_pos, price))
    polygon_points.append((0, height))

    draw.polygon(polygon_points, fill=polygon_color)
    for i in range(1, len(scaled_prices)):
        start_point = (width - ((i-1) * x_interval), scaled_prices[i-1])
        end_point = (width - (i * x_interval), scaled_prices[i])
        draw.line([start_point, end_point], fill=line_color, width=1)
    return draw



def render_stock_on_matrix(ticker='AAPL'):
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)
    stock_data = get_stock_data(ticker)
    polygon_color = (255, 255, 255)
    line_color = (127, 127, 127)
    if stock_data['dollar_change'] >= 0:
        polygon_color = (0, 0, 255)
        line_color = (127, 126, 255)
    else:
        polygon_color = (255, 0, 0)
        line_color = (255, 127, 127)

    daily_close_prices = stock_data['daily_close_prices']
    
    draw_chart_on_matrix(matrix_img, draw, daily_close_prices, chart_start_y, polygon_color, line_color)
    
    offscreen_canvas = matrix.CreateFrameCanvas()
    matrix_img = matrix_img.convert('RGB')
    for y in range(height):
        for x in range(width):
            pixel = matrix_img.getpixel((x, y))
            offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])
    
    ticker_str = stock_data['ticker']
    graphics.DrawText(offscreen_canvas, font, 2, 7, color, ticker_str)
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    graphics.DrawText(offscreen_canvas, font, width - 5 * len(change_percent_str), 7, color, change_percent_str)
    price_str = f"${stock_data['current_price']:.2f}"
    graphics.DrawText(offscreen_canvas, font, 2, 17, color, price_str)
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"
    graphics.DrawText(offscreen_canvas, font, width - 5 * len(change_dollar_str), 17, color, change_dollar_str)

    matrix.SwapOnVSync(offscreen_canvas)

