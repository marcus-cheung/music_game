from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import json

app = Flask(__name__, static_folder="static", static_url_path="/static")

app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)


@app.route('/', methods=['GET', 'POST'])
def sessions():
    return render_template('test.html')


@socketio.on('connect')
def connect():
    print('\n \n \n Someone has connected \n \n \n')


@socketio.on('incoming_msg')
def incoming_msg(data):
    print('\n \n \n Message Received \n \n')
    socketio.emit('message', data)

if __name__ == '__main__':
    socketio.run(app, debug=True)
    print('server launched')