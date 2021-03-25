from flask import Flask, render_template, session, request
from flask_socketio import SocketIO
import spotipy.oauth2 as oauth2
from flask_session import Session
import spotipy
import classes
import random
from datetime import datetime

#making a flask socket object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
#session stuff
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#list of room codes
active_rooms = []
#list of gamestates
gamestates = [None]*9000

@app.route('/test/', methods = ['GET', 'POST'])
def hello_world():
    return render_template('chat.html')

myurl = 'http://127.0.0.1:5000/'

#auth stuff
SPOTIPY_CLIENT_ID = 'f50f20e747fb4bda8d9352696004cda4'
SPOTIPY_CLIENT_SECRET = '8adcb482dbf04ddbb261b7740309325e'
SPOTIPY_REDIRECT_URI = myurl+'spotify-login/'
SCOPE = 'user-library-read'
sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE)

#main page
@app.route('/')
def main():
    session['unique'] = datetime.now().time()
    if session.get('token')==None:
        return render_template('mainmenu_default.html')
    else:
        return render_template('mainmenu_spotify.html')

#spotify login
@app.route('/spotify-login/')
def authentication():
    # if already logged in redirect to main menu
    if session.get('token'):
        print("Access token available! Trying to get user information...")
        return render_template('Logged_in.html')

    # if not check for callback and add to cookies
    else:
        code = request.args.get('code')
        if code != None:
            print("Found Spotify auth code in Request URL!")
            session['token'] = code
    return render_template('spotify.html')

#redirect on spotify login
@socketio.on('spotifylogin')
def login():
    socketio.emit('spotifyloginrequest', sp_oauth.get_authorize_url())


# when make_room_button is pressed on main page create a room and add this user to the room
@socketio.on('make_room')
def makeRoom(data):
    user = classes.User(username = data.get('username'), unique = session.get('unique'), spotify_acc = session.get('token')) 
    room = random.randint(1000,9999)
    if len(active_rooms) == 9000:
        pass
        #print(socketio.emit('server_full'))
    else:
        # find an availible room code
        while room in active_rooms:
            room = random.randint(1000,9999)
        active_rooms.append(room)
        #create a gamestate in list of gamestates at index = room number
        gamestates[room-1000] = classes.GameState(room_number=room, password= data.get('password'))
        gamestates[room-1000].allow(session['unique'])
        gamestates[room-1000].addUser(user)
        #redirect to the game room
        socketio.emit('room_made', f'{myurl}game/{room}' )


@socketio.on('join_room')
def joinRoom(data):
    user = classes.User(username = data.get('username'), unique = session.get('unique'), spotify_acc = session.get('token')) 
    room = int(data['roomcode'])
    password = data['password']
    # if room is active
    if room not in active_rooms:
        socketio.emit('Room_noexist')
    #checking is password correct then redirecting to the room
    if gamestates[room-1000].password == password:
        gamestates[room-1000].allow(session['unique'])
        gamestates[room-1000].addUser(user)
        socketio.emit('password_correct', f'{myurl}game/{room}')
    #saying wrong password
    else:
        socketio.emit('wrong_pass')

@app.route('/game/<int:room>/')
def runGame(room):
    # If gamestate doesn't exist or user is not whitelisted
    if not gamestates[room-1000] or session.get('unique') not in gamestates[room-1000].allowed:
        return render_template('backtomain.html')
    else:
        return render_template('game.html')

@socketio.on('connected_to_room')
def getplayers(data):
    room = int(data['url'][27:31])
    string = ''
    for user in gamestates[room-1000].users:
        string += user.username + '  '
    print(string,gamestates[room-1000].users)
    socketio.emit('display_players', string)


#@socketio.on('disconnect')
def disconnect():
    pass


#run server
if __name__ == '__main__':
    socketio.run(app)