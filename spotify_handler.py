import json
import requests

base_url = 'https://api.spotify.com/v1/'

markets = [ "AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY",
      "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU",
      "ID", "IE", "IS", "IT", "JP", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL",
      "NO", "NZ", "PA", "PE", "PH", "PL", "PT", "PY", "SE", "SG", "SK", "SV", "TH", "TR", "TW",
      "US", "UY", "VN" ]

def getPlaylists(access_token):
    header = {'Authorization': 'Bearer '+ access_token}
    playlists_data = requests.get(base_url + 'me/playlists', {'limit':20}, headers = header)
    playlists_json = playlists_data.json()
    playlist_infos = []
    if validStatus(playlists_data):
        playlist_infos += playlists_json['items']
        index = 1
        while playlists_json['next'] != None:
            # request
            playlists_data = requests.get(base_url + 'me/playlists', {'limit':20, 'offset': 20 * index}, headers = header)
            print(playlists_data)
            # change playlist_json
            playlists_json = playlists_data.json()
            # add playlist 
            playlist_infos += playlists_json['items']
            index += 1
    return playlist_infos

def getPlaylistSongs(playlist_ids, access_token):
    header = {'Authorization': 'Bearer '+access_token}
    all_song_infos = []
    for playlist_id in playlist_ids:
        print(playlist_id)
        playlist_data = None
        for market in markets:
            playlist_data = requests.get(base_url + f'playlists/{playlist_id}/tracks', {'limit': 100, 'market':market}, headers=header)
            if validStatus(playlist_data):
                break
        playlist_json = playlist_data.json()
        if validStatus(playlist_data):
            all_song_infos += playlist_json['items']
            index = 1
            while playlist_json['next'] != None:
                playlist_data = requests.get(base_url + f'playlists/{playlist_id}/tracks', {'limit': 100, 'offset': index * 100, 'market':market}, headers = header)
                playlist_json = playlist_data.json()
                all_song_infos += playlist_json['items']
                index += 1
        else:
            print('getPlaylistSongs Error: Code ' + str(playlist_data.status_code))
    return all_song_infos


def validStatus(request):
    return request.status_code==200

def artists_songs(artist_name, number):
    pass
    sp = spotipy.Spotify('BQAPMMQyspUy_qKzNTVCg3SAMnKRsPtRnTFkRjC29v_OCPbsPnvFYkpj8JguSzEH5a1v0IErw5DW6XrIC7oygltpPKk7Oay9tv6eQMLse5yj_rZm9B8M2vbYZxu9RKPjD_1wxPYCJ2Bwa53IRu8yLh7mc9Lth5Q')
    artist_id = sp.search(artist_name, type = 'artist')['artists']['items'][0]['id']
    album_infos = sp.artist_albums(artist_id, limit = 2)['items']
    song_infos = []
    for album_info in album_infos:
        print(album_info['name'])
        print(album_info['id'])
        album_tracks = sp.album_tracks(album_info['id'])['items']
        print(album_tracks)
        song_infos += album_tracks
    return song_selector(song_infos, rounds)