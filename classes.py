from random import randint
import spotipy
class GameState:
    max_users = 8

    def __init__(
        self, room_number, gamemode, songs, roundlength=90, password=None
    ):
        #On call
        self.room_number = room_number
        self.gamemode = gamemode
        self.roundlength = roundlength
        self.password = password
        self.song = songs
        #Mutated when making/joining room
        self.users = []
        self.allowed = []
    def allow(self, unique):
        self.allowed.append(unique)

    # called when someone connects to a /game
    def addUser(self, user):
        self.users.append(user)

    def kickUser(self, user):
        self.users.remove(user)
        


class User:
    score = 0

    def __init__(self, unique, username):
        if username == "":
            self.username = "Guest" + str(randint(10000, 99999))
        else:
            self.username = username
        self.unique = unique
