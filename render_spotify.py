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
import threading

app = Flask(__name__)

client_id = "0bd953803d7c40049e275816cc208579" 
client_secret="4442c4bde22048808a3b05a600323164",
redirect_uri="http://localhost:8000/callback",

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="0bd953803d7c40049e275816cc208579",
                                               client_secret="4442c4bde22048808a3b05a600323164",
                                               redirect_uri="http://localhost:8000/callback",
                                               scope="user-read-currently-playing user-read-playback-state")) 

shared_data = {
    'track_name': None,
    'artist_name': None,
    'album_name': None,
    'album_cover': None
}

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

@app.route('/refresh_token', methods=['GET'])
def refresh_token_endpoint():
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
        access_token = response.json().get('access_token')
        return jsonify(access_token=access_token)
    else:
        return "Error refreshing token", 400

def refresh_token():
    # Assuming you stored your refresh token in a variable named refresh_token
    response = requests.get(f"http://localhost:5000/refresh_token?refresh_token={refresh_token}")
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        # Handle the error
        return None

if __name__ == "__main__":
    # Run the Flask app on a different thread
    flask_thread = threading.Thread(target=app.run, kwargs={'debug': False, 'port': 5000})
    flask_thread.start()

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


def poll_spotify_for_changes():
    global shared_data

    while True:
        track_info = sp.current_playback()
        
        if track_info:
            shared_data["track_info"] = track_info
            shared_data["track_name"] = track_info['item']['name']
            shared_data["artist_name"] = track_info['item']['artists'][0]['name']
            shared_data["album_cover_url"] = track_info['item']['album']['images'][0]['url']
            shared_data["album_name"] = track_info['item']['album']['name']

        time.sleep(1)  # Poll every second

polling_thread = threading.Thread(target=poll_spotify_for_changes)
polling_thread.daemon = True  # This ensures the thread will exit when the main program exits
polling_thread.start()

# Get album image
def get_album_cover_image(url, target_size=(26, 26)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.convert("RGB")  # Ensure the image is in RGB mode
    img = img.resize(target_size, Image.LANCZOS)
    return img
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


CLEAR_COLOR = graphics.Color(0, 0, 0)  # Black for now, but you can change this

RIGHT_CANVAS_START_X = 32
RIGHT_CANVAS_END_X = 63
ALBUM_COVER_Y_POSITION = 32 - 22 - 2  
ALBUM_COVER_X_POSITION = 2
TRACK_Y_POSITION = 7

track_name_color = graphics.Color(29, 185, 84)
try:
    while True:
        offscreen_canvas = matrix.CreateFrameCanvas()

        # Fetch the latest track details from shared_data
        track_name = shared_data["track_name"]
        artist_name = shared_data["artist_name"]
        album_cover_url = shared_data["album_cover_url"]
        album_name = shared_data["album_name"]
        album_cover = get_album_cover_image(album_cover_url)

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

