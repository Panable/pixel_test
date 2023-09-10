from PIL import Image, ImageDraw, ImageFont
from getweather import get_weather

scaling_factor = 40
adjusted_width, adjusted_height = 64 * scaling_factor, 32 * scaling_factor

font_path = "/usr/local/share/fonts/ProggyCleanCENerdFontMono-Regular.ttf"
time_font_size = 14 * scaling_factor
icon_font_size = 10 * scaling_factor 
temp_font_size = 12 * scaling_factor  

time_font = ImageFont.truetype(font_path, time_font_size)
icon_font = ImageFont.truetype(font_path, icon_font_size)
temp_font = ImageFont.truetype(font_path, temp_font_size)

def get_text_dimensions(text_string, font):
    text_string = str(text_string)
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def format_time(current_time):
    hour_str, minute_str = current_time
    return f"{hour_str}:{minute_str}"


def create_time_image(current_time, city='Sydney'):
    img = Image.new('RGB', (adjusted_width, adjusted_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    time_str = format_time(current_time)
    hour_str, minute_str = time_str.split(":")

    hour_width, hour_height = get_text_dimensions(hour_str, time_font)
    minute_width, minute_height = get_text_dimensions(minute_str, time_font)

    # Calculate the total width 
    total_width = hour_width + minute_width + scaling_factor

    # Calculate colon spacing
    colon_center_x = (adjusted_width - total_width) // 2 + hour_width + scaling_factor // 2

    # Adjust for colon spacing
    hour_x = colon_center_x - hour_width - 75 
    minute_x = colon_center_x + 75

    # Drawing the hour and minute
    draw.text((hour_x, 2 * scaling_factor), hour_str, font=time_font, fill=(255, 255, 255))
    draw.text((minute_x, 2 * scaling_factor), minute_str, font=time_font, fill=(255, 255, 255))

    # Colon vertical pos 
    colon_center_y = 7 * scaling_factor
    colon_spacing = scaling_factor * 2
    draw.rectangle([(colon_center_x - scaling_factor // 2, colon_center_y - colon_spacing),
                    (colon_center_x + scaling_factor // 2, colon_center_y - colon_spacing + scaling_factor)], fill=(255, 255, 255))
    draw.rectangle([(colon_center_x - scaling_factor // 2, colon_center_y + colon_spacing),
                    (colon_center_x + scaling_factor // 2, colon_center_y + colon_spacing + scaling_factor)], fill=(255, 255, 255))

    # Fetch weather 
    icon_str, temp_str = get_weather()
    temp_str_with_symbol = f"{temp_str}°C"
    icon_width, icon_height = get_text_dimensions(icon_str, icon_font)
    temp_width, temp_height = get_text_dimensions(temp_str_with_symbol, temp_font)
    
    # Calculate the x positions
    icon_x = (adjusted_width - (icon_width + scaling_factor + temp_width)) // 2
    temp_x = icon_x + icon_width + scaling_factor
    
    # Drawing the weather 
    draw.text((icon_x, 18 * scaling_factor), str(icon_str), font=icon_font, fill=(255, 255, 255))
    draw.text((temp_x, 18 * scaling_factor), str(temp_str_with_symbol), font=temp_font, fill=(255, 255, 255))
    
    return img
   
