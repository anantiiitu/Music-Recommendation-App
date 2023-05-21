import spotipy
from spotipy.oauth2 import SpotifyOAuth
from scipy.spatial import distance

client_id = "73480adb178a409e81402cb141b"  # Update your client id
client_secret = "2e9d9e7ff39442390785c41841"  # Update your client secret
redirect_uri = "http://localhost:8000/callback"  # Update with your redirect URI

# Set up the SpotifyOAuth object
scope = "user-read-recently-played"
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
)

# Obtain the authorization URL
auth_url = sp_oauth.get_authorize_url()
print(f"Please visit this URL to authorize the application: {auth_url}")

# Redirect the user to the authorization URL and obtain the authorization code
# Paste the obtained authorization code here
code = input("Enter the authorization code: ")

# Exchange the authorization code for an access token
token_info = sp_oauth.get_access_token(code)
access_token = token_info["access_token"]

# Create a new Spotipy instance using the access token
sp = spotipy.Spotify(auth=access_token)

# Define a list to store all the song features
all_song_features = []

# Define a list to store all the songs
all_songs = []


def get_song_features(track_id):
    features = sp.audio_features(track_id)
    if features:
        return features[0]
    return None


def get_similar_songs(song_features, num_songs=5):
    song_distances = []
    for idx, features in enumerate(all_song_features):
        if features is not None:
            dist = distance.euclidean(song_features, features)
            song_distances.append((idx, dist))
    sorted_songs = sorted(song_distances, key=lambda x: x[1])
    similar_songs = [all_songs[idx] for idx, _ in sorted_songs[:num_songs]]
    return similar_songs


# Retrieve the recently played tracks
def get_recently_played_tracks():
    results = sp.current_user_recently_played()
    for idx, item in enumerate(results["items"]):
        track = item["track"]
        all_songs.append(track["name"])
        song_features = get_song_features(track["id"])
        all_song_features.append(song_features)
        print(f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}")


# Main program
def main():
    # Get recently played tracks
    print("Retrieving recently played tracks...")
    get_recently_played_tracks()
    print()

    # Prompt the user for a track index
    while True:
        try:
            track_index = int(
                input(
                    "Enter the track index to get similar recommendations (0 to exit): "
                )
            )
            if track_index == 0:
                break
            if track_index < 1 or track_index > len(all_songs):
                print("Invalid track index. Please try again.")
                continue
            selected_track = all_songs[track_index - 1]
            selected_features = all_song_features[track_index - 1]
            similar_songs = get_similar_songs(selected_features)
            print(f"\nRecommended songs similar to '{selected_track}':")
            for idx, song in enumerate(similar_songs):
                print(f"{idx + 1}. {song}")
            print()
        except ValueError:
            print("Invalid input. Please try again.")


if __name__ == "__main__":
    main()
