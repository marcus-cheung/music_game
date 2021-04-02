from random import randint
import spotipy
import re

class GameState:
    max_users = 8

    def __init__(
        self, room_number, gamemode, song_infos, rounds, host, playlists, users = [], roundlength=90, password=None
    ):
        #On call
        self.room_number = room_number
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
        #Used each round
        self.correct = []
        self.current_round = 1
        self.round_start = False
        #Mutated when making/joining room
        self.users = users
        self.allowed = []
        self.answers = []
        self.sockets = []
        self.game_ended = False
        #get the answers
        for song_info in self.song_infos:
            if self.gamemode == 'song':
                print('name: '+song_info['name'])
                self.answers.append(answer_variations(song_info['name']))
            if self.gamemode == 'year':
                release_date = song_info['album']['release_date']
                year = release_date[0:4]
                self.answers.append([year])
            if self.gamemode == 'artist':
                self.answers.append([sanitize(song_info['artists'][0]['name'])])
        
        
    def allow(self, unique):
        self.allowed.append(unique)

    # called when someone connects to a /game
    def addUser(self, user):
        self.users.append(user)

    def kickUser(self, user):
        self.users.remove(user)

    def getScoreDATA(self):
        lst = []
        for user in self.correct:
            gain = 100-self.correct.index(user)*5
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
        return {'song':song_info['name'], 'artist':song_info['artists'], 'year': song_info['album']['release_date'][0:4]}

    def checkAnswer(self, user_input):
        print('user_input')
        print(sanitize(user_input))
        if sanitize(user_input) in self.answers[self.current_round-1]:
            print('Correct')
            return True
        else:
            return False

        


class User:
    def __init__(self, unique, username):
        if username == "":
            self.username = "Guest" + str(randint(10000, 99999))
        else:
            self.username = username
        self.unique = unique
        self.already_answered = False
        self.score = 0


# Sanitizes a string
def sanitize(answer):
    special_char = 'ñńçčćàáâäæãåāèéêëēėęôöòóœøōõîïíīįìûüùúūžźżÿłßśš'
    translation = 'nncccaaaaaaaaeeeeeeeooooooooiiiiiiuuuuuzzzylsss'
    table = answer.maketrans(special_char,translation)
    #Special chars fixed, spaces removed, lowercase
    string = answer.translate(table).replace(" ", "").lower()
    return string

def answer_variations(answer):
    answers = [answer]
    sanitized = sanitize(answer)
    answers.append(sanitized)
    # Remove stuff
    no_paren = remove_paren(sanitized)
    no_sqrBracket = remove_sqrBracket(sanitized)
    no_hyphen = remove_hyphen(sanitized)
    no_paren_hyphen = remove_paren(no_hyphen)
    answers.append(no_paren_hyphen)
    answers.append(no_paren)
    answers.append(no_sqrBracket)
    answers.append(no_hyphen)
    print(answers)
    return answers

def remove_paren(string):
    if '(' and ')' in string:
        return string[0:string.index('(')] + string[string.index(')')+1:]
    else:
        return string
def remove_sqrBracket(string):
    if '[' and ']' in string:
        return string[0:string.index('[')] + string[string.index(']')+1:]
    else:
        return string
def remove_hyphen(string):
    if '-' in string:
        return string[0:string.index('-')]
    else:
        return string