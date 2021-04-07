import json
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, close_room
from flask_session import Session
import classes
from datetime import datetime
import requests
import urllib
import base64
from hashlib import sha256
from random import choice, randint
from string import ascii_letters, digits
import re
import os
import time


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
state = ''.join(choice(ascii_letters + digits + '_.-~') for i in range(128))
state_encoded = base64.b64encode(bytes(state,encoding='utf8'))

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
    if not session.get("spotify_data"):
        # adds spotify log in button
        socketio.emit("add_spotify_button",room=request.sid)
    else:
        pass


# spotify login
@app.route("/spotify-login/")
def spotify_login():
    #Code challenge/verifier generation
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)
    session['code_verifier'] = code_verifier
    code_challenge = sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')    
    #Constructing body
    query_data = {'client_id':client_id, 'response_type':'code', 'redirect_uri':redirect_uri, 'code_challenge_method':'S256', 'code_challenge':code_challenge,'state':state}
    query = urllib.parse.urlencode(query_data)
    auth_redirect = 'https://accounts.spotify.com/authorize?'+query
    return redirect(auth_redirect)


# After authorization saves token_info to cookies and redirects to main
@app.route("/spotify-login/callback/")
def authentication():
    callback_state = request.args.get('state')
    if state != callback_state:
        # abort
        print('Callback state does not match')
        return redirect(myurl)
    else:
        auth_code = request.args.get("code")
        #post request
        user_data = requests.post('https://accounts.spotify.com/api/token', data = {'client_id': client_id, 'grant_type': 'authorization_code', 'code': auth_code, 'redirect_uri': redirect_uri, 'code_verifier':session['code_verifier']})
        if user_data.status_code == 200:
            session['spotify_data'] = user_data.json()
            session['spotify_data']['expires_at'] = int(time.time()) + session['spotify_data']['expires_in']
        else:
            print('Error: ' + str(user_data.status_code))
        return redirect(myurl)

# checks if token needs to be refreshed and does so, if not just returns access token
def getToken(session):
    # If expired, fetch refreshed token
    if session[['spotify_data']['expires_at'] > int(time.time()):
        user_data = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type': 'refresh_token', 'refresh_token': session['spotify_data']['refresh_token'], 'client_id': client_id})
        if user_data.status_code == 200:
            session['spotify_data'] = user_data.json()
            session['spotify_data']['expires_at'] = int(time.time()) + session['spotify_data']['expires_in']
        else:
            print('Error: ' + str(user_data.status_code))
    return session['spotify_data']['access_token']

if __name__ == "__main__":
    socketio.run(app)