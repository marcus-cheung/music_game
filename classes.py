from random import randint
from methods import *

class GameState:
    max_users = 8

    def __init__(
        self, room_number, gamemode, song_infos, rounds, host, playlists, users, roundlength=90, password=None
    ):
        #On call
        self.room_number = room_number
        self.downloaded = 0
        self.ready_start = False
        self.rounds = rounds
        # Either song, artist, or year
        self.gamemode = gamemode
        # Duration of each round
        self.roundlength = roundlength
        self.password = password
        # Host
        self.host = host
        self.host_reqID = None
        # List of song_infos passed from spotipy when 'make room'
        self.song_infos = song_infos
        self.playlists = playlists
        # Used each round
        self.correct = []
        self.current_round = 1
        self.round_start = False
        # Mutated when making/joining room
        self.game_started = False
        self.users = users
        self.inactive_users = []
        self.waiting_room = []
        self.allowed = []
        self.answers = []
        self.sockets = []
        self.game_ended = False
        # Get the answers
        for song_info in self.song_infos:
            if self.gamemode == 'song':
                self.answers.append(answer_variations(song_info['name']))
            if self.gamemode == 'year':
                release_date = song_info['album']['release_date']
                year = release_date[0:4]
                self.answers.append([year])
            if self.gamemode == 'artist':
                self.answers.append([sanitize(song_info['artists'][0]['name'])])
        print('gamestate made')
        
        
    def allow(self, unique):
        self.allowed.append(unique)

    # called when someone connects to a /game
    def addUser(self, user):
        self.users.append(user)

    def kickUser(self, user):
        self.users.remove(user)

    def getScoreDATA(self):
        lst = []
        for user in self.users:
            if user in self.correct:
                gain = 100-self.correct.index(user)*5
            else:
                gain = 0
            user.score += gain
            lst.append({'username': user.username, 'score': user.score, 'gain': gain})
        return lst

    def endRound(self):
        for user in self.users:
            user.already_answered = False
        # Check if all rounds are up
        if self.current_round != len(self.song_infos):
            self.current_round+=1
            self.correct = []

    #must be called before endRound, returns dictionary of song info parsed
    def getAnswer(self):
        song_info = self.song_infos[self.current_round-1]
        return {'album_cover': song_info['album']['images'][0]['url'], 'song':song_info['name'], 'artist':song_info['artists'][0]['name'], 'year': song_info['album']['release_date'][0:4]}

    def checkAnswer(self, user_input):
        print('user_input')
        print(sanitize(user_input))
        print(self.answers[self.current_round-1])
        if sanitize(user_input) in self.answers[self.current_round-1]:
            print('Correct')
            return True
        else:
            return False

    def inactive(self, user):
        print('inactive called')
        self.users.remove(user)
        self.inactive_users.append(user)
        print(self.users, self.inactive_users)
        if self.users == []:
            pass
            # TODO: Implement ending of the game

    def reconnect(self, user):
        print('reconnecting user')
        self.inactive_users.remove(user)
        self.waiting_room.append(user)
        user.already_answered = True
        print(self.users, self.inactive_users)
    
    def clearWaiting(self):
        for user in self.waiting_room:
            self.waiting_room.remove(user)
            self.users.append(user)
        
        


class User:
    def __init__(self, unique, username):
        if username == "":
            self.username = "Guest" + str(randint(10000, 99999))
        else:
            self.username = username
        self.unique = unique
        self.already_answered = False
        self.score = 0



        
def remove_punc(s):
    new_string = ''
    for character in s:
        if character.isalnum():
            new_string += character
    return new_string