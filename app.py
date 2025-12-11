import os
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
print("CID:", os.getenv("SPOTIPY_CLIENT_ID"))
print("CSECRET:", os.getenv("SPOTIPY_CLIENT_SECRET"))
print("REDIRECT:", os.getenv("SPOTIPY_REDIRECT_URI"))


app = Flask(__name__)
CORS(app)

# Use a stable secret key
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = 'user-read-currently-playing user-read-playback-state user-read-recently-played'

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
    cache_path=".spotify_cache",
    show_dialog=True
)




@app.route('/')
def home():
    return "Spotify Backend Online — <a href='/login'>Login</a>"

@app.route('/login')
def login():
    return redirect(auth_manager.get_authorize_url())

@app.route('/callback')
def callback():
    code = request.args.get('code')
    auth_manager.get_access_token(code, check_cache=False)
    return "Authorization successful! You can close this tab."

@app.route('/api/now-playing')
def now_playing():
    # If no token, no data.
    token_info = auth_manager.cache_handler.get_cached_token()
    if not auth_manager.validate_token(token_info):
        return jsonify({"is_playing": False, "error": "Not authorized"}), 401

    sp = spotipy.Spotify(auth_manager=auth_manager)

    try:
        # First try CURRENTLY PLAYING
        current = sp.current_user_playing_track()

        if current and current.get("is_playing"):
            track = current["item"]
            return jsonify({
                "mode": "live",
                "is_playing": True,
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album_art": track["album"]["images"][0]["url"],
                "url": track["external_urls"]["spotify"]
            })

        # Otherwise fallback to LAST PLAYED TRACK
        recent = sp.current_user_recently_played(limit=1)

        if recent and recent.get("items"):
            last = recent["items"][0]["track"]
            return jsonify({
                "mode": "history",
                "is_playing": False,
                "title": last["name"],
                "artist": last["artists"][0]["name"],
                "album_art": last["album"]["images"][0]["url"],
                "url": last["external_urls"]["spotify"]
            })

        # If NOTHING exists (you account is a barren wasteland)
        return jsonify({
            "mode": "empty",
            "is_playing": False,
            "status": "No playback history found"
        })

    except Exception as e:
        print("Error in /api/now-playing:", e)
        return jsonify({"is_playing": False, "error": str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
