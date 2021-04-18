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


myurl = "https://knewsic.herokuapp.com/"

# auth stuff chr
client_id = "f50f20e747fb4bda8d9352696004cda4"
client_secret = "8adcb482dbf04ddbb261b7740309325e"
redirect_uri = myurl + 'spotify-login/callback/'
default_redirect_uri = myurl + 'super-secret-default-spotify/callback/'
state = ''.join(random.choice(ascii_letters + digits + '_.-~') for i in range(47, 128))




# main page
@app.route("/")
def main():
    if not session.get('unique'):
        session["unique"] = (''.join(random.choice(ascii_letters + digits + '_.-~') for i in range(128)), time.time())
    return render_template("mainmenu.html")

# If user logged into spotify adds playlists as options
@socketio.on("connected_to_main")
def setupMain():
    # If no access to spotify adds spotify log in button
    if not session.get("spotify_data"):
        # adds spotify log in button
        socketio.emit("add_spotify_button",room=request.sid)
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
    scopes = 'playlist-read-private playlist-read-collaborative user-read-private'
    query_data = {'client_id':client_id, 'response_type':'code', 'redirect_uri':redirect_uri, 'code_challenge_method':'S256', 'code_challenge':code_challenge,'scope':scopes,'state':state}
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
    print(song_infos)
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
        download_songs(room, song_infos)
        # Whitelisting user
        getGame(room).allow(session["unique"])
        getGame(room).addUser(user)
        # redirect to the game room
        socketio.emit("room_made", myurl + f"game/{room}",room=request.sid)

@socketio.on('search')
def sendResults(data):
    print(data)
    if data!='':
        socketio.emit('artist_results', getArtistSearch(data), room = request.sid)

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
            socketio.emit("Room_no_exist",room=request.sid)
        # check if too many people
        elif len(gamestates[room - 1000].users) > gamestates[room - 1000].max_users:
            socketio.emit("Room_full",room=request.sid)
        # checking no password case
        elif gamestates[room - 1000].password == "":
            gamestates[room - 1000].allow(session["unique"])
            gamestates[room - 1000].addUser(user)
            socketio.emit("password_correct", myurl + f"game/{room}",room=request.sid)
        # checking is password correct then redirecting to the room
        elif gamestates[room - 1000].password == password:
            gamestates[room - 1000].allow(session["unique"])
            gamestates[room - 1000].addUser(user)
            socketio.emit("password_correct", myurl + f"game/{room}",room=request.sid)
        # saying wrong password
        else:
            socketio.emit("wrong_pass",room=request.sid)


@socketio.on("logout_spotify")
def logout():
    session.pop("token_info")


@app.route("/game/<int:room>/")
def runGame(room):
    # If gamestate doesn't exist or user is not whitelisted, entry for private/public only allowed through main
    if (
        not getGame(room)
        or session.get("unique") not in getGame(room).allowed
    ):
        return redirect(myurl)
    else:
        session['room'] = room
        return render_template("game.html", myurl=myurl)


#What happens on game connect: Prints user joined, if host add start button
@socketio.on("connected_to_room")
def gameConnect(room):
    gamestate = getGame(room)
    if gamestate and getUser(gamestate) in gamestate.inactive_users:
        gamestate.reconnect(getUser(gamestate))
        join_room('correct' + str(room))
        socketio.emit('uptodate',gamestate.current_round, room = request.sid)
        # Add a message to client that tells to wait for one round
    join_room(room)
    #Print user
    user = getUser(gamestate)
    socketio.emit('user_joined', user.username, room=room)

    #if is host set as host
    if gamestate and gamestate.host and session['unique'] == gamestate.host and not gamestate.game_started:
        gamestate.host_reqID = request.sid
        socketio.emit('host', room=request.sid)
        
    # Send all the song file names
    socketio.emit('send_song_paths', [myurl + 'static/music/' + str(room) + '/' + super_sanitize(song['name']) + '.m4a' for song in gamestate.song_infos], room=request.sid)

# Sends chat messages to everyone in room
@socketio.on('message_send')
def onMSG(data):
    room = int(data['room'])
    gamestate = gamestates[room - 1000]
    user = getUser(gamestate)
    username = user.username
    print(username)
    # If already answered
    if user.already_answered:
        print('already answered')
        socketio.emit('chat', {'username': username, 'msg': data['msg'], 'correct': True}, room='correct' + str(room))
    # If haven't answered
    else:
        # if round started and correct answer
        if gamestate.round_start and gamestate.checkAnswer(data['msg']):
            # Add user to dictionary of correct answerers
            gamestate.correct[user] = int(time.time())
            join_room('correct' + str(room))
            socketio.emit('chat', {'username': username, 'msg': f'{user.username} has answered correctly!', 'correct': 'first'}, room=str(room))
            user.already_answered = True
            # check if round should be ended
            if len(gamestate.users) == len(gamestate.correct):
                print('round end')
                # check if game will end
                print(gamestate.current_round,len(gamestate.song_infos))
                if gamestate.current_round == len(gamestate.song_infos):
                    print('game end')
                    end_game(str(room))
                else:
                    end_round(str(room))    
        # If round hasn't started or wrong answer
        else:
            socketio.emit('chat', {'username': username, 'msg': data['msg'], 'correct': False}, room=data['room'])

def start_round(room):
    # Make it possible to get correct answer
    gamestate = getGame(room)
    gamestate.round_start_time = int(time.time())
    gamestate.round_start = True
    current_round = gamestate.current_round
    socketio.emit('start_round', room=room)
    # if its not the last round
    if not gamestate.current_round==gamestate.rounds:
        # Starts a timer for the room
        time.sleep(gamestate.roundlength)
        # Calls end_round provided that the round has not incremented from everyone answering correctly
        if gamestate.current_round == current_round:
            end_round(room)

def end_round(room):
    gamestate = getGame(room)

    # Disable getting correct answer
    gamestate.round_start=False

    # Get list of user/scoretotal/gain from that round ordered
    scores = gamestate.getScoreDATA()
    socketio.emit('update_scores', scores, room=room)

    # Emit correct answer
    answer_dict = gamestate.getAnswer()
    answer = f"The song was {answer_dict['song']} by {answer_dict['artist']} ({answer_dict['year']})."
    socketio.emit('correct_answer', answer, room = room)

    # Get song info to be displayed
    song_info = gamestate.getAnswer()

    # Save the current round before it changes in endRound()
    checker = not gamestate.current_round == len(gamestate.song_infos)
    # Ends the round on server-side, also returns answer
    gamestate.endRound()

    # Closes the room of correct answerers
    close_room('correct' + str(room))

    # if game not ended, Wait five seconds and then start round,
    if checker:
        # Emits event to clients to end round
        socketio.emit('end_round', {'scores':scores, 'song_info':song_info}, room=room)
        time.sleep(2)
        start_round(room)
    

@socketio.on('start_game')
def start_game(room):
    # TODO: Error-checking: make sure that answers and songs all have enough elements
    # TODO: Some front-end start-up messages
    getGame(room).game_started = True
    start_round(room)
    


@socketio.on('new_game_clicked')
def new_game(room):
    print('starting new game')
    old_gamestate = getGame(room)
    old_users = old_gamestate.users
    old_pass = old_gamestate.password
    old_host = old_gamestate.host
    old_gamemode = old_gamestate.gamemode
    old_playlists = old_gamestate.playlists
    old_rounds = old_gamestate.rounds

    allsongs = getPlaylistSongs(old_playlists, getToken(session))

    # choose random from allsongs
    song_infos = song_selector(allsongs, old_rounds)

    # create a gamestate in list of gamestates at index = room number
    gamestates[int(room) - 1000] = classes.GameState(
        song_infos = song_infos, host = old_host, gamemode = old_gamemode, users = old_users, room_number=room, password=old_pass, rounds = old_rounds, playlists = old_playlists
    )
    makeDir(room)
    # Add songs to directory
    download_songs(room,song_infos)
    # Preload on everyone's client
    song_paths = [myurl+'static/music/'+ str(room) + '/' + super_sanitize(song['name'])+'.m4a' for song in song_infos]
    # Now everything ready, start round client side
    socketio.emit('start_new', song_paths, room = room)
    socketio.emit('host', room = request.sid)

@socketio.on('skip')
def skip(room):
    gamestate = getGame(room)
    user = getUser(gamestate)
    if user not in gamestate.voted_skip:
        gamestate.vote_skip.append(user)
        votes = len(gamestate.voted_skip)
        message_string = f'{user.username} has voted to skip the round. ({votes}/{len(gamestate.users)}).'
        socketio.emit('vote_skip', message_string, room=room)
        if votes == len(gamestate.users):
            socketio('skip_round', room = room)
            end_round(room)



@socketio.on('disconnect')
def disconnect():
    # On disconnection from a gameroom
    if session.get('room'):
        room = session['room']
        gamestate = getGame(room)
        user = getUser(gamestate)
        gamestate.inactive(user)
        socketio.emit('user_disconnect', user.username, room=room)
        session['room'] = None

@socketio.on('downloaded')
def downloaded(room):
    gamestate = getGame(room)
    gamestate.downloaded += 1
    if gamestate.downloaded == len(gamestate.users):
        socketio.emit('all_downloaded', room = gamestate.host_reqID)

def end_game(room):
    gamestate = getGame(room)
    scores = gamestate.getScoreDATA()
    song_info = gamestate.getAnswer()
    # Opens end modal for all users
    socketio.emit('end_game', {'scores':scores,'song_info':song_info}, room=room)
    gamestate.endRound()
    # Adds start new button for host
    socketio.emit('host_end', room = gamestate.host_reqID)
    # Wipes directory
    directory =  'static/music/' + room
    shutil.rmtree(directory)
    # Close correct socketio rooms
    close_room('correct' + str(room))

# gets userobject based of unique
def getUser(gamestate):
    users = gamestate.users + gamestate.inactive_users + gamestate.waiting_room
    list_unique = [user.unique for user in users]
    index = list_unique.index(session['unique'])
    user = users[index]
    return user

# Called on end of game or if room is empty
def closeRooms(room):
    close_room(room)
    close_room('correct' + str(room))

def getGame(room):
    return gamestates[int(room) - 1000]


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