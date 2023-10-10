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
    """
    Draw or scroll the text. If the text width is larger than max_width, it will be scrolled.
    Otherwise, it will be centered within the max_width.
    """

    # Calculate the width of the text
    text_width = graphics.DrawText(canvas, font, -9999, -9999, color, text)

    # If the text fits within the bounds, draw it centered
    if text_width <= max_width:
        centered_x = start_x + (max_width - text_width) // 2
        graphics.DrawText(canvas, font, centered_x, y, color, text)
        return start_x  # No scrolling needed, so return the starting position

    # If we need to scroll, start drawing the text from the current scroll position
    new_pos = scroll_pos + shift
    if new_pos + text_width <= start_x:  # If the text has scrolled past the left boundary, reset
        new_pos = start_x + max_width
    graphics.DrawText(canvas, font, new_pos, y, color, text)
    return new_pos

def calculate_scroll_duration(text_width, shift):
    return abs(text_width / shift)

# Initial positions
scroll_pos_title, scroll_pos_artist, scroll_pos_album = 64, 34, 34

# Individual shift values for title, artist, and album
shift_title = -1.5
shift_artist = -1
shift_album = -1

album_cover = get_album_cover_image(album_cover_url)
while True:
    offscreen_canvas = matrix.CreateFrameCanvas()

    # Fetch the album cover and paste it
    for y in range(8, 32):
        for x in range(32):
            pixel = album_cover.getpixel((x, y - 8))
            offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])

    # Calculate durations for artist and album
    duration_artist = calculate_scroll_duration(graphics.DrawText(offscreen_canvas, font, -9999, -9999, color, artist_name), shift_artist)
    duration_album = calculate_scroll_duration(graphics.DrawText(offscreen_canvas, font, -9999, -9999, color, album_name), shift_album)

    max_duration = max(duration_artist, duration_album)

    artist_wait_time = max_duration - duration_artist
    album_wait_time = max_duration - duration_album

    artist_wait_counter = 0
    album_wait_counter = 0

    scroll_pos_title = draw_or_scroll_text_step(offscreen_canvas, font, 0, 8, 64, track_name, color, scroll_pos_title, shift_title)
    
    if artist_wait_counter <= 0:
        scroll_pos_artist = draw_or_scroll_text_step(offscreen_canvas, font, 34, 18, 30, artist_name, color, scroll_pos_artist, shift_artist)
    else:
        artist_wait_counter -= 1
        
    if album_wait_counter <= 0:
        scroll_pos_album = draw_or_scroll_text_step(offscreen_canvas, font, 34, 28, 30, album_name, color, scroll_pos_album, shift_album)
    else:
        album_wait_counter -= 1

    # Check if we need to reset
    if scroll_pos_artist == 0:
        artist_wait_counter = int(artist_wait_time / 0.07)
    if scroll_pos_album == 0:
        album_wait_counter = int(album_wait_time / 0.07)

    time.sleep(0.07)
    matrix.SwapOnVSync(offscreen_canvas)
