import os
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = "user-read-currently-playing user-read-recently-played"

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
    open_browser=False,
    cache_path=".spotify_cache"
)

@app.route("/")
def home():
    return "Backend running OK"

@app.route("/login")
def login():
    return redirect(auth_manager.get_authorize_url())

@app.route("/callback")
def callback():
    code = request.args.get("code")
    auth_manager.get_access_token(code)
    return "AUTHORIZED — Close this tab"

@app.route("/now-playing")
def now_playing():
    if not auth_manager.validate_token(auth_manager.cache_handler.get_cached_token()):
        return jsonify({"error": "not_authorized"}), 401

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # LIVE SONG
    current = sp.current_user_playing_track()
    if current and current["is_playing"]:
        t = current["item"]
        return jsonify({
            "mode": "live",
            "title": t["name"],
            "artist": t["artists"][0]["name"],
            "album_art": t["album"]["images"][0]["url"],
            "url": t["external_urls"]["spotify"]
        })

    # LAST PLAYED
    recent = sp.current_user_recently_played(limit=1)
    if recent and recent["items"]:
        t = recent["items"][0]["track"]
        return jsonify({
            "mode": "history",
            "title": t["name"],
            "artist": t["artists"][0]["name"],
            "album_art": t["album"]["images"][0]["url"],
            "url": t["external_urls"]["spotify"]
        })

    return jsonify({"mode": "none"})
