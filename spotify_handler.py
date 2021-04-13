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
                all_song_infos += playlist_json['items']
                index += 1
        else:
            print('getPlaylistSongs Error: Code ' + str(playlist_data.status_code))
    return all_song_infos

def getAlbumSongs(album_ids, access_token):
    header = {'Authorization': 'Bearer ' + access_token}
    all_song_infos = []
    for album_id in album_ids:
        album_data = None
        market = None
        for test_market in markets:
            album_data = requests.get(base_url + f'albums/{album_id}/tracks', {'limit': 50, 'market': test_market}, headers=header)
            if validStatus(album_data):
                market = test_market
                break
        if validStatus(album_data):
            album_json = album_data.json()
            all_song_infos += album_json['items']
            index = 1
            while album_json['next'] != None:
                album_data = requests.get(base_url + f'albums/{album_id}/tracks', {'limit': 50, 'market': market, 'offset': 50 * index}, headers = header)
                album_json = album_data.json()
                all_song_infos += album_json['items']
                index += 1
        else:
            print('getAlbumSongs Error: Code ' + str(album_data.status_code))
    return all_song_infos

def getArtistsSongs(artist_ids, access_token):
    header = {'Authorization': 'Bearer ' + access_token}
    all_album_infos = []
    album_groups = 'album, single, appears_on'
    # TODO: Look through that come from appears_on albums to make sure that the artist actually appears on it.
    for artist_id in artist_ids:
        artist_data = None
        market = None
        for test_market in markets:
            artist_data = requests.get(base_url + f'artists/{artist_id}/albums', {'limit': 50, 'market': test_market, 'include_groups': album_groups}, headers= header)
            if validStatus(artist_data):
                market = test_market
                break
        if validStatus(artist_data):
            artist_json = artist_data.json()
            all_album_infos += artist_data.json()
            index = 1
            while artist_json['next'] != None:
                artist_data = requests.get(base_url + f'artists/{artist_id}/albums', {'limit': 50, 'offset': 50 * index, 'market': market, 'include_groups': album_groups}, headers= header)
                artist_json = artist_data.json()
                all_album_infos += artist_json['items']
                index += 1
        else:
            print('getArtistsSongs Error: Code ' + str(artist_data.status_code))
    album_ids = []
    for album_info in all_album_infos:
        album_ids.append(album_info['id'])
    return getAlbumSongs(album_ids, access_token)


def validStatus(request):
    return request.status_code==200

