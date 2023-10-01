
def draw_chart_on_matrix(matrix_img, draw, daily_close_prices, start_y, polygon_color, line_color):
    # Find the dimensions of the matrix
    width, height = matrix_img.size
    
    # Normalize the prices
    min_price = min(daily_close_prices)
    max_price = max(daily_close_prices)
    price_range = max_price - min_price

    # The scaling factor to fit the prices in the matrix height
    scale_factor = (height - start_y) / price_range

    normalized_prices = [(price - min_price) * scale_factor for price in daily_close_prices]

    # Adjust the normalized prices so that the chart starts from start_y
    adjusted_prices = [height - (price + start_y) for price in normalized_prices]

    # Create the polygon points
    polygon_points = [(x, adjusted_prices[x]) for x in range(width)] 
    polygon_points = [(0, height)] + polygon_points + [(width-1, height)]  # Adding base points for the polygon

    # Draw the polygon
    draw.polygon(polygon_points, fill=polygon_color)

    # Draw the line on top of the polygon
    line_points = [(x, adjusted_prices[x]) for x in range(width)]
    draw.line(line_points, fill=line_color)

    return matrix_img
