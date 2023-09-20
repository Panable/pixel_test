from PIL import Image, ImageDraw, ImageFont
from getweather import get_weather
import os
from textwrap import wrap
import numpy as np
from rgbmatrix import RGBMatrix, RGBMatrixOptions

TEMP_FONT_SIZE_FACTOR = 1.0 
ICON_SCALE_FACTOR = 0.6  
TOP_PADDING = 3

width, height = 64, 32

# Assuming that the font is located at the given path, adjust if necessary
font_path = "/usr/local/share/fonts/Dina-Regular-01.ttf"
time_font_size = 14
temp_font_size = 12  

time_font = ImageFont.truetype(font_path, time_font_size)
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
    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    time_str = format_time(current_time)
    hour_str, minute_str = time_str.split(":")
    
    hour_width, hour_height = get_text_dimensions(hour_str, time_font)
    minute_width, minute_height = get_text_dimensions(minute_str, time_font)
    total_width = hour_width + minute_width + 1

    colon_center_x = (width - total_width) // 2 + hour_width + 1
    hour_x = colon_center_x - hour_width - 1
    minute_x = colon_center_x + 1

    draw.text((hour_x, TOP_PADDING), hour_str, font=time_font, fill=(255, 255, 255))
    draw.text((minute_x, TOP_PADDING), minute_str, font=time_font, fill=(255, 255, 255))
    colon_center_y = 7
    colon_spacing = 2
    draw.rectangle([(colon_center_x, colon_center_y - colon_spacing),
                    (colon_center_x, colon_center_y - colon_spacing + 1)], fill=(255, 255, 255))
    draw.rectangle([(colon_center_x, colon_center_y + colon_spacing),
                    (colon_center_x, colon_center_y + colon_spacing + 1)], fill=(255, 255, 255))

    weather_image_path, temp_str = get_weather()
    temp_str_with_symbol = f"{temp_str}°C"
    
    # Load and adjust the size of weather icon 
    weather_image = Image.open(weather_image_path)
    upscale_factor = int(16 * ICON_SCALE_FACTOR)  
    weather_image = weather_image.resize((upscale_factor, upscale_factor))
    icon_width, icon_height = weather_image.size

    start_y = (height - icon_height) // 2 + TOP_PADDING

    start_x = (width - icon_width) // 2

    # Position the icon
    icon_y = start_y
    img.paste(weather_image, (start_x, icon_y))

    # Position the temperature
    temp_x = start_x + icon_width + 1  
    temp_y = icon_y + icon_height - temp_font_size
    draw.text((temp_x, temp_y), str(temp_str_with_symbol), font=temp_font, fill=(255, 255, 255))

    return img


