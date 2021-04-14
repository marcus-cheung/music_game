import json
import requests
import time

base_url = 'https://api.spotify.com/v1/'

markets = [ "AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY",
      "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU",
      "ID", "IE", "IS", "IT", "JP", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL",
      "NO", "NZ", "PA", "PE", "PH", "PL", "PT", "PY", "SE", "SG", "SK", "SV", "TH", "TR", "TW",
      "US", "UY", "VN" ]

myurl = "https://knewsic.herokuapp.com/"

# auth stuff chr
client_id = "f50f20e747fb4bda8d9352696004cda4"
default_redirect_uri = myurl + 'super-secret-default-spotify/callback/'

def getDefaultToken(): 
    #Open file
    with open('static/default_spotify.json', 'r+') as f:
        #load it as a dictionary
        spotify_data = json.load(f)
        #save first instance of access token
        access_token = spotify_data['access_token']
        # If expired, fetch refreshed token
        if spotify_data['expires_at'] < int(time.time()):
            user_data = requests.post('https://accounts.spotify.com/api/token', data = {'grant_type': 'refresh_token', 'refresh_token': spotify_data['refresh_token'], 'client_id': client_id})
            #if everything good reupdate session data
            if user_data.status_code == 200:
                spotify_data = user_data.json()
                spotify_data['expires_at'] = int(time.time()) + spotify_data['expires_in']
                access_token = spotify_data['access_token']
                #save new data into json file
                f.seek(0)
                f.truncate(0)
                json.dump(spotify_data, f, indent = 4)
            else:
                print('getToken error: ' + str(user_data.status_code))
        return access_token


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
    header = {'Authorization': 'Bearer ' + access_token}
    all_song_infos = []
    for playlist_id in playlist_ids:
        print(playlist_id)
        playlist_data = None
        market = None
        for test_market in markets:
            playlist_data = requests.get(base_url + f'playlists/{playlist_id}/tracks', {'limit': 100, 'market':test_market}, headers=header)
            if validStatus(playlist_data):
                market = test_market
                break
        playlist_json = playlist_data.json()
        if validStatus(playlist_data):
            all_song_infos += playlist_json['items']
            index = 1
            while playlist_json['next'] != None:
                playlist_data = requests.get(base_url + f'playlists/{playlist_id}/tracks', {'limit': 100, 'offset': index * 100, 'market':market}, headers = header)
                playlist_json = playlist_data.json()
                all_song_infos += [item['tracks'] for item in playlist_json['items']]
                index += 1
        else:
            print('getPlaylistSongs Error: Code ' + str(playlist_data.status_code))
    return all_song_infos



def getAlbumSongs(album_ids, access_token):
    header = {'Authorization': 'Bearer ' + access_token}
    all_song_infos = []
    for album_id in album_ids:
        print(album_id)
        album_song_infos = []
        album_data = None
        market = None
        for test_market in markets:
            album_data = requests.get(base_url + f'albums/{album_id}/tracks', {'limit': 50, 'market': test_market}, headers=header)
            if validStatus(album_data):
                market = test_market
                break
        if validStatus(album_data):
            album_json = album_data.json()
            album_song_infos += album_json['items']
            index = 1
            while album_json['next'] != None:
                album_data = requests.get(base_url + f'albums/{album_id}/tracks', {'limit': 50, 'market': market, 'offset': 50 * index}, headers = header)
                album_json = album_data.json()
                album_song_infos += album_json['items']
                index += 1
            # Get the album info
            album_info_json = requests.get(base_url + f'albums/{album_id}', {'market': market}, headers = header).json()
            # Adds the album info to each song info
            for song_info in album_song_infos:
                song_info['album'] = album_info_json
            all_song_infos += album_song_infos
        else:
            print('getAlbumSongs Error: Code ' + str(album_data.status_code))
    return all_song_infos


def getArtistsSongs(artist_ids, access_token, include_feature = False):
    header = {'Authorization': 'Bearer ' + access_token}
    all_song_infos = []
    album_groups = 'album,single'
    if include_feature:
        album_groups += ',appears_on'
    for artist_id in artist_ids:
        all_album_infos = []
        artist_data = None
        market = None
        for test_market in markets:
            artist_data = requests.get(base_url + f'artists/{artist_id}/albums', {'limit': 50, 'market': test_market, 'include_groups': album_groups}, headers= header)
            if validStatus(artist_data):
                market = test_market
                break
        if validStatus(artist_data):
            artist_json = artist_data.json()
            all_album_infos += artist_data.json()['items']
            index = 1
            while artist_json['next'] != None:
                artist_data = requests.get(base_url + f'artists/{artist_id}/albums', {'limit': 50, 'offset': 50 * index, 'market': market, 'include_groups': album_groups}, headers= header)
                artist_json = artist_data.json()
                all_album_infos += artist_json['items']
                index += 1
        else:
            print('getArtistsSongs Error: Code ' + str(artist_data.status_code))
        for album_info in all_album_infos:
            all_song_infos += getAlbumSongs([album_info['id']], access_token)
    return all_song_infos



def getArtistInfos(artist_name, limit = 1):
    header = {'Authorization': 'Bearer ' + getDefaultToken()}    
    artist_data = requests.get(base_url + 'search', {'q': artist_name, 'type': 'artist', 'limit': limit}, headers = header)
    if validStatus(artist_data):
        return artist_data.json()['artists']['items']
    else:
        print('getArtistINFO Error: Code ' + str(artist_data.status_code))

def validStatus(request):
    return request.status_code==200

# Called on search
def getArtistSearch(artist_name):
    limit = 5
    artist_json = getArtistInfos(artist_name, limit = limit)
    payload = []
    for entry in artist_json:
        artist_info = {'name': entry['name'], 'id': entry['id']}
        if entry['images'] != []:
            artist_info['image'] = entry['images'][0]['url']
        else:
            pass
            # TODO: Add default image
        payload.append(artist_info)
    return payload

print(getPlaylistSongs(['37i9dQZEVXbMDoHDwVN2tF'],getDefaultToken())[49])