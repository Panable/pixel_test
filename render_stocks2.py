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
max_chart_height = 15
chart_start_y = height - max_chart_height


font = graphics.Font()
font.LoadFont("/usr/local/share/fonts/5x8.bdf")
color = graphics.Color(255, 255, 255)





def draw_chart_on_matrix(matrix_img, draw, daily_close_prices, start_y, polygon_color, line_color):
    max_price = max(daily_close_prices)
    min_price = min(daily_close_prices)
    price_range = max_price - min_price

    chart_end_y = height - 1
    chart_area_height = chart_end_y - start_y
    chart_area_width = width

    # Calculate the required padding for your price range
    padding = 0.10  # 10% padding
    padded_price_range = price_range + 2 * padding * price_range

    # Calculate the scale factor for the prices
    scale_factor = chart_area_height / padded_price_range

    # Adjust the starting point based on whether stock went up or down
    if daily_close_prices[-1] >= daily_close_prices[0]:  # Stock went up
        adjusted_start_y = chart_end_y - (max_price + padding * price_range) * scale_factor
    else:  # Stock went down
        adjusted_start_y = chart_end_y - (min_price - padding * price_range) * scale_factor

    scaled_prices = [
        adjusted_start_y + (price - min_price + padding * price_range) * scale_factor
        for price in daily_close_prices
    ]

    x_interval = chart_area_width / (len(scaled_prices) - 1)

    polygon_points = [(0, chart_end_y)]
    for i, price in enumerate(scaled_prices):
        x_pos = i * x_interval
        polygon_points.append((x_pos, price))
    polygon_points.append((width - 1, chart_end_y))

    draw.polygon(polygon_points, fill=polygon_color)

    for i in range(1, len(scaled_prices)):
        start_point = ((i-1) * x_interval, scaled_prices[i-1])
        end_point = (i * x_interval, scaled_prices[i])
        draw.line([start_point, end_point], fill=line_color, width=1)

    print("First polygon point:", polygon_points[0])
    print("Some polygon y-values:", [p[1] for p in polygon_points[:5]])
    return draw(polygon_points, fill=polygon_color)

    for i in range(1, len(scaled_prices)):
        start_point = ((i-1) * x_interval, scaled_prices[i-1])
        end_point = (i * x_interval, scaled_prices[i])
        draw.line([start_point, end_point], fill=line_color, width=1)

    print("First polygon point:", polygon_points[0])
    print("Some polygon y-values:", [p[1] for p in polygon_points[:5]])
    return draw




def render_stock_on_matrix(ticker='AAPL'):
    # Create a new PIL image to draw the chart.
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    stock_data = get_stock_data(ticker)
    
    # Draw the stock chart on the PIL image.
    if stock_data['dollar_change'] >= 0:
        polygon_color = (0, 0, 255)
        line_color = (127, 126, 255)
    else:
        polygon_color = (255, 0, 0)

def render_stock_on_matrix(ticker='AAPL'):
    # Create a new PIL image to draw the chart.
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    stock_data = get_stock_data(ticker)
    
    # Draw the stock chart on the PIL image.
    if stock_data['dollar_change'] >= 0:
        polygon_color = (0, 0, 255)
        line_color = (127, 126, 255)
    else:
        polygon_color = (255, 0, 0)
        line_color = (255, 127, 127)
    draw_chart_on_matrix(matrix_img, draw, stock_data['daily_close_prices'], chart_start_y, polygon_color, line_color)

    # Transfer the PIL image to the offscreen_canvas.
    offscreen_canvas = matrix.CreateFrameCanvas()
    matrix_img = matrix_img.convert('RGB')
    for y in range(height):
        for x in range(width):
            pixel = matrix_img.getpixel((x, y))
            offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])

    # Render text on top of the chart directly on the offscreen_canvas.
    ticker_str = stock_data['ticker']
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    price_str = f"${stock_data['current_price']:.2f}"
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"

    # Define positioning for each text element:
    ticker_x = 2
    ticker_y = 7
    change_percent_x = width - 5 * len(change_percent_str)
    change_percent_y = 7
    price_x = 2
    price_y = 17
    change_dollar_x = width - 5 * len(change_dollar_str)
    change_dollar_y = 17

    
    if stock_data['dollar_change'] >= 0:
        change_color = graphics.Color(0, 0, 255)  # Green for price up
    else:
        change_color = graphics.Color(255, 0, 0)  # Red for price down
    
    # Render text on top of the chart directly on the offscreen_canvas.
    ticker_str = stock_data['ticker']
    graphics.DrawText(offscreen_canvas, font, ticker_x, ticker_y, color, ticker_str)
    
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    graphics.DrawText(offscreen_canvas, font, change_percent_x, change_percent_y, change_color, change_percent_str)
    
    price_str = f"${stock_data['current_price']:.2f}"
    graphics.DrawText(offscreen_canvas, font, price_x, price_y, color, price_str)
    
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"
    graphics.DrawText(offscreen_canvas, font, change_dollar_x, change_dollar_y, change_color, change_dollar_str)

    matrix.SwapOnVSync(offscreen_canvas)
