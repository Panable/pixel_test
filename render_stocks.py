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
font_path = "/usr/local/share/fonts/DinaRemasterCollection.ttc/0"  # Replace the 0 if you want a different font from the collection

def get_text_dimensions(text_string, font):
    text_string = str(text_string)
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def draw_chart_on_matrix(draw, daily_prices, start_y):
    max_price = max(daily_prices)
    min_price = min(daily_prices)

    chart_end_y = height - 2
    chart_area_height = chart_end_y - start_y
    raw_scaled_prices = [
            int(((price - min_price) / (max_price - min_price)) * chart_area_height)
            for price in daily_prices
    ]

    scaled_prices = [start_y + price for price in raw_scaled_prices]
    x_interval = width / (len(scaled_prices) - 1)

    polygon_points = [(0, height - 1)]
    for i, price in enumerate(scaled_prices):
        x_pos = i * x_interval
        polygon_points.append((x_pos, price))
    polygon_points.append((width-1, height - 1))

    draw.polygon(polygon_points, fill=(0, 255, 0))
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

    # Fonts
    ticker_font = ImageFont.truetype(font_path, 10) 
    price_font = ImageFont.truetype(font_path, 10)
    change_font = ImageFont.truetype(font_path, 10)

    # Render stock ticker
    ticker_str = stock_data['ticker']
    ticker_width, ticker_height = get_text_dimensions(ticker_str, ticker_font)
    draw.text((10, 2), ticker_str, font=ticker_font, fill=(255, 255, 255))

    # Render current price
    price_str = f"${stock_data['current_price']:.2f}"
    price_width, price_height = get_text_dimensions(price_str, price_font)
    draw.text((10, ticker_height + 2), price_str, font=price_font, fill=(255, 255, 255))

    # Render dollar change
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"
    change_color = (0, 255, 0) if stock_data['dollar_change'] >= 0 else (255, 0, 0)
    change_dollar_width, change_dollar_height = get_text_dimensions(change_dollar_str, change_font)
    draw.text((width - change_dollar_width - 10, 2), change_dollar_str, font=change_font, fill=change_color)

    # Render % change
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    change_percent_width, change_percent_height = get_text_dimensions(change_percent_str, change_font)
    draw.text((width - change_percent_width - 10, change_dollar_height + 2), change_percent_str, font=change_font, fill=change_color)

    # Calculate start_y for the chart
    chart_start_y = ticker_height + price_height + change_dollar_height + change_percent_height + 4

    # Draw the stock chart on the matrix
    draw_chart_on_matrix(draw, stock_data['daily_close_prices'], chart_start_y)

    # Display on matrix
    matrix.SetImage(matrix_img)

if __name__ == "__main__":
    render_stock_on_matrix('AAPL')

