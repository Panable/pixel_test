from PIL import Image, ImageDraw
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

# Load the bdf font
font_path = "/path/to/7x13.bdf"
font = graphics.Font()
font.LoadFont(font_path)

# Colors and positions
text_color_white = graphics.Color(255, 255, 255)
text_color_blue = graphics.Color(0, 0, 255)
text_color_red = graphics.Color(255, 0, 0)

ticker_x = 2
ticker_y = 2

def get_text_dimensions(text_string, font):
    # Note: This function may no longer be needed as we are relying on hzeller's library for text rendering.
    # It's kept for compatibility with other parts of your code.
    text_string = str(text_string)
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)





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
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    frame_canvas = matrix.CreateFrameCanvas()
    stock_data = get_stock_data(ticker)

    # Render stock ticker
    ticker_str = stock_data['ticker']
    graphics.DrawText(frame_canvas, font, ticker_x, ticker_y + font.baseline, text_color_white, ticker_str)

    # Render % change right next to the ticker name
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    change_percent_x = width - len(change_percent_str) * 7  # Assuming each char in the bdf font is about 7 pixels wide.
    graphics.DrawText(frame_canvas, font, change_percent_x, ticker_y + font.baseline, text_color_blue if stock_data['dollar_change'] >= 0 else text_color_red, change_percent_str)

    # Render current price below the ticker name
    price_str = f"${stock_data['current_price']:.2f}"
    price_y = ticker_y + 13  # Assuming the height of the bdf font characters is 13 pixels.
    graphics.DrawText(frame_canvas, font, ticker_x, price_y + font.baseline, text_color_white, price_str)

    # Render dollar change right next to the current price
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"
    change_dollar_x = width - len(change_dollar_str) * 7
    graphics.DrawText(frame_canvas, font, change_dollar_x, price_y + font.baseline, text_color_blue if stock_data['dollar_change'] >= 0 else text_color_red, change_dollar_str)
    
    # Calculate start_y for the chart based on where the last text is drawn
    chart_start_y = price_y + 13 + 2  # Adjust this if needed.

    # Color settings based on price change
    if stock_data['dollar_change'] >= 0:
        polygon_color = (0, 0, 255)  # blue for positive change
        line_color = (127, 126, 255)  # lighter blue for the line
    else:
        polygon_color = (255, 0, 0)  # red for negative change
        line_color = (255, 127, 127)  # lighter red for the line

    # Draw the stock chart on the matrix image
    draw_chart_on_matrix(matrix_img, draw, stock_data['daily_close_prices'], chart_start_y, polygon_color, line_color)

    frame_canvas.SetImage(matrix_img)
    matrix.SwapOnVSync(frame_canvas)

if __name__ == "__main__":
    render_stock_on_matrix('AAPL')
