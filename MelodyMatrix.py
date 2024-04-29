from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import re
from flask import Flask, request, render_template


app = Flask(__name__)

auth_manager = SpotifyClientCredentials(client_id="c389e6ff9ac847578d6ef13170394d33", client_secret="d96fc96fb1b3462b85d06aa63bac2c1c")
sp = Spotify(auth_manager=auth_manager)
genius = lyricsgenius.Genius("uX8DuZ_OeCJqTtz1f_zuW_Q9UNNORmcRxiq9nCBe-A64dK92Da6jmbLqM-aJcXs5",timeout=15, retries=3)
genius.verbose = False
genius.remove_section_headers = True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_name = request.form['input_name']
        data = get_related_info(input_name)
        return render_template('results.html', data=data)
    return render_template('index.html')



def fetch_lyrics(track_name, artist_name):
    """ Fetch and clean lyrics using the Genius API with error handling """
    try:
        song = genius.search_song(track_name, artist_name)
        if song and song.lyrics:
            lyrics = re.sub(r'\[.*?\]', '', song.lyrics)
            return lyrics.strip()
    except Exception as e:
        print(f"Error fetching lyrics: {e}")
    return "Lyrics not found."

def get_related_info(input_name):
    track_results = sp.search(q=f"track:{input_name}", type='track', limit=1)
    artist_results = sp.search(q=f"artist:{input_name}", type='artist', limit=1)

    if track_results['tracks']['items']:
        track = track_results['tracks']['items'][0]
        track_id = track['id']
        track_name = track['name']
        artist_name = ', '.join(artist['name'] for artist in track['artists'])
        lyrics = fetch_lyrics(track_name, artist_name)
        print(f"Lyrics for {track_name} by {artist_name}:\n{lyrics}")

        # Display related tracks
        related_tracks = sp.recommendations(seed_tracks=[track_id], limit=10)['tracks']
        print("\nRelated Tracks:")
        for related_track in related_tracks:
            print(f"{related_track['name']} by {', '.join(artist['name'] for artist in related_track['artists'])}")

    if artist_results['artists']['items']:
        artist = artist_results['artists']['items'][0]
        artist_id = artist['id']
        artist_name = artist['name']

        # Fetch and display top tracks
        top_tracks = sp.artist_top_tracks(artist_id)['tracks']
        print(f"\nTop Tracks for {artist_name}:")
        for track in top_tracks:
            print(f"{track['name']} - Popularity: {track['popularity']}")

        # Display related artists
        related_artists = sp.artist_related_artists(artist_id)['artists']
        print(f"\nRelated Artists for {artist_name}:")
        for related_artist in related_artists:
            print(f"{related_artist['name']} - Popularity: {related_artist['popularity']}")
    data = {
        'lyrics_info': None,
        'related_tracks': [],
        'top_tracks': [],
        'related_artists': []
    }

    track_results = sp.search(q=f"track:{input_name}", type='track', limit=1)
    artist_results = sp.search(q=f"artist:{input_name}", type='artist', limit=1)

    if track_results['tracks']['items']:
        track = track_results['tracks']['items'][0]
        track_id = track['id']
        track_name = track['name']
        artist_name = ', '.join(artist['name'] for artist in track['artists'])
        lyrics = fetch_lyrics(track_name, artist_name)
        data['lyrics_info'] = {'track_name': track_name, 'artist_name': artist_name, 'lyrics': lyrics}

        related_tracks = sp.recommendations(seed_tracks=[track_id], limit=10)['tracks']
        for related_track in related_tracks:
            data['related_tracks'].append({
                'name': related_track['name'],
                'artists': ', '.join(artist['name'] for artist in related_track['artists'])
            })

    if artist_results['artists']['items']:
        artist = artist_results['artists']['items'][0]
        artist_id = artist['id']
        artist_name = artist['name']

        top_tracks = sp.artist_top_tracks(artist_id)['tracks']
        for track in top_tracks:
            data['top_tracks'].append({
                'name': track['name'],
                'popularity': track['popularity']
            })

        related_artists = sp.artist_related_artists(artist_id)['artists']
        for related_artist in related_artists:
            data['related_artists'].append({
                'name': related_artist['name'],
                'popularity': related_artist['popularity']
            })

    return data


def main():
    input_name = input("Enter the name of a track or an artist: ")
    get_related_info(input_name)

if __name__ == "__main__":
    app.run(debug=True)