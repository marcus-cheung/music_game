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
import time
import pafy
from youtubesearchpython import VideosSearch
import os
import shutil
import urllib
import base64
import re
from hashlib import sha256
from string import ascii_letters, digits
from spotify_handler import *

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
state = ''.join(random.choice(ascii_letters + digits + '_.-~') for i in range(128))
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
        playlist_infos = getPlaylists(getToken(session))
        for playlist in playlist_infos:
            data = {}
            playlist_id = playlist["id"]
            name = playlist["name"]
            data["label"] = f'<label for="{name}">{name}</label><br>'
            data[
                "checkbox"
            ] = f'<input type="checkbox" id="{name}" name="checkbox" value="{playlist_id}">'
            socketio.emit("add_playlist", data, room=request.sid)


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
            print('Callback error: ' + str(user_data.status_code))
        return redirect(myurl)

# when make_room_button is pressed on main page create a room and add this user to the room
@socketio.on("make_room")
def makeRoom(data):
    #making user to later add to gamestate
    user = classes.User(username = data['username'],
        unique=session.get("unique"),
    )
    allsongs = getPlaylistSongs(data['playlists'], getToken(session))
    # choose random from allsongs
    song_infos = song_selector(allsongs, int(data['rounds']))
    if song_infos == []:
        socketio.emit('invalid_rounds', room=request.sid)
    else:
        #Gets free room number
        room = random.randint(1000, 9999)
        while room in active_rooms:
            room = random.randint(1000, 9999)
        active_rooms.append(room)
        # create a gamestate in list of gamestates at index = room number
        gamestates[room - 1000] = classes.GameState(
            song_infos = song_infos, host = session['unique'], gamemode = data['gamemode'], rounds = int(data['rounds']), users = [], room_number=room, password=data.get("password"), playlists = data['playlists']
        )
        makeDir(room)
        # Add songs to directory
        song_counter = 1
        for song in song_infos:
            song_name = song['name']
            song_artist = song['artists'][0]['name']
            print('Test:'+song_name)
            print(song_artist)
            download_music_file(song_name + ' ' + song_artist, room, song_name)
            song_counter += 1
        #Whitelisting user
        gamestates[room - 1000].allow(session["unique"])
        gamestates[room - 1000].addUser(user)
        # redirect to the game room
        socketio.emit("room_made", myurl + f"game/{room}",room=request.sid)





# checks if token needs to be refreshed and does so, if not just returns access token
def getToken(session):
    # If expired, fetch refreshed token
    if session['spotify_data']['expires_at'] < int(time.time()):
        user_data = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type': 'refresh_token', 'refresh_token': session['spotify_data']['refresh_token'], 'client_id': client_id})
        if user_data.status_code == 200:
            session['spotify_data'] = user_data.json()
            session['spotify_data']['expires_at'] = int(time.time()) + session['spotify_data']['expires_in']
        else:
            print('get token error: ' + str(user_data.status_code))
    return session['spotify_data']['access_token']


def song_selector(allsongs, rounds):
    song_infos = []
    if len(allsongs) == 0:
        return []
    for i in range(rounds):
        x = random.randint(0,len(allsongs) - 1)
        #Check if song already in list of songs
        while allsongs[x]['track'] in song_infos:
            #remove duplicate song
            allsongs.pop(x)
            # Breaks loop if allsongs empty
            if len(allsongs) == 0:
                return []
            #generates new index to check
            x = random.randint(0,len(allsongs) - 1)
        #Appends valid song to song_infos
        song_infos.append(allsongs.pop(x)['track'])
    return song_infos




def getGame(room):
    return gamestates[int(room) - 1000]

def makeDir(room):
    directory =  'static/music' + '/' + str(room)
    #checks if directory exists
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

def download_music_file(query, roomnumber, filename, filetype='m4a', bitrate='48k', lyric=True):
    destination = 'static/music/' + str(roomnumber)
    path = destination + '/' + filename + '.' + filetype
    if lyric:
        query += ' lyric'
    top_result = VideosSearch(query, limit=1).result()['result'][0]
    url = top_result['link']
    print(url)
    video = pafy.new(url)
    audiostreams = video.audiostreams
    filetype_audiostreams = []
    final_file = None
    for audiostream in audiostreams:
        # print(audiostream)
        # print(audiostream.bitrate)
        if audiostream.extension == filetype:
            filetype_audiostreams.append(audiostream)
    for audiostream in filetype_audiostreams:
        # print(audiostream)
        if audiostream.bitrate==bitrate:
            final_file = audiostream
        else:
            final_file = filetype_audiostreams[len(filetype_audiostreams) - 1]
    # Overwrite existing file if it exists
    if os.path.isfile(path):
        os.remove(path)
    final_file.download(path, quiet=True)

if __name__ == "__main__":
    socketio.run(app)