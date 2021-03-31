from random import randint
import spotipy
class GameState:
    max_users = 8

    def __init__(
        self, room_number, gamemode, song_infos, roundlength=90, password=None
    ):
        #On call
        self.room_number = room_number
        # Either song, artist, or year
        self.gamemode = gamemode
        # Duration of each round
        self.roundlength = roundlength
        self.password = password
        # List of song_infos passed from spotipy when 'make room'
        self.song_infos = song_infos
        #Used each round
        self.correct = []
        self.current_round = 1
        #Mutated when making/joining room
        self.users = []
        self.allowed = []
        self.answers = []
        #get the answers
        for song_info in self.song_infos:
            if self.gamemode == 'song':
                self.answers.append(song_info['name'].lower())
            if self.gamemode == 'year':
                release_date = song_info['album']['release_date']
                year = release_date[0:4]
                self.answers.append(year)
            if self.gamemode == 'artist':
                self.answers.append(song_info['artists'][0]['name'].lower())
        
        
    def allow(self, unique):
        self.allowed.append(unique)

    # called when someone connects to a /game
    def addUser(self, user):
        self.users.append(user)

    def kickUser(self, user):
        self.users.remove(user)

    def getscoreDATA(self):
        return [{'username': user.username, 'score': user.score+}
        for user in self.correct:
            gain = 100-self.correct.index*5
            



    def endRound(self):
        for user in self.users:
            user.score += round_score(user)
        if self.current_round == len(self.songs):
            self.endGame()
        self.current_round+=1
        self.correct = []
    
    def endGame(self):
        # TODO
        pass
        


class User:
    score = 0
    def __init__(self, unique, username):
        if username == "":
            self.username = "Guest" + str(randint(10000, 99999))
        else:
            self.username = username
        self.unique = unique
        self.already_answered = False
        self.score