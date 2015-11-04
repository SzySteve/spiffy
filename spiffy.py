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

"""FILE IO"""
def load_creds():
    creds = {}
    with open('creds.json') as data_file:    
        creds = json.load(data_file)
    #DO CRED RELATED STUFF

# Load cached songs
def load_cache():
    song_cache = {}
    with open('songCache.json') as data_file:    
        song_cache = json.load(data_file)
    return song_cache

# Write songs to cache
def write_cache(songs):
    with open('songCache.json', 'w') as outfile:
        json.dump(songs, outfile)

# Write song metrics
def write_metrics(stats):
    with open('metrics.json', 'w') as outfile:
        json.dump(stats, outfile)



#Compute stats for a season
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

#Fetch songs from remote API
def fetch_songs():
    songs = {}
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

        songs[season] = analyzed_tracks
    return songs

def main():
    songs = {}
    if use_cache:
        songs = load_cache()
    else:
        songs = fetch_songs()
        write_cache(songs)
    stats = {}
    for season in songs:
        print 'Analyzing season: ' + season
        stats[season] = compute_stats(songs[season])
    write_metrics(stats)


if __name__ == "__main__":
    main()

