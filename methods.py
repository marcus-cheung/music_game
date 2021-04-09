import random
from youtubesearchpython import VideosSearch
import os
import shutil
import pafy
import string

def song_selector(allsongs, rounds):
    song_infos = []
    if len(allsongs) == 0:
        return []
    for i in range(rounds):
        x = random.randint(0,len(allsongs) - 1)
        #Check if song already in list of songs
        while allsongs[x]['track'] in song_infos:
            #remove duplicate song
            allsongs.pop(x)
            # Breaks loop if allsongs empty
            if len(allsongs) == 0:
                return []
            #generates new index to check
            x = random.randint(0,len(allsongs) - 1)
        #Appends valid song to song_infos
        song_infos.append(allsongs.pop(x)['track'])
    return song_infos

def download_music_file(query, roomnumber, filename, filetype='m4a', bitrate='48k', lyric=True):
    destination = 'static/music/' + str(roomnumber)
    path = destination + '/' + sanitize(filename) + '.' + filetype
    if lyric:
        query += ' lyric'
    top_result = VideosSearch(query, limit=1).result()['result'][0]
    url = top_result['link']
    print(url)
    video = pafy.new(url)
    audiostreams = video.audiostreams
    filetype_audiostreams = []
    final_file = None
    for audiostream in audiostreams:
        # print(audiostream)
        # print(audiostream.bitrate)
        if audiostream.extension == filetype:
            filetype_audiostreams.append(audiostream)
    for audiostream in filetype_audiostreams:
        # print(audiostream)
        if audiostream.bitrate==bitrate:
            final_file = audiostream
        else:
            final_file = filetype_audiostreams[len(filetype_audiostreams) - 1]
    # Overwrite existing file if it exists
    if os.path.isfile(path):
        os.remove(path)
    final_file.download(path, quiet=True)


def download_songs(room, song_infos):
    for song in song_infos:
        song_name = song['name']
        song_artist = song['artists'][0]['name']
        download_music_file(song_name + ' ' + song_artist, room, song_name)


def makeDir(room):
    directory =  'static/music' + '/' + str(room)
    #checks if directory exists
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

# Sanitizes a string
def sanitize(answer):
    s = answer.lower()
    special_char = 'ñńçčćàáâäæãåāèéêëēėęôöòóœøōõîïíīįìûüùúūžźżÿłßśš'
    translation = 'nncccaaaaaaaaeeeeeeeooooooooiiiiiiuuuuuzzzylsss'
    table = s.maketrans(special_char,translation)
    #Special chars fixed, spaces removed, lowercase
    s = s.translate(table).replace(" ", "")
    return s

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
    no_punc = []
    for answer in answers:
        no_punc.append(remove_punc(answer))
    answers += no_punc
    return answers

def remove_paren(string):
    while '(' in string and ')' in string:
        string = string[0:string.index('(')] + string[string.index(')')+1:]
    return string

def remove_sqrBracket(string):
    while '[' in string and ']' in string:
        string =  string[0:string.index('[')] + string[string.index(']')+1:]
    return string

def remove_hyphen(string):
    if '-' in string:
        return string[0:string.index('-')]
    else:
        return string

def remove_punc(s):
    return s.translate(str.maketrans('', '', string.punctuation))

def super_sanitize(string):
    return remove_punc(sanitize(string))
