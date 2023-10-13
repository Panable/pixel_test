import requests
import logging
from io import BytesIO
import time
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from io import BytesIO

# Spotify setup (Note: Replace these placeholder values with actual ones.)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                               client_secret="YOUR_CLIENT_SECRET",
                                               redirect_uri="YOUR_REDIRECT_URI",
                                               scope="user-read-currently-playing user-read-playback-state"))

# Retrieve track information
track_info = sp.current_playback()
track_name = track_info['item']['name']
artist_name = track_info['item']['artists'][0]['name']
original_artist_name = artist_name
album_cover_url = track_info['item']['album']['images'][0]['url']
album_name = track_info['item']['album']['name']
# Matrix setup
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

class WindowCanvas:
    def __init__(self, delegatee, width, height, offset_x, offset_y):
        self.delegatee = delegatee
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
    
    def set_pixel(self, x, y, r, g, b):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return  # Clip to prevent drawing outside the window
        self.delegatee.SetPixel(x + self.offset_x, y + self.offset_y, r, g, b)
    
    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.set_pixel(x, y, 0, 0, 0)
    
    def fill(self, r, g, b):
        for y in range(self.height):
            for x in range(self.width):
                self.set_pixel(x, y, r, g, b)
# Get the album cover image
def get_album_cover_image(url, target_size=(32, 32)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))  # Using BytesIO to handle binary content
    img = img.resize(target_size, Image.LANCZOS)
    return img
album_cover = get_album_cover_image(album_cover_url)

# Create two window canvases: one for the album cover and one for the text
album_cover_window = WindowCanvas(matrix, 32, 32, 0, 0)
text_window = WindowCanvas(matrix, 32, 32, 32, 0)

# Main loop
scroll_pos_artist = 64
scroll_pos_album = 64
shift_artist = -1  # Shift per frame in pixels

# Define the start x-position and width of the right-side canvas
right_canvas_start_x = 32  # Assuming the left-side canvas (album cover) is 32 pixels wide
right_canvas_width = 32    # Assuming the right-side canvas is also 32 pixels wide

# Initial position of the artist name
scroll_pos_artist = right_canvas_start_x

logging.basicConfig(filename='scrolling_text.log', level=logging.DEBUG)

CLEAR_COLOR = graphics.Color(0, 0, 0)  # Black for now, but you can change this

RIGHT_CANVAS_START_X = 32
RIGHT_CANVAS_END_X = 63
try:
    while True:
        offscreen_canvas = matrix.CreateFrameCanvas()

        # Draw the album cover on the left half
        for y in range(32):  # Full height
            for x in range(32):  # Only the left half
                pixel = album_cover.getpixel((x, y))
                offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])

        # Calculate the width of the artist's name
        text_artist_width = graphics.DrawText(offscreen_canvas, font, -9999, -9999, color, artist_name)
        
        if text_artist_width > right_canvas_width:
            # Scroll the artist's name
            scroll_pos_artist -= 1
            # Reset position of the artist name when it goes off the canvas
            if scroll_pos_artist < right_canvas_start_x - text_artist_width:
                scroll_pos_artist = right_canvas_start_x + right_canvas_width
        else:
            # Center the artist's name if it's shorter than the canvas width
            scroll_pos_artist = right_canvas_start_x + (right_canvas_width - text_artist_width) // 2
        
        # Draw artist text
        graphics.DrawText(offscreen_canvas, font, scroll_pos_artist, 18, color, artist_name)       
        # Calculate the width of the album's name
        text_album_width = graphics.DrawText(offscreen_canvas, font, -9999, -9999, color, album_name)
        
        if text_album_width > right_canvas_width:
            # Scroll the album's name
            scroll_pos_album -= 1
            # Reset position of the album name when it goes off the canvas
            if scroll_pos_album < right_canvas_start_x - text_album_width:
                scroll_pos_album = right_canvas_start_x + right_canvas_width
        else:
            # Center the album's name if it's shorter than the canvas width
            scroll_pos_album = right_canvas_start_x + (right_canvas_width - text_album_width) // 2
        
        # Draw album text
        graphics.DrawText(offscreen_canvas, font, scroll_pos_album, 26, color, album_name)
        # Ensure any text that might overlap with the left canvas is cleared
        for y in range(32):  # Assuming the canvas is 32 pixels tall
            for x in range(32):  # Only the left half
                pixel = album_cover.getpixel((x, y))
                offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])

        # Logging
        logging.debug(f"Artist Name: {artist_name}")
        logging.debug(f"Text Artist Width: {text_artist_width}")
        logging.debug(f"Scroll Position Artist: {scroll_pos_artist}")
        logging.debug(f"Right Canvas Start X: {right_canvas_start_x}")
        logging.debug(f"Right Canvas Width: {right_canvas_width}")
        logging.debug("----")

        matrix.SwapOnVSync(offscreen_canvas)
        time.sleep(0.07)

except KeyboardInterrupt:
    # Graceful exit on Ctrl+C
    pass
finally:
    # Ensure the matrix is cleared on exit
    offscreen_canvas.Clear()
    matrix.SwapOnVSync(offscreen_canvas)

