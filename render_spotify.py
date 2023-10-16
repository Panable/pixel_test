from flask import Flask, request, jsonify
import requests
import logging
from io import BytesIO
import time
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from io import BytesIO
import base64
import websocket
import json

app = Flask(__name__)
# Spotify setup (Note: Replace these placeholder values with actual ones.)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="0bd953803d7c40049e275816cc208579",
                                               client_secret="4442c4bde22048808a3b05a600323164",
                                               redirect_uri="http://localhost:8000/callback",
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
options.hardware_mapping = 'adafruit-hat-pwm'
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
@app.route('/refresh_token', methods=['GET'])
def refresh_token_endpoint():
    global current_access_token, current_refresh_token

    refresh_token = request.args.get('refresh_token')
    auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_string}'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    
    if response.status_code == 200:
        current_access_token = response.json().get('access_token')
        current_refresh_token = response.json().get('refresh_token', current_refresh_token)
        return jsonify(access_token=current_access_token)
    else:
        return "Error refreshing token", 400


def refresh_token():
    global current_access_token

    response = requests.get(f"http://localhost:5000/refresh_token?refresh_token={current_refresh_token}")
    if response.status_code == 200:
        current_access_token = response.json().get('access_token')
        return current_access_token
    else:
        # Handle the error
        return None
#Get album image
def get_album_cover_image(url, target_size=(26, 26)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.convert("RGB")  # Ensure the image is in RGB mode
    img = img.resize(target_size, Image.LANCZOS)
    return img
if __name__ == "__main__":
    # Run the Flask app on a different thread so it doesn't block the main execution
    from threading import Thread
    t = Thread(target=app.run, kwargs={'debug': False})
    t.start()

def on_message(ws, message):
    data = json.loads(message)
    if 'event' in data:
        event_type = data['event']
        if event_type == 'track_change':
            track_info = data['track']
            update_matrix_display(track_info)

def update_matrix_display(track_info):
    global track_name, artist_name, album_cover, album_name, current_track_id
album_cover = get_album_cover_image(album_cover_url)

# Create two window canvases: one for the album cover and one for the text
album_cover_window = WindowCanvas(matrix, 32, 32, 0, 0)
text_window = WindowCanvas(matrix, 32, 32, 32, 0)

scroll_pos_artist = 64
scroll_pos_album = 64
scroll_pos_track = 64
shift_artist = -1

# Define the start x-position and width of the right-side canvas
right_canvas_start_x = 32 - 4 
right_canvas_width = 32    

# Initial position of the artist name
scroll_pos_artist = right_canvas_start_x

logging.basicConfig(filename='scrolling_text.log', level=logging.DEBUG)

CLEAR_COLOR = graphics.Color(0, 0, 0)  # Black for now, but you can change this

RIGHT_CANVAS_START_X = 32
RIGHT_CANVAS_END_X = 63
ALBUM_COVER_Y_POSITION = 32 - 22 - 2  
ALBUM_COVER_X_POSITION = 2
TRACK_Y_POSITION = 7

track_name_color = graphics.Color(29, 185, 84)
prev_track_id = None
offscreen_canvas = matrix.CreateFrameCanvas()
last_polled_time = 0
last_known_timestamp = 0
current_track_id = None
try:
    while True:
#        offscreen_canvas = matrix.CreateFrameCanvas()
        current_time = time.time()
        if current_time - last_polled_time >= 1:  # Check every 5 seconds for track changes
            previous_track_id = current_track_id
            new_track_id = update_track_details()
            if previous_track_id != new_track_id:  # A track change was detected
                offscreen_canvas.Clear()
            last_polled_time = current_time
        offscreen_canvas.Clear() 
        # Draw the album cover on the left half
        for y in range(ALBUM_COVER_Y_POSITION, ALBUM_COVER_Y_POSITION + 22):  
            for x in range(ALBUM_COVER_X_POSITION, ALBUM_COVER_X_POSITION + 22):
                pixel = album_cover.getpixel((x - ALBUM_COVER_X_POSITION, y - ALBUM_COVER_Y_POSITION))
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
        graphics.DrawText(offscreen_canvas, font, scroll_pos_album, 25, color, album_name)
        # Ensure any text that might overlap with the left canvas is cleared
        for y in range(ALBUM_COVER_Y_POSITION, ALBUM_COVER_Y_POSITION + 22):  
            for x in range(ALBUM_COVER_X_POSITION, ALBUM_COVER_X_POSITION + 22):
                pixel = album_cover.getpixel((x - ALBUM_COVER_X_POSITION, y - ALBUM_COVER_Y_POSITION))
                offscreen_canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])
        
        for y in range(32):  # Assuming the canvas height is 32 pixels
            offscreen_canvas.SetPixel(0, y, 0, 0, 0)  # Set the first column pixel to black
            offscreen_canvas.SetPixel(1, y, 0, 0, 0)  # Set the second column pixel to black
        text_track_width = graphics.DrawText(offscreen_canvas, font, -9999, -9999, track_name_color, track_name)
         
        if text_track_width > 64:  # Assuming the entire matrix width is 64 pixels
            # Scroll the track's name
            scroll_pos_track -= 1
            # Reset position of the track name when it goes off the canvas
            if scroll_pos_track < -text_track_width:
                scroll_pos_track = 64
        else:
            # Center the track's name if it's shorter than the matrix width
            scroll_pos_track = (64 - text_track_width) // 2 
        text_track_width = graphics.DrawText(offscreen_canvas, font, -9999, -9999, color, track_name)
        graphics.DrawText(offscreen_canvas, font, scroll_pos_track, TRACK_Y_POSITION, track_name_color, track_name)
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
    pass
finally:
    offscreen_canvas.Clear()
    matrix.SwapOnVSync(offscreen_canvas)

