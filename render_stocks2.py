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
    start_y += 14
    max_price = max(daily_close_prices)
    min_price = min(daily_close_prices)
    price_range = max_price - min_price

    if price_range == 0:
        price_range = 0.01  # Setting a small default value

    # Check if the price range is too narrow
    if price_range < 0.1 * max_price:
        price_range = 0.1 * max_price  # This will give the chart a minimum height.

    scale_factor = max_chart_height / price_range

    # Resample the data points to fit into the matrix width
    data_points_per_column = len(daily_close_prices) // width
    resampled_prices = [daily_close_prices[i] for i in range(0, len(daily_close_prices), data_points_per_column)]
    
    scaled_prices = [start_y - (price - min_price) * scale_factor for price in resampled_prices]
    x_interval = width / (len(scaled_prices) - 1)

    polygon_points = [(0, start_y)]
    for i, price in enumerate(scaled_prices):
        x_pos = i * x_interval
        polygon_points.append((x_pos, price))
    polygon_points.append((width - 1, start_y))

    draw.polygon(polygon_points, fill=polygon_color)
    for i in range(1, len(scaled_prices)):
        start_point = ((i-1) * x_interval, scaled_prices[i-1])
        end_point = (i * x_interval, scaled_prices[i])
        draw.line([start_point, end_point], fill=line_color, width=1)

    print("Resampled Prices:", resampled_prices[:10])
    return draw

def render_stock_on_matrix(ticker='AAPL'):
    local_chart_start_y = chart_start_y
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
    max_price = max(daily_close_prices)
    min_price = min(daily_close_prices)
    price_range = max_price - min_price
    padding = 0.10
    padded_price_range = price_range + 2 * padding * price_range

    if padded_price_range == 0:
        padded_price_range = 0.01

    chart_end_y = height - 1
    chart_area_height = chart_end_y - local_chart_start_y
    scale_factor = chart_area_height / padded_price_range

    if daily_close_prices[-1] >= daily_close_prices[0]:
        adjusted_start_y = chart_end_y - (max_price + padding * price_range) * scale_factor
    else:
        adjusted_start_y = chart_end_y - (min_price - padding * price_range) * scale_factor

    scaled_prices = [
        adjusted_start_y + (price - min_price + padding * price_range) * scale_factor
        for price in daily_close_prices
    ]
    
    first_last_diff = scaled_prices[-1] - scaled_prices[0]
    if stock_data['dollar_change'] < 0 and first_last_diff > 0:
        local_chart_start_y += first_last_diff

    draw_chart_on_matrix(matrix_img, draw, daily_close_prices, local_chart_start_y, polygon_color, line_color)

    offscreen_canvas = matrix.CreateFrameCanvas()
    matrix_img = matrix_img.convert('RGB')
    for y in range(height):
        for x in range(width):
            pixel = matrix_img.getpixel((x, y))
            offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])

    ticker_str = stock_data['ticker']
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    price_str = f"${stock_data['current_price']:.2f}"
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"

    ticker_x = 2
    ticker_y = 7
    change_percent_x = width - 5 * len(change_percent_str)
    change_percent_y = 7
    price_x = 2
    price_y = 17
    change_dollar_x = width - 5 * len(change_dollar_str)
    change_dollar_y = 17

    if stock_data['dollar_change'] >= 0:
        change_color = graphics.Color(0, 0, 255)
    else:
        change_color = graphics.Color(255, 0, 0)
    
    graphics.DrawText(offscreen_canvas, font, ticker_x, ticker_y, color, ticker_str)
    graphics.DrawText(offscreen_canvas, font, change_percent_x, change_percent_y, change_color, change_percent_str)
    graphics.DrawText(offscreen_canvas, font, price_x, price_y, color, price_str)
    graphics.DrawText(offscreen_canvas, font, change_dollar_x, change_dollar_y, change_color, change_dollar_str)

    matrix.SwapOnVSync(offscreen_canvas)

