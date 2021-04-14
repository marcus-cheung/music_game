from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, close_room
from flask_session import Session

import classes
from spotify_handler import *
from methods import *

import random
import time
import os
import shutil
import json
import requests
import urllib
import base64
import re
from hashlib import sha256
from string import ascii_letters, digits


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

#http://127.0.0.1:5000/super-secret-default-spotify/


# auth stuff chr
client_id = "f50f20e747fb4bda8d9352696004cda4"
client_secret = "8adcb482dbf04ddbb261b7740309325e"
redirect_uri = myurl + 'spotify-login/callback/'
default_redirect_uri = myurl + 'super-secret-default-spotify/callback/'
state = ''.join(random.choice(ascii_letters + digits + '_.-~') for i in range(128))


@app.route('/super-secret-default-spotify/')
def super_secret_default_spotify():
    #Code challenge/verifier generation
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)
    session['code_verifier'] = code_verifier
    code_challenge = sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')    
    #Constructing body
    scopes = 'playlist-read-private playlist-read-collaborative user-read-private'
    query_data = {'client_id':client_id, 'response_type':'code', 'redirect_uri':default_redirect_uri, 'code_challenge_method':'S256', 'code_challenge':code_challenge,'scope':scopes,'state':state}
    query = urllib.parse.urlencode(query_data)
    auth_redirect = 'https://accounts.spotify.com/authorize?'+query
    return redirect(auth_redirect)

@app.route("/super-secret-default-spotify/callback/")
def super_secret_default_spotify_callback():
    callback_state = request.args.get('state')
    if state != callback_state:
        # abort
        print('Callback state does not match')
        return redirect(myurl)
    else:
        auth_code = request.args.get("code")
        #post request
        user_data = requests.post('https://accounts.spotify.com/api/token', data = {'client_id': client_id, 'grant_type': 'authorization_code', 'code': auth_code, 'redirect_uri': default_redirect_uri, 'code_verifier':session['code_verifier']})
        if user_data.status_code == 200:
            spotify_data = user_data.json()
            spotify_data['expires_at'] = int(time.time()) + spotify_data['expires_in']
            #save new data into json file
            with open('static/default_spotify.json', 'w') as f:
                json.dump(spotify_data, f)
        else:
            print('Callback error: ' + str(user_data.status_code))
        return redirect(myurl)

# checks if token needs to be refreshed and does so, if not just returns access token
def getToken(session):
    access_token = ''
    # If not logged in
    if not session.get('spotify_data'):
        access_token = getDefaultToken()
    # If logged in
    else:
        access_token = session['spotify_data']['access_token']
        # If expired, fetch refreshed token
        if session['spotify_data']['expires_at'] < int(time.time()):
            user_data = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type': 'refresh_token', 'refresh_token': session['spotify_data']['refresh_token'], 'client_id': client_id})
            #if everything good reupdate session data
            if user_data.status_code == 200:
                session['spotify_data'] = user_data.json()
                session['spotify_data']['expires_at'] = int(time.time()) + session['spotify_data']['expires_in']
                access_token = session['spotify_data']['access_token']
            else:
                print('getToken error: ' + str(user_data.status_code))
    return access_token

# run server
if __name__ == "__main__":
    socketio.run(app)