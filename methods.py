
import random
from youtubesearchpython import VideosSearch
import os
import shutil
import pafy

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
    path = destination + '/' + filename + '.' + filetype
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