import pyen
from spotipy import client, util, oauth2
import numpy
import json
import sys, random, os

nest_key = os.environ['ECHONEST_KEY']

nest = pyen.Pyen(nest_key)

steve_spotify_id = '1210159879'

PLAYLIST_IDS = {
    'fall': '4wm4J4d2cKeTTCJ4Mzz06M',
    'winter': '7EUoqdUjR91tMmp41nw7Y4',
    'spring': '0rmr2dJ3fuudkrXyIXZgIZ',
    'summer': '3mpSb7dwheLtB6QdvIBV2m',
    'rainy': '2u7t4X9wA2B493qQgR47aW'
}

SONG_DATA_FIELDS = {
    'danceability',
    'energy',
    'loudness',
    'mode',
    'key',
    'tempo',
    'valence'
}

use_cache = True

"""FILE IO"""

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
def fetch_song_data():
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

#Wire this up to a weather API
def is_raining():
    return False

#Should have a dict of valid season values somewhere
#Gonna hard code each season for now because HACKDAYZ
def get_seasonal_params(season, stats):
    query = {}

    season_stats = stats[season]
    if season == 'fall' or season == 'winter':
        query['max_energy'] = season_stats['energy']['mean'] + (season_stats['energy']['std'] / 2)
        query['min_energy'] = season_stats['energy']['mean'] - season_stats['energy']['std']
        query['max_valence'] = season_stats['valence']['mean'] + (season_stats['valence']['std'] / 2)
        query['min_valence'] = season_stats['valence']['mean'] - season_stats['valence']['std']
    elif season == 'spring' or season == 'summer':
        query['max_energy'] = season_stats['energy']['mean'] + season_stats['energy']['std']
        query['min_energy'] = season_stats['energy']['mean'] - (season_stats['energy']['std'] / 2)
        query['max_valence'] = season_stats['valence']['mean'] + season_stats['valence']['std']
        query['min_valence'] = season_stats['valence']['mean'] - (season_stats['valence']['std'] / 2)

    if is_raining():
        query['max_tempo'] = stats['rainy']['tempo']['mean']
        query['min_tempo'] = stats['rainy']['tempo']['mean'] - stats['rainy']['tempo']['std']
    #Also decrease the valence and energy by something

    return query

def get_new_songs_alt(season, stats):
    query = {}
    query['genre'] = ['stomp and holler', 'indie folk']
    query['sort'] = ['hotttnesss-desc']
    query['results'] = ['100']
    # Get up to 200 artists. This is so messy
    artists = nest.get('artist/search', query)['artists']
    query['start'] = ['100']
    artists.extend(nest.get('artist/search', query)['artists'])
    
    songs = []
    song_query = get_seasonal_params(season, stats)
    for artist in artists:
        song_query['artist_id'] = artist['id']
        song_query['results'] = ['10']
        songs.extend(nest.get('song/search', song_query)['songs'])

    return random.sample(songs, 30)

# Take songs from Echonest api, search for them in spotify to get their ID,
# add to newly created playlist
def make_playlist(spot, songs, name):
    playlist = spot.user_playlist_create(steve_spotify_id, name)
    ids = []
    for song in songs:
        query = 'track:'+ song['title'] + ' artist:' + song['artist_name']
        results = spot.search(query, 1, 0, 'track')['tracks']['items']
        if(results):
            ids.append(results[0]['id'])
    spot.user_playlist_add_tracks(steve_spotify_id, playlist['id'], ids)


def main(argv):
    token = util.prompt_for_user_token(steve_spotify_id, 'playlist-modify-public')
    spot = client.Spotify(token)
    songs = {}
    if use_cache:
        songs = load_cache()
    else:
        songs = fetch_song_data()
        write_cache(songs)
    stats = {}
    for season in songs:
        print 'Analyzing season: ' + season
        stats[season] = compute_stats(songs[season])
    write_metrics(stats)

    new_songs = get_new_songs_alt('summer', stats)
    make_playlist(spot, new_songs, 'Spiffy: Fall New')


if __name__ == "__main__":
    main(sys.argv[1:])

