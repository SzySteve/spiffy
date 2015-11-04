import pyen
from spotipy import client, util, oauth2
import numpy
import json

nest = pyen.Pyen('SKHFYAIUO1CEEL9A1')

spotify_token = oauth2.SpotifyClientCredentials(client_id='9d21af84de0a41b28894a35af9533b2c',
    client_secret='260ca31f34f24ca1805051944ab09246').get_access_token()

spot = client.Spotify(spotify_token)

steve_spotify_id = '1210159879'

PLAYLIST_IDS = {
    'fall': '4wm4J4d2cKeTTCJ4Mzz06M',
    'winter': '7EUoqdUjR91tMmp41nw7Y4',
    'spring': '0rmr2dJ3fuudkrXyIXZgIZ',
    'summer': '3mpSb7dwheLtB6QdvIBV2m'
}

SONG_DATA_FIELDS = {
    'danceability',
    'energy',
    'loudness',
    'mode',
    'key',
    'tempo'
}

use_cache = True

song_cache = {}

def compute_stats(season):
    stats = {}
    for field in SONG_DATA_FIELDS:
        raw = [track['audio_summary'][field] for track in season]
        mean = numpy.mean(raw)
        std = numpy.std(raw)

        stats[field] = {
            'raw': raw,
            'mean': mean,
            'std': std
        }

    return stats

if use_cache:
    with open('songCache.json') as data_file:    
        song_cache = json.load(data_file)
else:
    for season in PLAYLIST_IDS:
        print 'Fetching season playlist: ' + season
        playlist = spot.user_playlist_tracks(steve_spotify_id, PLAYLIST_IDS[season])

        playlist_tracks = []

        for item in playlist['items']:
            track = item['track']
            playlist_tracks.append({
                'title': track['name'],
                'artist': track['artists'][0]['name']
                })

        analyzed_tracks = []

        print 'Fetching song analysis: ' + season
        for track in playlist_tracks:
            results = nest.get('song/search', artist=track['artist'],
                title=track['title'], bucket='audio_summary')
            # Should prolly be exception handled but WHATEVER HACKDAYZ
            if results['songs']:
                analyzed_tracks.append(results['songs'][0])

        song_cache[season] = analyzed_tracks

    with open('songCache.json', 'w') as outfile:
        json.dump(song_cache, outfile)
    
stats = {}
for season in song_cache:
    print 'Analyzing season: ' + season
    stats[season] = compute_stats(song_cache[season])
with open('metrics.json', 'w') as outfile:
    json.dump(stats, outfile)




