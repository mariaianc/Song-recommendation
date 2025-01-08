import requests
import json
import base64
import csv
import os
from dotenv import load_dotenv

# CLIENT_ID = "b5c0e40efaa34b7f8e796e32896e155b"
# CLIENT_SECRET = "a939d203707a475a907708f862e097cb"

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_token(token):
    return {"Authorization": "Bearer " + token}


def search_song(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_token(token)
    query = f"?q={song_name}&type=track&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)

    song_info = {}

    if 'tracks' in json_result and json_result['tracks']['items']:
        track = json_result['tracks']['items'][0]
        track_id = track['id']
        track_name = track["name"]
        artist_name = ", ".join(artist["name"] for artist in track["artists"])
        album_name = track["album"]["name"]
        track_url = track["external_urls"]["spotify"]
        track_popularity = track["popularity"]
        duration_ms = track["duration_ms"]

        song_info = {
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": album_name,
            "track_url": track_url,
            "popularity": track_popularity,
            "duration_ms": duration_ms,
        }

        # Get artist genres
        artist_id = track["artists"][0]["id"]
        genre = get_artist_primary_genre(token, artist_id)

        song_info["primary_genre"] = genre
    else:
        song_info = {"track_name": song_name, "artist_name": "N/A", "primary_genre": "N/A"}

    return song_info


def get_artist_primary_genre(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_token(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)

    genre = "UNKNOWN"
    if json_result and 'genres' in json_result:
        genres = json_result['genres']
        if genres:
            genre = genres[0]  # Taking the first genre as the primary genre
    return genre


def read_csv(input_csv):
    """Read the CSV file and return song title and artist pairs."""
    songs_data = []
    with open(input_csv, mode="r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        next(reader)  # Skip header row if there is one
        for row in reader:
            song_title = row[0]
            artist_name = row[1]
            songs_data.append((song_title, artist_name))
    return songs_data


def write_to_csv(output_csv, data):
    """Write processed song data into a CSV file."""
    with open(output_csv, mode="w", newline='', encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def process_songs(input_csv, token, output_csv):
    """Read songs from CSV, process each one, and write the results to another CSV file."""
    songs_data = read_csv(input_csv)
    processed_songs = []

    for song_title, artist_name in songs_data:
        song_info = search_song(token, song_title)
        processed_songs.append(song_info)

    write_to_csv(output_csv, processed_songs)
