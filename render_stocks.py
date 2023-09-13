from PIL import Image, ImageDraw, ImageFont
from getstocks import get_stock_data

scaling_factor = 40
adjusted_width, adjusted_height = 64 * scaling_factor, 32 * scaling_factor
font_path = "/usr/local/share/fonts/ProggyCleanCENerdFontMono-Regular.ttf"
ticker_font_size = 10 * scaling_factor
price_font_size = 10 * scaling_factor
change_font_size = 10 * scaling_factor

ticker_font = ImageFont.truetype(font_path, ticker_font_size)
price_font = ImageFont.truetype(font_path, price_font_size)
change_font = ImageFont.truetype(font_path, change_font_size)

def get_text_dimensions(text_string, font):
    text_string = str(text_string)
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def draw_chart(draw, daily_prices, start_y):
    max_price = max(daily_prices)
    min_price = min(daily_prices)
    
    chart_area_height = 20 * scaling_factor
    chart_area_width = adjusted_width

    scaled_prices = [
        int(((price - min_price) / (max_price - min_price)) * chart_area_height) 
        for price in daily_prices
    ]

    x_interval = chart_area_width / (len(scaled_prices) - 1)
    
    polygon_points = [(0, start_y + chart_area_height)]
    for i, price in enumerate(scaled_prices):
        x_pos = i * x_interval
        y_pos = start_y + chart_area_height - price
        polygon_points.append((x_pos, y_pos))
    polygon_points.append((adjusted_width-1, start_y + chart_area_height))
    
    draw.polygon(polygon_points, fill=(0, 255, 0))
    
    for i in range(1, len(scaled_prices)):
        start_point = ((i-1) * x_interval, start_y + chart_area_height - scaled_prices[i-1])
        end_point = (i * x_interval, start_y + chart_area_height - scaled_prices[i])
        draw.line([start_point, end_point], fill=(127, 255, 127), width=1)

    return draw

def create_stock_image(ticker='AAPL'):
    img = Image.new('RGB', (adjusted_width, adjusted_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    stock_data = get_stock_data(ticker)
    print(stock_data)
    
    # Render stock ticker
    ticker_str = stock_data['ticker']
    ticker_width, ticker_height = get_text_dimensions(ticker_str, ticker_font)
    ticker_x = 10
    ticker_y = 2 * scaling_factor
    draw.text((ticker_x, ticker_y), ticker_str, font=ticker_font, fill=(255, 255, 255))

    # Render current price
    price_str = f"${stock_data['current_price']:.2f}"
    price_width, price_height = get_text_dimensions(price_str, price_font)
    price_x = 10
    price_y = ticker_y + ticker_height + scaling_factor
    draw.text((price_x, price_y), price_str, font=price_font, fill=(255, 255, 255))

    # Render dollar change
    change_dollar_str = f"${stock_data['dollar_change']:.2f}"
    change_color = (0, 255, 0) if stock_data['dollar_change'] >= 0 else (255, 0, 0)
    change_dollar_width, change_dollar_height = get_text_dimensions(change_dollar_str, change_font)
    change_dollar_x = adjusted_width - change_dollar_width - 10
    change_dollar_y = 2 * scaling_factor
    draw.text((change_dollar_x, change_dollar_y), change_dollar_str, font=change_font, fill=change_color)

    # Render % change
    change_percent_str = f"{stock_data['percent_change']:.2f}%"
    change_percent_width, change_percent_height = get_text_dimensions(change_percent_str, change_font)
    change_percent_x = adjusted_width - change_percent_width - 10
    change_percent_y = change_dollar_y + change_dollar_height + scaling_factor
    draw.text((change_percent_x, change_percent_y), change_percent_str, font=change_font, fill=change_color)
    # Calculate start_y for the chart based on where the last text is drawn
    total_text_height = change_percent_y + change_percent_height
    chart_start_y = total_text_height + (3 * scaling_factor)  # Added some padding

    # Draw the chart
    draw_chart(draw, stock_data['daily_close_prices'], chart_start_y)
    
    return img

if __name__ == "__main__":
    # Test the rendering
    create_stock_image('AAPL').show()
