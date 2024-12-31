import requests
import base64
import csv
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials loaded from the environment
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')

# Function to refresh the access token using the refresh token
def refresh_access_token():
    """Refresh the access token using the refresh token."""
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        new_token = response.json()['access_token']
        print(f"New access token: {new_token}")
        return new_token
    else:
        print(f"Error refreshing token: {response.status_code}, {response.text}")
        return None


# Function to get the current access token
def get_access_token():
    """Get a valid access token."""
    access_token = refresh_access_token()
    if not access_token:
        raise Exception("Unable to get access token")
    return access_token


# Function to get top artists with pagination
def get_top_artists(limit=50, total_artists=100):
    """Get the user's top artists over the long term."""
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    all_artists = []
    for offset in range(0, total_artists, limit):
        params = {
            'limit': limit,  # Fetch up to 50 artists per request
            'offset': offset,  # Start position for fetching artists
            'time_range': 'long_term'  # Long-term time range
        }
        response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers, params=params)

        if response.status_code == 200:
            top_artists = response.json()
            all_artists.extend(top_artists['items'])
        else:
            print(f"Error fetching top artists: {response.status_code}, {response.text}")
            break

    return all_artists


# Function to export artists to CSV
def export_artists_to_csv(artists, filename='top_100_artists.csv'):
    """Export the top artists to a CSV file."""
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Name', 'ID', 'Genres', 'Popularity', 'Followers', 'URI', 'Profile Image'])
        writer.writeheader()
        for artist in artists:
            writer.writerow({
                'Name': artist['name'],
                'ID': artist['id'],
                'Genres': ', '.join(artist['genres']),
                'Popularity': artist['popularity'],
                'Followers': artist['followers']['total'],
                'URI': artist['uri'],
                'Profile Image': artist['images'][0]['url'] if artist['images'] else 'N/A'
            })
    print(f"Artists have been exported to {filename}")


# Main execution
if __name__ == "__main__":
    try:
        top_artists = get_top_artists(total_artists=100)  # Get up to 100 artists
        if top_artists:
            export_artists_to_csv(top_artists, filename='top_100_artists.csv')
    except Exception as e:
        print(f"Error: {e}")
