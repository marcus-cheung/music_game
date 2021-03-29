from random import randint


class GameState:
    max_users = 8

    def __init__(
        self, room_number, rounds, roundlength=90, playlists=[], password=None
    ):
        #On call
        self.room_number = room_number
        self.rounds = rounds
        self.roundlength = roundlength
        self.playlists = playlists
        self.password = password
        #Mutated when making/joining room
        self.users = []
        self.allowed = []
        self.song = []

    def allow(self, unique):
        self.allowed.append(unique)

    # called when someone connects to a /game
    def addUser(self, user):
        self.users.append(user)

    def kickUser(self, user):
        self.users.remove(user)


class guessArtist(GameState):
    def __init__(self):
        super().__init__(self, room_number, playlists=[], password=None)


class User:
    score = 0

    def __init__(self, unique, username):
        if username == "":
            self.username = "Guest" + str(randint(10000, 99999))
        else:
            self.username = username
        self.unique = unique
