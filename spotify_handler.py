import json
import requests

base_url = 'https://api.spotify.com/v1/me/'

def getPlaylists(access_token):
    header = {'Authorization': 'Bearer '+access_token}
    playlist_data = requests.get(base_url + 'playlists', {'limit':20}, headers = header)
    playlist_json = playlist_data.json()
    playlist_infos = []
    if playlist_data.status_code == 200:
        playlist_infos += playlist_json['items']
        index = 1
        while playlist_json['next'] != None:
            # request
            playlist_data = requests.get(base_url + 'playlists', {'limit':20, 'offset': 20 * index}, headers = header)
            print(playlist_data)
            # change playlist_json
            playlist_json = playlist_data.json()
            # add playlist 
            playlist_infos += playlist_json['items']
    return playlist_infos

    
    
def artists_songs(artist_name, number):
    pass
    # sp = spotipy.Spotify('BQAPMMQyspUy_qKzNTVCg3SAMnKRsPtRnTFkRjC29v_OCPbsPnvFYkpj8JguSzEH5a1v0IErw5DW6XrIC7oygltpPKk7Oay9tv6eQMLse5yj_rZm9B8M2vbYZxu9RKPjD_1wxPYCJ2Bwa53IRu8yLh7mc9Lth5Q')
    # artist_id = sp.search(artist_name, type = 'artist')['artists']['items'][0]['id']
    # album_infos = sp.artist_albums(artist_id, limit = 2)['items']
    # song_infos = []
    # for album_info in album_infos:
    #     print(album_info['name'])
    #     print(album_info['id'])
    #     album_tracks = sp.album_tracks(album_info['id'])['items']
    #     print(album_tracks)
    #     song_infos += album_tracks
    # return song_selector(song_infos, rounds)

