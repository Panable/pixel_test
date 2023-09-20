from PIL import Image, ImageDraw, ImageFont
import numpy as np
from getstocks import get_stock_data
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Initialize matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

# Always render chart 64x32
width, height = 64, 32
font_path = "/usr/local/share/fonts/ProggyCleanCENerdFontMono-Regular.ttf"

# Adjusted font sizes for the reduced matrix size
ticker_font_size = 10
price_font_size = 8
change_font_size = 8

ticker_font = ImageFont.truetype(font_path, ticker_font_size)
price_font = ImageFont.truetype(font_path, price_font_size)
change_font = ImageFont.truetype(font_path, change_font_size)

def get_text_dimensions(text_string, font):
    text_string = str(text_string)
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def draw_chart_on_matrix(draw, daily_prices, start_y):
    max_price = max(daily_prices)
    min_price = min(daily_prices)

    chart_end_y = height - 2  # giving a little padding at the bottom
    chart_area_height = chart_end_y - start_y

    raw_scaled_prices = [
        int(((price - min_price) / (max_price - min_price)) * chart_area_height)
        for price in daily_prices
    ]

    scaled_prices = [start_y + price for price in raw_scaled_prices]
    x_interval = width / (len(scaled_prices) - 1)

    for i in range(1, len(scaled_prices)):
        start_point = ((i-1) * x_interval, scaled_prices[i-1])
        end_point = (i * x_interval, scaled_prices[i])
        draw.line([start_point, end_point], fill=(127, 255, 127), width=1)

    return draw

def render_stock_on_matrix(ticker='AAPL'):
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)

    stock_data = get_stock_data(ticker)
    print(stock_data)    

    # Render stock ticker
    ticker_str = stock_data['ticker']
    ticker_width, ticker_height = get_text_dimensions(ticker_str, ticker_font)
    ticker_x = 2
    ticker_y = 2
    draw.text((ticker_x, ticker_y), ticker_str, font=ticker_font, fill=(255, 255, 255))

    # Render current price
    price_str = f"${stock_data['current_price']:.2f}"
    price_width, price_height = get_text_dimensions(price_str, price_font)
    price_x = 2
    price_y = ticker_y + ticker_height + 1
    draw.text((price_x, price_y), price_str, font=price_font, fill=(255, 255, 255))

    # Render dollar change
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"
    change_color = (0, 255, 0) if stock_data['dollar_change'] >= 0 else (255, 0, 0)
    change_dollar_width, change_dollar_height = get_text_dimensions(change_dollar_str, change_font)
    change_dollar_x = width - change_dollar_width - 2
    change_dollar_y = 2
    draw.text((change_dollar_x, change_dollar_y), change_dollar_str, font=change_font, fill=change_color)

    # Render % change
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    change_percent_width, change_percent_height = get_text_dimensions(change_percent_str, change_font)
    change_percent_x = width - change_percent_width - 2
    change_percent_y = change_dollar_y + change_dollar_height + 1
    draw.text((change_percent_x, change_percent_y), change_percent_str, font=change_font, fill=change_color)

    # Calculate start_y for the chart based on where the last text is drawn
    total_text_height = change_percent_y + change_percent_height
    margin = 2  # Define margin after the text
    chart_start_y = total_text_height + margin

    # Draw the stock chart on the matrix image
    draw_chart_on_matrix(draw, stock_data['daily_close_prices'], chart_start_y)

    # Display on matrix
    matrix.SetImage(matrix_img)

if __name__ == "__main__":
    render_stock_on_matrix('AAPL')
