base_url = https://api.spotify.com/v1/me/

def getPlaylists(access_token):
    playlist_data = requests.get(base_url + '/playlists', data = {limit: 10}, headers = {'Authorization':access_token})
    
    
def artists_songs(artist_name, number):
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
    