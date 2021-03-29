from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO
import spotipy.oauth2 as oauth2
from flask_session import Session
import spotipy
import classes
import random
from datetime import datetime
import requests
import time
import json
import pafy
from youtubesearchpython import VideosSearch
import os
import shutil

# making a flask socket object
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config[
    "SECRET_KEY"
] = "z\xe4\xdc\xc4)\xf1\xad\x8dF\x07EVv8k\x14\xda\xd8\xd0\x8a\xc4\xbc\xaew\x98\xf1\x0f\xfa\x01\x90"
socketio = SocketIO(app)
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


# auth stuff
SPOTIPY_CLIENT_ID = "f50f20e747fb4bda8d9352696004cda4"
SPOTIPY_CLIENT_SECRET = "8adcb482dbf04ddbb261b7740309325e"
SPOTIPY_REDIRECT_URI = myurl + "spotify-login/callback"
SCOPE = "user-library-read"
API_BASE = "https://accounts.spotify.com"


# main page
@app.route("/")
def main():
    session["unique"] = datetime.now().time()
    return render_template("mainmenu.html")


# If user logged into spotify adds playlists as options
@socketio.on("connected_to_main")
def setupMain():
    # If no access to spotify adds spotify log in button
    if not session.get("token_info"):
        # adds spotify log in button
        socketio.emit("add_spotify_button")
    # if has access shows playlists
    else:
        # refreshes token:
        session["token_info"], authorized = get_token(session)
        # show personal playlists
        session.modified = True
        if not authorized:
            print("notauthorized")
        data = request.form
        sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))
        playlists_info = sp.current_user_playlists()
        socketio.emit("add_playlist", "data")
        for playlist in playlists_info["items"]:
            dct = {}
            playlist_id = "spotify:playlist:" + playlist["id"]
            name = playlist["name"]
            dct["label"] = f'<label for="{name}">{name}</label><br>'
            dct[
                "checkbox"
            ] = f'<input type="checkbox" id="{name}" name="checkbox" value="{playlist_id}">'
            socketio.emit("add_playlist", dct)


# spotify login
@app.route("/spotify-login/")
def spotify_login():
    # if already logged in redirect to main menu, checks if token info exists
    if session.get("token_info"):
        print("Access token available! Trying to get user information...")
        return redirect(myurl)
    # if not logged in redirect to spotify api authorisation
    else:
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE,
        )
        return redirect(sp_oauth.get_authorize_url())


# After authorization saves token_info to cookies and redirects to main
@app.route("/spotify-login/callback/")
def authentication():
    code = request.args.get("code")
    sp_oauth = oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
    )
    token_info = sp_oauth.get_access_token(code)
    # Saving the access token along with all other token related info
    session["token_info"] = token_info
    return redirect(myurl)


# Checks valid token, if not valid refreshes and returns new token
def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})
    # Checking if the session already has a token stored
    if not (session.get("token_info", False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get("token_info").get("expires_at") - now < 60

    # Refreshing token if it has expired
    if is_token_expired:
        # Don't reuse a SpotifyOAuth object because they store token info
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE,
        )
        token_info = sp_oauth.refresh_access_token(
            session.get("token_info").get("refresh_token")
        )

    token_valid = True
    return token_info, token_valid


# when make_room_button is pressed on main page create a room and add this user to the room
@socketio.on("make_room")
def makeRoom(data):
    #making user to later add to gamestate
    user = classes.User(
        username=data.get("username"),
        unique=session.get("unique"),
    )
    #choosing songs
    sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))
    allsongs = []
    songs = []
    #make list of allsongs
    for playlist in data['playlists']:
        results = sp.user_playlist_tracks(sp.current_user()['display_name'],playlist)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        allsongs.extend(tracks)
    if len(allsongs) < int(data['rounds']):
        socketio.emit('invalid_rounds')
    else:
        # choose random from allsongs
        for i in range(int(data['rounds'])):
            x = random.randint(0,len(allsongs) - 1)
            songs.append(allsongs.pop(x)['track'])
        room = random.randint(1000, 9999)
        while room in active_rooms:
            room = random.randint(1000, 9999)
        active_rooms.append(room)
        # create a gamestate in list of gamestates at index = room number
        gamestates[room - 1000] = classes.GameState(
            songs = songs, gamemode = data['gamemode'], room_number=room, password=data.get("password")
        )   
        makeDir(room)
        # Add songs to directory
        song_counter = 1
        for song in songs:
            song_name = song['name']
            song_artists = song['artists'][0]['name']
            print(song_name)
            print(song_artists)
            #download_music_file(song_name + ' ' + song_artists, room, str(song_counter))
            song_counter += 1
        #Whitelisting user
        gamestates[room - 1000].allow(session["unique"])
        gamestates[room - 1000].addUser(user)
        # redirect to the game room
        socketio.emit("room_made", myurl + f"game/{room}")

def makeDir(room):
    directory =  'static/music' + '/' + str(room)
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

# when join room pressed
@socketio.on("join_room")
def joinRoom(data):
    user = classes.User(
        username=data.get("username"),
        unique=session.get("unique"),
    )
    password = data["password"]
    if data["roomcode"] != "":
        room = int(data["roomcode"])
        # if room is active
        if room not in active_rooms:
            socketio.emit("Room_noexist")
        # check if too many people
        elif len(gamestates[room - 1000].users) > gamestates[room - 1000].max_users:
            socketio.emit("Room_full")
        # checking no password case
        elif gamestates[room - 1000].password == "":
            gamestates[room - 1000].allow(session["unique"])
            gamestates[room - 1000].addUser(user)
            socketio.emit("password_correct", myurl + f"game/{room}")
        # checking is password correct then redirecting to the room
        elif gamestates[room - 1000].password == password:
            gamestates[room - 1000].allow(session["unique"])
            gamestates[room - 1000].addUser(user)
            socketio.emit("password_correct", myurl + f"game/{room}")
        # saying wrong password
        else:
            socketio.emit("wrong_pass")


@socketio.on("logout_spotify")
def logout():
    session.pop("token_info")


@app.route("/game/<int:room>/")
def runGame(room):
    # If gamestate doesn't exist or user is not whitelisted, entry for private/public only allowed through main
    if (
        not gamestates[room - 1000]
        or session.get("unique") not in gamestates[room - 1000].allowed
    ):
        return redirect(myurl)
    else:
        return render_template("game.html")


@socketio.on("connected_to_room")
def getplayers(data):
    room = int(data["url"][27:31])
    if gamestates[room - 1000]:
        string = ""
        for user in gamestates[room - 1000].users:
            string += user.username + "  "
        socketio.emit("display_players", string)



# on disconnect from game removes user
@socketio.on("disconnect_game")
def disconnect():
    print('disconnect')
    room = int(data["url"][27:31])
    directory =  'static/music' + '/' + str(room)
    if os.path.isdir(directory):
        shutil.rmtree(directory)

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
        print(audiostream)
        print(audiostream.bitrate)
        if audiostream.extension == filetype:
            filetype_audiostreams.append(audiostream)
    for audiostream in filetype_audiostreams:
        print(audiostream)
        if audiostream.bitrate==bitrate:
            final_file = audiostream
        else:
            final_file = filetype_audiostreams[len(filetype_audiostreams) - 1]
    # if os.path.isdir(destination):
    #     print('Error: Directory does not exist')
    print(final_file)
    # Overwrite existing file if it exists
    if os.path.isfile(path):
        os.remove(path)
    final_file.download(path)

# run server
if __name__ == "__main__":
    socketio.run(app)