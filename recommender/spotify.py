import requests
from recommender.spotify_auth import get_access_token

SEARCH_URL = "https://api.spotify.com/v1/search"

EMOTION_QUERIES = {
    "happy": "happy upbeat pop",
    "sad": "sad acoustic emotional",
    "angry": "angry rock metal",
    "neutral": "chill indie",
    "surprise": "energetic dance"
}

def get_spotify_recommendations(emotion: str, limit: int = 10):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    query = EMOTION_QUERIES.get(emotion, "chill pop")

    params = {
        "q": query,
        "type": "track",
        "limit": limit,
        "market": "US"
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)

    print("🎧 Spotify SEARCH status:", response.status_code)

    response.raise_for_status()

    tracks = response.json()["tracks"]["items"]

    return [
        {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "preview_url": track["preview_url"],
            "spotify_url": track["external_urls"]["spotify"]
        }
        for track in tracks
    ]
