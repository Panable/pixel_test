import requests
import logging
import time
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from io import BytesIO

# Spotify setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                               client_secret="YOUR_CLIENT_SECRET",
                                               redirect_uri="YOUR_REDIRECT_URI",
                                               scope="user-read-currently-playing user-read-playback-state"))

track_info = sp.current_playback()
track_name = track_info['item']['name']
artist_name = track_info['item']['artists'][0]['name']
original_artist_name = artist_name
album_name = track_info['item']['album']['name']
album_cover_url = track_info['item']['album']['images'][0]['url']
# Matrix setup stuff
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.gpio_slowdown = 4 
matrix = RGBMatrix(options=options)

font_path = "/usr/local/share/fonts/4x6.bdf"
font = graphics.Font()
font.LoadFont(font_path)
color = graphics.Color(255, 255, 255)

def get_album_cover_image(url, target_size=(32, 24)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.resize(target_size, Image.LANCZOS)
    return img

def calculate_frames(text_width, display_width, offset_start, offset_end, delay):
    total_distance = display_width + text_width + offset_start + offset_end
    return total_distance + delay

def scroll_text(canvas, text, text_width, frame_idx, start_x, y, display_width, offset_start, offset_end, delay, color, font):
    # If we're still in the delay phase, draw the text at the starting offset
    if frame_idx < delay:
        graphics.DrawText(canvas, font, start_x + offset_start, y, color, text)
        return
    
    # Calculate the effective frame index by deducting the delay
    effective_frame = frame_idx - delay
    
    # Calculate the position to draw the text
    draw_position = start_x + offset_start - effective_frame
    
    # If we've scrolled past the end offset, loop back to the start
    if draw_position < -text_width - offset_end:
        draw_position = start_x + offset_start
    
    graphics.DrawText(canvas, font, draw_position, y, color, text)

album_cover = get_album_cover_image(album_cover_url)

# Initialize frame index
frame_idx = 0

# Define parameters for the scrolling
offset_start = 5
offset_end = 5
delay = 30  # Delay in frames

# Initial positions
scroll_pos_artist = 64

base_shift = -1  # Shift per frame in pixels
boundary = 96  # X coordinate boundary after which letters should start being deleted

# Initialize a frame counter
frame_counter = 0

# Initialize a deletion counter
deletion_counter = 0.0

# Define a deletion rate
deletion_rate = 1

logging.basicConfig(filename='marquee_log.txt', level=logging.DEBUG)

while True:
    offscreen_canvas = matrix.CreateFrameCanvas()
    
    # Fetch the album cover and paste it
    for y in range(8, 32):
        for x in range(32):
            pixel = album_cover.getpixel((x, y - 8))
            offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])
    
    # Calculate the width of the artist's name
    text_artist_width = graphics.DrawText(offscreen_canvas, font, -9999, -9999, color, artist_name)
    
    # If the end of the text has crossed the boundary and there's more than one character in the artist name
    if scroll_pos_artist + text_artist_width <= boundary and len(artist_name) > 1:
        # Remove the first character
        artist_name = artist_name[1:]
        # Compensate the scroll position for deletion
        scroll_pos_artist -= base_shift * 2  # Compensating more to slow down deletion apparent speed
    else:
        # Scroll the text to the left by base_shift units
        scroll_pos_artist += base_shift
    
    # Draw the artist's name
    graphics.DrawText(offscreen_canvas, font, scroll_pos_artist, 18, color, artist_name)
    logging.debug(f'Frame: {frame_counter}')
    logging.debug(f'Artist Name: {artist_name}')
    logging.debug(f'Scroll Position: {scroll_pos_artist}')
    logging.debug(f'Text Width: {text_artist_width}')
    logging.debug(f'Boundary: {boundary}') 
    time.sleep(0.07)
    matrix.SwapOnVSync(offscreen_canvas)

    # Increment frame counter
    frame_counter += 1
