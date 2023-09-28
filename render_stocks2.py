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
    matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(matrix_img)
    stock_data = get_stock_data(ticker)
    
    # Using hzeller's library to render text
    offscreen_canvas = matrix.CreateFrameCanvas()
    offscreen_canvas.Clear()  # Clear any previous content

    # Render stock ticker at the top left of the matrix
    ticker_str = stock_data['ticker']
    graphics.DrawText(offscreen_canvas, font, 2, font.height, color, ticker_str)

    # Render % change right next to the ticker name
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    graphics.DrawText(offscreen_canvas, font, width - 8 * len(change_percent_str) - 2, font.height, color, change_percent_str)

    # Render current price below the ticker name
    price_str = f"${stock_data['current_price']:.2f}"
    graphics.DrawText(offscreen_canvas, font, 2, 2 * font.height, color, price_str)

    # Render dollar change right next to the current price
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"
    graphics.DrawText(offscreen_canvas, font, width - 8 * len(change_dollar_str) - 2, 2 * font.height, color, change_dollar_str)

    # Draw the stock chart on the matrix image
    if stock_data['dollar_change'] >= 0:
        polygon_color = (0, 0, 255)
        line_color = (127, 126, 255)
    else:
        polygon_color = (255, 0, 0)
        line_color = (255, 127, 127)
    draw_chart_on_matrix(matrix_img, draw, stock_data['daily_close_prices'], chart_start_y, polygon_color, line_color)

    # Combine the chart with the text rendered with hzeller's library
    matrix_img = matrix_img.convert('RGB')
    for y in range(height):
        for x in range(width):
            pixel = matrix_img.getpixel((x, y))
            offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])

    matrix.SwapOnVSync(offscreen_canvas)

if __name__ == "__main__":
    render_stock_on_matrix('AAPL')

