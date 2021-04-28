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
socketio = SocketIO(app, always_connect=True, manage_session=False)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = False
# session stuff
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# list of room codes
active_rooms = []
# list of gamestates
gamestates = [None] * 9000

myurl = "https://knewsic.herokuapp.com/"

# auth stuff chr
client_id = "f50f20e747fb4bda8d9352696004cda4"
client_secret = "8adcb482dbf04ddbb261b7740309325e"
redirect_uri = myurl + "spotify-login/callback/"
default_redirect_uri = myurl + "super-secret-default-spotify/callback/"
state = "".join(random.choice(ascii_letters + digits + "_.-~") for i in range(47, 128))


# main page
@app.route("/")
def main():
    return render_template("main_menu.html")


@app.route("/make-room/")
def makeRoom():
    print(session)
    return render_template("make_room.html")


@app.route("/join-room/")
def joinRoom():
    return render_template("join_room.html")


@socketio.on("connect")
def connect():
    if not session.get("unique"):
        session["unique"] = (
            "".join(random.choice(ascii_letters + digits + "_.-~") for i in range(128)),
            time.time()
        )


# If user logged into spotify adds playlists as options
@socketio.on("connected_to_make_room")
def setupMain():
    # If no access to spotify adds spotify log in button
    if not session.get("spotify_data"):
        # adds spotify log in button
        socketio.emit("add_spotify_button", room=request.sid)
    playlist_infos = getPlaylists(getToken(session))
    playlist_buttons = [f"<button class='playlist' id='p{playlist['id']}' value='{playlist['id']}' onclick='add_playlist({playlist['id']},{playlist['name']})'>{playlist['name']}</button>" for playlist in playlist_infos]
    socketio.emit("add_playlist", playlist_buttons, room=request.sid)


# spotify login
@app.route("/spotify-login/")
def spotify_login():
    # Code challenge/verifier generation
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
    session["code_verifier"] = code_verifier
    code_challenge = sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")
    # Constructing body
    scopes = "playlist-read-private playlist-read-collaborative user-read-private"
    query_data = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
        "scope": scopes,
        "state": state,
    }
    query = urllib.parse.urlencode(query_data)
    auth_redirect = "https://accounts.spotify.com/authorize?" + query
    return redirect(auth_redirect)


# After authorization saves token_info to cookies and redirects to main
@app.route("/spotify-login/callback/")
def authentication():
    callback_state = request.args.get("state")
    if state != callback_state:
        # abort
        print("Callback state does not match")
        return redirect(myurl)
    else:
        auth_code = request.args.get("code")
        # post request
        user_data = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "client_id": client_id,
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri,
                "code_verifier": session["code_verifier"],
            },
        )
        if user_data.status_code == 200:
            session["spotify_data"] = user_data.json()
            session["spotify_data"]["expires_at"] = (
                int(time.time()) + session["spotify_data"]["expires_in"]
            )
        else:
            print("Callback error: " + str(user_data.status_code))
        return redirect(myurl + "/make-room/")


@socketio.on("create_user")
def createUser(username):
    print(username)
    user = classes.User(username=username, unique=session.get("unique"))
    session["user_object"] = user
    session["test"] = "this passed"
    print(session)
    print(session["user_object"])
    print("User created: " + user.username)


# when make_room_button is pressed on main page create a room and add this user to the room
@socketio.on("make_room")
def makeRoom(data):
    # Gets free room number
    room = random.randint(1000, 9999)
    while room in active_rooms:
        room = random.randint(1000, 9999)
    socketio.emit("room_loading", room)
    allsongs = getPlaylistSongs(data["playlists"], getToken(session))
    # choose random from allsongs
    song_infos = song_selector(allsongs, int(data["rounds"]))
    print(song_infos)
    if song_infos == []:
        socketio.emit("invalid_rounds", room=request.sid)
    else:
        active_rooms.append(room)
        # create a gamestate in list of gamestates at index = room number
        gamestates[room - 1000] = classes.GameState(
            song_infos=song_infos,
            host=session["unique"],
            gamemode=data["gamemode"],
            rounds=int(data["rounds"]),
            users=[],
            room_number=room,
            password=data.get("password"),
            playlists=data["playlists"],
        )
        makeDir(room)
        # Add songs to directory
        download_songs(room, song_infos)
        # redirect to the game room
        socketio.emit("room_made", myurl + f"game/{room}", room=request.sid)

