
from PIL import Image, ImageDraw, ImageFont
from getweather import get_weather
import os
from textwrap import wrap
TEMP_FONT_SIZE_FACTOR = 1.0 
ICON_SCALE_FACTOR = 0.6  
TOP_PADDING = 100

scaling_factor = 40
adjusted_width, adjusted_height = 64 * scaling_factor, 32 * scaling_factor

font_path = "/usr/local/share/fonts/ProggyCleanCENerdFontMono-Regular.ttf"
time_font_size = 14 * scaling_factor
temp_font_size = 12 * scaling_factor  

time_font = ImageFont.truetype(font_path, time_font_size)
temp_font = ImageFont.truetype(font_path, temp_font_size)

def get_text_dimensions(text_string, font):
    text_string = str(text_string)
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def get_y_and_heights(text_wrapped, dimensions, margin, font):
    ascent, descent = font.getmetrics()
    line_heights = [
        font.getmask(text_line).getbbox()[3] + descent + margin
        for text_line in text_wrapped
    ]
    line_heights[-1] -= margin
    height_text = sum(line_heights)
    y = (dimensions[1] - height_text) // 2
    return (y, line_heights)

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
    total_width = hour_width + minute_width + scaling_factor

    colon_center_x = (adjusted_width - total_width) // 2 + hour_width + scaling_factor // 2
    hour_x = colon_center_x - hour_width - 75 
    minute_x = colon_center_x + 75

    draw.text((hour_x, 2 * scaling_factor), hour_str, font=time_font, fill=(255, 255, 255))
    draw.text((minute_x, 2 * scaling_factor), minute_str, font=time_font, fill=(255, 255, 255))
    colon_center_y = 7 * scaling_factor
    colon_spacing = scaling_factor * 2
    draw.rectangle([(colon_center_x - scaling_factor // 2, colon_center_y - colon_spacing),
                    (colon_center_x + scaling_factor // 2, colon_center_y - colon_spacing + scaling_factor)], fill=(255, 255, 255))
    draw.rectangle([(colon_center_x - scaling_factor // 2, colon_center_y + colon_spacing),
                    (colon_center_x + scaling_factor // 2, colon_center_y + colon_spacing + scaling_factor)], fill=(255, 255, 255))

    weather_image_path, temp_str = get_weather()
    temp_str_with_symbol = f"{temp_str}°C"
    
    # Adjust the size of temperature to scale factors 
    adjusted_temp_font_size = int(temp_font_size * TEMP_FONT_SIZE_FACTOR)
    temp_font_adjusted = ImageFont.truetype(font_path, adjusted_temp_font_size)
    temp_width, temp_height = get_text_dimensions(temp_str_with_symbol, temp_font_adjusted)

    # Load and adjust the size of weather icon 
    weather_image = Image.open(weather_image_path)
    upscale_factor = int(16 * 40 * ICON_SCALE_FACTOR)  # Original size times default scaling times iconscale factor
    weather_image = weather_image.resize((upscale_factor, upscale_factor))
    icon_width, icon_height = weather_image.size

    # Calculate the vertical positioning of the combined icon and temperature text
    combined_height = icon_height + temp_height
    start_y = (adjusted_height - combined_height) // 2 + TOP_PADDING

    # Calculate total width required for both icon and temperature
    total_width = icon_width + temp_width + scaling_factor  # Include a gap (scaling_factor) between the icon and the temperature

    # Calculate starting x-coordinates to center the combination of icon + temperature
    start_x = (adjusted_width - total_width) // 2

    # Position the icon
    icon_y = start_y + (combined_height - icon_height) // 2  # Center the icon vertically relative to the temperature text
    img.paste(weather_image, (start_x, icon_y))

    # Position the temperature
    temp_x = start_x + icon_width + scaling_factor  # Add icon's width and the gap
    temp_y = icon_y + icon_height - temp_height  # Bottom-align the temperature with the icon
    draw.text((temp_x, temp_y), str(temp_str_with_symbol), font=temp_font_adjusted, fill=(255, 255, 255))

    return img

