from random import randint
class GameState():
    round = 0
    max_users = 8
    def __init__(self, room_number, playlist_id = None, password=None):
        if playlist_id == None:
            self.playlist_id = 'spotify:playlist:6UeSakyzhiEt4NB3UAd6NQ'
        else:
            self.playlist_id = playlist_id
        self.users = []
        self.allowed = []
        self.password = password
        self.room_number = room_number

    def allow(self, unique):
        self.allowed.append(unique)

    # called when someone connects to a /game
    def addUser(self, user):
        self.users.append(user)

    def kickUser(self, user):
        self.users.remove(user)


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
