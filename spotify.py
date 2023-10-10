import spotipy
from spotipy.oauth2 import SpotifyOAuth

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
