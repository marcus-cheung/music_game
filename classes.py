class GameState():
    rounds = 0
    def __init__(self, room_number, playlist_id = 'spotify:playlist:6UeSakyzhiEt4NB3UAd6NQ', password=None):
        self.users = []
        self.allowed = []
        self.password = password
        self.playlist_id = playlist_id
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
    def __init__(self, username, unique, spotify_acc=None):
        self.username = username
        self.spotify_acc = spotify_acc
        self.unique = unique
    def returnElements(self):
        return {'score': self.score, 'spotify_acc': self.spotify_acc, 'username':self.username}
