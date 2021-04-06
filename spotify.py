import json
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, close_room
import spotipy.oauth2 as oauth2
from flask_session import Session
import spotipy
import classes
import random
from datetime import datetime
import requests
import urllib
import base64


# making a flask socket object
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config[
    "SECRET_KEY"
] = "z\xe4\xdc\xc4)\xf1\xad\x8dF\x07EVv8k\x14\xda\xd8\xd0\x8a\xc4\xbc\xaew\x98\xf1\x0f\xfa\x01\x90"
socketio = SocketIO(app, always_connect=True)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = False
# session stuff
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# list of room codes
active_rooms = []
# list of gamestates
gamestates = [None] * 9000


myurl = "http://127.0.0.1:5000/"

# spotify auth stuff
client_id = "f50f20e747fb4bda8d9352696004cda4"
client_secret = "8adcb482dbf04ddbb261b7740309325e"
redirect_uri = myurl+'spotify-login/callback/'
query_data = {'client_id':client_id, 'response_type':'code', 'redirect_uri':redirect_uri}
query = urllib.parse.urlencode(query_data)
auth_redirect = 'https://accounts.spotify.com/authorize?'+query

# main page
@app.route("/")
def main():
    if not session.get('unique'):
        session["unique"] = datetime.now().time()
    return render_template("mainmenu_test.html")



# If user logged into spotify adds playlists as options
@socketio.on("connected_to_main")
def setupMain():
    # If no access to spotify adds spotify log in button
    if not session.get("token_info"):
        # adds spotify log in button
        socketio.emit("add_spotify_button",room=request.sid)

# spotify login
@app.route("/spotify-login/")
def spotify_login():
    # if already logged in redirect to main menu, checks if token info exists
    return redirect(auth_redirect)


# After authorization saves token_info to cookies and redirects to main
@app.route("/spotify-login/callback/")
def authentication():
    auth_code = request.args.get("code")
    print(auth_code)
    encodedData = base64.b64encode(bytes(f"{client_id}:{client_secret}", "ISO-8859-1")).decode("ascii")
    authorization_header_string = f"Authorization: Basic {encodedData}"
    user_data = requests.post('https://accounts.spotify.com/api/token', 
    data = {'grant_type': 'authorization_code', 'code': auth_code, 'redirect_uri': redirect_uri}, 
    auth = (client_id, client_secret)).json()
    session['spotify_data'] = user_data
    print(session['spotify_data'])
    return redirect(myurl)

# def get_token(session):
#     token_valid = False
#     token_info = session.get("token_info", {})
#     # Checking if the session already has a token stored
#     if not (session.get("token_info", False)):
#         token_valid = False
#         return token_info, token_valid

#     # Checking if token has expired
#     now = int(time.time())
#     is_token_expired = session.get("token_info").get("expires_at") - now < 60

#     # Refreshing token if it has expired
#     if is_token_expired:
#         # Don't reuse a SpotifyOAuth object because they store token info
#         sp_oauth = spotipy.oauth2.SpotifyOAuth(
#             client_id=SPOTIPY_CLIENT_ID,
#             client_secret=SPOTIPY_CLIENT_SECRET,
#             redirect_uri=SPOTIPY_REDIRECT_URI,
#             scope=SCOPE,
#         )
#         token_info = sp_oauth.refresh_access_token(
#             session.get("token_info").get("refresh_token")
#         )

#     token_valid = True
#     return token_info, token_valid




if __name__ == "__main__":
    socketio.run(app)