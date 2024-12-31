# Filename: input_spotify_id_output_MBID.py

import csv
import requests
import time

def get_artist_mbid(spotify_artist_id):
    # Construct the Spotify URL from the artist ID
    spotify_url = f"https://open.spotify.com/artist/{spotify_artist_id}"

    # Base URL for MusicBrainz API
    base_url = "https://musicbrainz.org/ws/2/url/"

    # Parameters for the API request
    params = {
        "resource": spotify_url,
        "fmt": "json",
        "inc": "artist-rels"
    }

    retries = 3  # Number of retries for transient errors (e.g., 503)
    while retries > 0:
        try:
            # Send GET request to MusicBrainz API
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the JSON response
            data = response.json()

            # Extract the artist MBID from relationships
            if "relations" in data:
                for relation in data["relations"]:
                    if relation["type"] == "free streaming" and "artist" in relation:
                        return relation["artist"]["id"]

            return "Not Found"

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return "Not Found"
            elif response.status_code == 503:
                retries -= 1
                time.sleep(2)  # Wait before retrying
                continue
            else:
                return f"An error occurred: {e}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    return "Service Unavailable"

def process_csv(input_file, output_file):
    with open(input_file, mode="r") as infile, open(output_file, mode="w", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)

        # Write header to output CSV
        writer.writerow(["Name", "SpotifyID", "Profile Image", "MBID"])

        # Process each row in the input CSV
        for row in reader:
            name = row["Name"]
            spotify_id = row["SpotifyID"]
            profile_image = row["Profile Image"]
            mbid = get_artist_mbid(spotify_id)
            writer.writerow([name, spotify_id, profile_image, mbid])
            time.sleep(1)  # Add delay between requests to avoid server overload

if __name__ == "__main__":
    input_csv = "top_100_artists.csv"
    output_csv = "artists_mbid.csv"

    process_csv(input_csv, output_csv)
    print(f"Results have been written to '{output_csv}'.")
