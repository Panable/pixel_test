from PIL import Image, ImageDraw, ImageFont
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

width, height = 64, 32
ticker_font_size = 8
price_font_size = 8
change_font_size = 8

font_path = "/usr/local/share/fonts/DinaRemaster-Regular-01.ttf"
ticker_font = ImageFont.truetype(font_path, ticker_font_size)
price_font = ImageFont.truetype(font_path, price_font_size)
change_font = ImageFont.truetype(font_path, change_font_size)

def get_text_dimensions(text_string, font):
    text_string = str(text_string)
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def draw_chart_on_matrix(matrix_img, draw, daily_close_prices, start_y, polygon_color, line_color):
    max_price = max(daily_close_prices)
    min_price = min(daily_close_prices)

    chart_end_y = height - 2 
    chart_area_height = chart_end_y - start_y
    chart_area_width = width

   
    padding = 0.10  # 10% padding
    padded_min_price = min_price - padding * (max_price - min_price)
    padded_max_price = max_price + padding * (max_price - min_price)
    
    raw_scaled_prices = [
        start_y + int(((price - padded_min_price) / (padded_max_price - padded_min_price)) * chart_area_height)
        for price in daily_close_prices
    ]
    scaled_prices = [start_y + price for price in raw_scaled_prices]
    x_interval = chart_area_width / (len(scaled_prices) - 1)

    polygon_points = [(0, height - 1)]
    for i, price in enumerate(scaled_prices):
        x_pos = i * x_interval
        polygon_points.append((x_pos, price))
    polygon_points.append((width-1, height - 1))

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

    stock_data = get_stock_data(ticker)
    print(stock_data)    

    # Render stock ticker
    ticker_str = stock_data['ticker']
    ticker_width, ticker_height = get_text_dimensions(ticker_str, ticker_font)
    ticker_x = 2
    ticker_y = 2 
    draw.text((ticker_x, ticker_y), ticker_str, font=ticker_font, fill=(255, 255, 255))

    # Calculate widths for % change and dollar change
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"
    change_percent_width = get_text_dimensions(change_percent_str, change_font)[0]
    change_dollar_width = get_text_dimensions(change_dollar_str, change_font)[0]

    # Find the wider width to right-align both texts to this width
    max_change_width = max(change_percent_width, change_dollar_width)

    # Render % change right next to the ticker name, aligned to the right
    change_percent_x = ticker_x + ticker_width + 10 + max_change_width - change_percent_width
    change_percent_y = ticker_y
    draw.text((change_percent_x, change_percent_y), change_percent_str, font=change_font, fill=(0, 255, 0) if stock_data['dollar_change'] >= 0 else (255, 0, 0))

    # Render current price below the ticker name
    price_str = f"${stock_data['current_price']:.2f}"
    price_width, price_height = get_text_dimensions(price_str, price_font)
    price_x = ticker_x
    price_y = ticker_y + ticker_height + 2
    draw.text((price_x, price_y), price_str, font=price_font, fill=(255, 255, 255))

    # Render dollar change right next to the current price, aligned to the right
    change_dollar_x = price_x + price_width + 10 + max_change_width - change_dollar_width
    change_dollar_y = price_y
    draw.text((change_dollar_x, change_dollar_y), change_dollar_str, font=change_font, fill=(0, 255, 0) if stock_data['dollar_change'] >= 0 else (255, 0, 0))
    # Calculate start_y for the chart based on where the last text is drawn
    chart_start_y = price_y + price_height + 2

    if stock_data['dollar_change'] >= 0:
        polygon_color = (0, 255, 0)  # green for positive change
        line_color = (127, 255, 127)  # lighter green for the line
    else:
        polygon_color = (255, 0, 0)  # red for negative change
        line_color = (255, 127, 127)  # lighter red for the line

    # Draw the stock chart on the matrix image
    draw_chart_on_matrix(matrix_img, draw, stock_data['daily_close_prices'], chart_start_y, polygon_color, line_color)

    frame_canvas = matrix.CreateFrameCanvas()
    frame_canvas.SetImage(matrix_img)
    matrix.SwapOnVSync(frame_canvas)

if __name__ == "__main__":
    render_stock_on_matrix('AAPL')
