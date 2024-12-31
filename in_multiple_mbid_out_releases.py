import requests
import csv
import time

def get_albums_with_release_countries(mbid):
    # Base URLs for MusicBrainz API
    base_url = "https://musicbrainz.org/ws/2/release-group"
    release_base_url = "https://musicbrainz.org/ws/2/release"

    # Parameters for the release-group API request
    params = {
        "artist": mbid,
        "type": "album",  # Filter by primary type "album"
        "fmt": "json",   # Request JSON format
        "limit": 100     # Limit results to 100 per request
    }

    albums = []
    offset = 0

    while True:
        # Add offset for pagination
        params["offset"] = offset

        # Make the API request with a delay
        time.sleep(1)  # Delay to avoid rate-limiting
        response = requests.get(base_url, params=params)

        # Check for successful response
        if response.status_code != 200:
            print(f"Error: Unable to fetch data (status code {response.status_code})")
            break

        data = response.json()

        # Extract release groups
        release_groups = data.get("release-groups", [])
        for rg in release_groups:
            # Skip release groups with secondary types
            if rg.get("secondary-types"):
                continue

            # Query the releases to collect release countries
            time.sleep(1)  # Delay to avoid rate-limiting
            release_response = requests.get(
                release_base_url,
                params={
                    "release-group": rg["id"],
                    "fmt": "json"
                }
            )

            countries = []
            if release_response.status_code == 200:
                releases = release_response.json().get("releases", [])
                for release in releases:
                    country = release.get("country", "Unknown")
                    if country:
                        countries.append(country)

            # Filter albums to include only those released in GB or US
            filtered_countries = [country for country in countries if country in ["GB", "US"]]
            if not filtered_countries:
                continue

            # Add album information to the list
            album_info = {
                "title": rg["title"],
                "primary_type": rg.get("primary-type", "Unknown"),
                "release_year": rg.get("first-release-date", "Unknown")[:4],
                "artist_mbid": mbid,
                "secondary_types": None,  # Explicitly set to None since these are filtered out
                "release_countries": ", ".join(sorted(set(filtered_countries)))  # Include both GB and US if applicable
            }
            albums.append(album_info)

        # Check if there are more results to fetch
        if len(release_groups) < params["limit"]:
            break

        # Increment offset for next batch of results
        offset += params["limit"]

    return albums

def process_artists(input_file, output_file):
    # Read the artist data from the CSV file
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        artists = [{"name": row["Name"], "mbid": row["MBID"]} for row in reader]

    all_albums = []

    # Process each artist
    for artist_index, artist in enumerate(artists, start=1):
        artist_name = artist["name"]
        mbid = artist["mbid"]
        print(f"Processing artist: {artist_name} with MBID: {mbid}")
        albums = get_albums_with_release_countries(mbid)

        for album in albums:
            album["artist_index"] = artist_index
            album["artist_name"] = artist_name

        # Append the results for each artist
        all_albums.extend(albums)

    # Save all the results to a CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["artist_name", "artist_index", "title", "primary_type", "release_year", "artist_mbid", "secondary_types", "release_countries"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for album in all_albums:
            writer.writerow(album)

    print(f"CSV file '{output_file}' has been created successfully.")

if __name__ == "__main__":
    input_file = "artists_mbid.csv"
    output_file = "all_artists_albums.csv"
    process_artists(input_file, output_file)
