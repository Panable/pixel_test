import logging
import requests
import time
from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from io import BytesIO
#Spotify stuff TODO

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="0bd953803d7c40049e275816cc208579",
                     client_secret="4442c4bde22048808a3b05a600323164",
                     redirect_uri="http://localhost:8000",
                     scope="user-read-currently-playing user-read-playback-state"))

track_info = sp.current_playback()

track_name = track_info['item']['name']
artist_name = track_info['item']['artists'][0]['name']
album_name = track_info['item']['album']['name']
album_cover_url = track_info['item']['album']['images'][0]['url']

print(track_name, artist_name, album_name, album_cover_url)

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

def draw_or_scroll_text_step(canvas, font, start_x, y, max_width, text, color, scroll_pos, shift=-1.5):
    text_width = graphics.DrawText(canvas, font, -9999, -9999, color, text)

    if text_width <= max_width:
        centered_x = start_x + (max_width - text_width) // 2
        graphics.DrawText(canvas, font, centered_x, y, color, text)
        return int(centered_x)

    new_pos = int(scroll_pos + shift)
    
    if new_pos <= start_x - text_width:
        new_pos = 64

    graphics.DrawText(canvas, font, new_pos, y, color, text)
    return int(new_pos)

def calculate_scroll_duration(text_width, max_width, shift):

    total_distance = max_width + text_width
    duration = total_distance / abs(shift)

    return duration
# Initial positions
scroll_pos_title, scroll_pos_artist, scroll_pos_album = 64, 64, 64
# Individual shift values for title, artist, and album
shift_title = -1.5
shift_artist = -1
shift_album = -1

album_cover = get_album_cover_image(album_cover_url)

# ...
log_file = open("log.txt", "a")

boundary = 96
available_width = 62
while True:
    offscreen_canvas = matrix.CreateFrameCanvas()

    # Fetch the album cover and paste it
    for y in range(8, 32):
        for x in range(32):
            pixel = album_cover.getpixel((x, y - 8))
            offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])

    scroll_pos_title = draw_or_scroll_text_step(offscreen_canvas, font, 0, 8, 64, track_name, color, scroll_pos_title, shift_title)
    
    
    # Calculate the width of the artist's name
    text_artist_width = graphics.DrawText(offscreen_canvas, font, -9999, -9999, color, artist_name)
    # Log details
    log_file.write(f"Artist Name: {artist_name}\n")
    log_file.write(f"Scroll Position Artist: {scroll_pos_artist}\n")
    log_file.write(f"Text Artist Width: {text_artist_width}\n")

    # Draw the artist's name
    graphics.DrawText(offscreen_canvas, font, scroll_pos_artist, 18, color, artist_name)
    
    # If the position of the first letter in artist_name hits the boundary, delete it
    if len(artist_name) > 0:
        if (scroll_pos_artist + text_artist_width) <= boundary:
            artist_name = artist_name[1:]
    else:
        # Reset the scroll position if the artist's name is empty
        scroll_pos_artist = 64

    # Continue scrolling
    scroll_pos_artist += shift_artist

    # Reset the scroll position if the entire artist's name is off the canvas
    if scroll_pos_artist < -text_artist_width:
        scroll_pos_artist = 64
        artist_name = track_info['item']['artists'][0]['name']
    time.sleep(0.07)
    matrix.SwapOnVSync(offscreen_canvas)
