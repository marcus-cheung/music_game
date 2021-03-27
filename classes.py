from random import randint
class GameState():
    round = 0
    max_users = 8
    def __init__(self, room_number, playlists = [], password=None):
        self.playlists = playlists
        self.users = []
        self.allowed = []
        self.password = password
        self.room_number = room_number
        self.special = randint(100000,999999)

    def allow(self, unique):
        self.allowed.append(unique)

    # called when someone connects to a /game
    def addUser(self, user):
        self.users.append(user)

    def kickUser(self, user):
        self.users.remove(user)

class guessArtist(GameState):
    def __init__(self):
        super().__init__(self, room_number, playlists = [], password=None)



class User():
    score = 0
    def __init__(self, unique, username = None):
        if not username:
            self.username = 'Guest'+str(randint(10000,99999))
        else:
            self.username = username
        self.unique = unique
    def returnElements(self):
        return {'score': self.score, 'spotify_acc': self.spotify_acc, 'username':self.username}
