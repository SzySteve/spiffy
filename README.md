# spiffy
Seasonal/Weather-Based Spotify Playlist Generator

##Setup Instructions
Get API keys for The Echo Nest and Spotify, add them to the correct environment variables.
```
export SPOTIPY_CLIENT_ID='your-spotify-client-id'
export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
export ECHONEST_KEY='your-echonest-key'
```

You need the following python packages
* Pyen
* Spotipy


##ToDo
* Make this a web-facing application
* Tweak song selection for better results
  * Less duplicate artists
  * Figure out Echo Nest's genre/style distinction
* Implement a weather API to determine if it is currently precipitating
* Get a larger sample of music
