from flask import Flask, render_template, session, request
from flask_socketio import SocketIO
import spotipy.oauth2 as oauth2
from flask_session import Session
import spotipy
import classes
import random
from datetime import datetime
import requests

# making a flask socket object
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config[
    "SECRET_KEY"
] = "z\xe4\xdc\xc4)\xf1\xad\x8dF\x07EVv8k\x14\xda\xd8\xd0\x8a\xc4\xbc\xaew\x98\xf1\x0f\xfa\x01\x90"
socketio = SocketIO(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = True
# session stuff
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# list of room codes
active_rooms = []
# list of gamestates
gamestates = [None] * 9000


@app.route("/test/", methods=["GET", "POST"])
def hello_world():
    return render_template("chat.html")


myurl = "http://127.0.0.1:5000/"

# auth stuff
SPOTIPY_CLIENT_ID = "f50f20e747fb4bda8d9352696004cda4"
SPOTIPY_CLIENT_SECRET = "8adcb482dbf04ddbb261b7740309325e"
SPOTIPY_REDIRECT_URI = myurl + "spotify-login/"
SCOPE = "user-library-read"
sp_oauth = oauth2.SpotifyOAuth(
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE
)
API_BASE = 'https://accounts.spotify.com'




# main page
@app.route("/")
def main():
    session["unique"] = datetime.now().time()
    if session.get("token") == None:
        return render_template("mainmenu_default.html")
    else:
        return render_template("mainmenu_spotify.html")


# spotify login
@app.route("/spotify-login/")
def authentication():
    # if already logged in redirect to main menu
    if session.get("token"):
        print("Access token available! Trying to get user information...")
        return render_template("Logged_in.html")

    # if not check for callback and add to cookies
    else:
        code = request.args.get("code")
        auth_token_url = f"{API_BASE}/api/token"
        res = requests.post(auth_token_url, data={
            "grant_type":"authorization_code",
            "code":code,
            "redirect_uri":SPOTIPY_REDIRECT_URI,
            "client_id":SPOTIPY_CLIENT_ID,
            "client_secret":SPOTIPY_CLIENT_SECRET
            })
        res_body = res.json()
        session['token'] = res_body.get("access_token")
    return render_template("spotify.html")


# redirect on spotify login
@socketio.on("spotifylogin")
def login():
    socketio.emit("spotifyloginrequest", sp_oauth.get_authorize_url())


# when make_room_button is pressed on main page create a room and add this user to the room
@socketio.on("make_room")
def makeRoom(data):
    # defaults playlist_id
    playlist_id = data["playlist"]
    print(playlist_id)
    user = classes.User(
        username=data.get("username"),
        unique=session.get("unique"),
        spotify_acc=session.get("token"),
    )
    room = random.randint(1000, 9999)
    if len(active_rooms) == 9000:
        pass
        # print(socketio.emit('server_full'))
    else:
        # find an availible room code
        while room in active_rooms:
            room = random.randint(1000, 9999)
        active_rooms.append(room)
        # create a gamestate in list of gamestates at index = room number
        gamestates[room - 1000] = classes.GameState(
            room_number=room, password=data.get("password")
        )
        gamestates[room - 1000].allow(session["unique"])
        gamestates[room - 1000].addUser(user)
        # redirect to the game room
        socketio.emit("room_made", myurl + f"game/{room}")


@socketio.on("join_room")
def joinRoom(data):
    user = classes.User(
        username=data.get("username"),
        unique=session.get("unique"),
        spotify_acc=session.get("token"),
    )
    room = int(data["roomcode"])
    password = data["password"]
    # if room is active
    if room not in active_rooms:
        socketio.emit("Room_noexist")
    # check if too many people
    elif len(gamestates[room - 1000].users) > gamestates[room - 1000].max_users:
        socketio.emit("Room_full")
    # checking no password case
    elif not gamestates[room - 1000].password:
        gamestates[room - 1000].allow(session["unique"])
        gamestates[room - 1000].addUser(user)
        socketio.emit("password_correct", myurl + f"game/{room}")
    # checking is password correct then redirecting to the room
    elif (
        gamestates[room - 1000].password
        and gamestates[room - 1000].password == password
    ):
        gamestates[room - 1000].allow(session["unique"])
        gamestates[room - 1000].addUser(user)
        socketio.emit("password_correct", myurl + f"game/{room}")
    # saying wrong password
    else:
        socketio.emit("wrong_pass")


@socketio.on("connected_to_main")
def updatePlaylists():
    # If access to spotify granted
    if session.get("token"):
        print('hi')
        print(session.get("token"))
        sp = spotipy.Spotify(auth=session.get("token"))
        print(sp.current_user())


@socketio.on("logout_spotify")
def logout():
    session.pop("key")


@app.route("/game/<int:room>/")
def runGame(room):
    # If gamestate doesn't exist or user is not whitelisted, entry for private/public only allowed through main
    if (
        not gamestates[room - 1000]
        or session.get("unique") not in gamestates[room - 1000].allowed
    ):
        return render_template("backtomain.html")
    else:
        return render_template("game.html")


@socketio.on("connected_to_room")
def getplayers(data):
    room = int(data["url"][27:31])
    string = ""
    for user in gamestates[room - 1000].users:
        string += user.username + "  "
    print(string, gamestates[room - 1000].users)
    socketio.emit("display_players", string)


# on disconnect from game removes user
@socketio.on("disconnect")
def disconnect():
    pass


# run server
if __name__ == "__main__":
    socketio.run(app)