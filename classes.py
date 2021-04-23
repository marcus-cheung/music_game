from random import randint
from methods import *


class GameState:
    max_users = 8

    def __init__(
        self,
        room_number,
        gamemode,
        song_infos,
        rounds,
        host,
        playlists,
        users,
        roundlength=90,
        password=None,
    ):
        # On call
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
        self.round_start_time = 0
        self.current_round = 1
        self.round_start = False
        # Mutated when making/joining room
        self.game_started = False
        self.answers = []
        self.game_ended = False
        # User lists
        self.users = users
        # Get the answers
        for song_info in self.song_infos:
            if self.gamemode == "song":
                self.answers.append(answer_variations(song_info["name"]))
            if self.gamemode == "year":
                release_date = song_info["album"]["release_date"]
                year = release_date[0:4]
                self.answers.append([year])
            if self.gamemode == "artist":
                self.answers.append([sanitize(song_info["artists"][0]["name"])])

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
            if user.states['correct']:
                gain = self.score(user)
            else:
                gain = 0
            user.score += gain
            lst.append({"username": user.username, "score": user.score, "gain": gain})
        return lst

    def endRound(self):
        self.clearWaiting()
        for user in self.users:
            user.already_answered = False
            if user.states['correct']:
                user.streak += 1
            else:
                user.streak = 0
        self.SuperstateWipe('correct', 'voted_skip')
        # Check if all rounds are up
        if self.current_round != len(self.song_infos):
            self.current_round += 1
            self.SuperstateWipe('correct', 'voted_skip')

    # Must be called before endRound, returns dictionary of song info parsed
    def getAnswer(self):
        song_info = self.song_infos[self.current_round - 1]
        return {
            "album_cover": song_info["album"]["images"][0]["url"],
            "song": song_info["name"],
            "artist": song_info["artists"][0]["name"],
            "year": song_info["album"]["release_date"][0:4],
        }

    def checkAnswer(self, user_input):
        if sanitize(user_input) in self.answers[self.current_round - 1]:
            return True
        else:
            return False

    def inactive(self, user):
        print("inactive called")
        user.states['correct'] = False
        user.states['inactive'] = True
        self.downloaded -= 1
        user.streak = 0
        if not self.users:
            pass
            # TODO: Implement ending of the game

    def reconnect(self, user):
        user.states['inactive'] = False
        user.states['waitlist'] = True
        user.already_answered = True


    def clearWaiting(self):
        self.SuperstateWipe('waitlist')

    def score(self, user):
        time = user.timestamp - self.round_start_time
        return int((1 - (time / self.roundlength)) * 500) + min(user.streak * 100, 500)
    
    def len(self, state):
        return len([user for user in self.users if user.states[state]])
    
    def SuperstateWipe(self, *args):
        for user in self.users:
            user.stateWipe(args)




class User:
    def __init__(self, unique, username, avatar):
        if username == "":
            self.username = "Guest" + str(randint(10000, 99999))
        else:
            self.username = username
        self.unique = unique
        self.already_answered = False
        self.score = 0
        self.streak = 0
        self.timestamp = None
        #States
        self.states = {
            'correct': False,
            'inactive': False,
            'voted_skip': False,
            'waitlist': False

        }
    def stateWipe(self, *args):
        for arg in args:
          self.states[arg] = False
    
    def reset(self):
        self.score = 0
        self.streak = 0
        self.timestamp = None
        self.already_answered = False
        for key in self.states.keys():
            self.states[key] = False
        
    

class avatar:
    def __init__(self):
        pass