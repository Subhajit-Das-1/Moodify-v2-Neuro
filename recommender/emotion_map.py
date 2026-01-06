"""
Emotion → Music Feature Mapping
This is the AI decision layer of Moodify-v2-Neuro
"""

emotion_to_features = {
    "happy": {
        "valence": 0.9,
        "energy": 0.8,
        "danceability": 0.8,
        "tempo": 120
    },
    "sad": {
        "valence": 0.2,
        "energy": 0.3,
        "danceability": 0.4,
        "tempo": 70
    },
    "angry": {
        "valence": 0.3,
        "energy": 0.9,
        "danceability": 0.6,
        "tempo": 140
    },
    "neutral": {
        "valence": 0.5,
        "energy": 0.5,
        "danceability": 0.5,
        "tempo": 100
    },
    "surprise": {
        "valence": 0.7,
        "energy": 0.7,
        "danceability": 0.7,
        "tempo": 130
    }
}
