
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

def draw_chart_on_canvas(canvas, daily_close_prices, start_y, polygon_color, line_color):
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

    for i in range(1, len(scaled_prices)):
        start_point = (int((i-1) * x_interval), int(scaled_prices[i-1]))
        end_point = (int(i * x_interval), int(scaled_prices[i]))
        graphics.DrawLine(canvas, start_point[0], start_point[1], end_point[0], end_point[1], line_color)

def render_stock_on_matrix(ticker='AAPL'):
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
        polygon_color = text_color_blue
        line_color = graphics.Color(127, 126, 255)
    else:
        polygon_color = text_color_red
        line_color = graphics.Color(255, 127, 127)

    # Draw the stock chart on the frame canvas
    draw_chart_on_canvas(frame_canvas, stock_data['daily_close_prices'], chart_start_y, polygon_color, line_color)

    matrix.SwapOnVSync(frame_canvas)

if __name__ == "__main__":
    render_stock_on_matrix('AAPL')

