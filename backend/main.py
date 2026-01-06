from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from emotion.face_emotion import detect_emotion
from recommender.spotify import get_spotify_recommendations
from recommender.spotify_auth import get_access_token  # ✅ ADD THIS

# ---------------- Logging Setup ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Moodify-v2-Neuro Backend")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "Moodify-v2-Neuro backend running"}

# ---------------- SPOTIFY AUTH TEST ----------------
@app.get("/spotify-test")
def spotify_test():
    """
    Test Spotify OAuth (Client Credentials Flow)
    """
    token = get_access_token()
    return {
        "message": "Spotify auth working ✅",
        "token_length": len(token)
    }

# ---------------- EMOTION ANALYSIS ----------------
@app.post("/analyze-emotion")
async def analyze_emotion(image: UploadFile = File(...)):

    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed"
        )

    try:
        emotion = detect_emotion(image)
        logging.info(f"Emotion detected: {emotion}")

        return {
            "success": True,
            "emotion": emotion
        }

    except Exception as e:
        logging.error(f"Error during emotion analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# ---------------- MUSIC RECOMMENDATION ----------------
@app.get("/recommend")
def recommend_music(emotion: str = "neutral"):
    try:
        tracks = get_spotify_recommendations(emotion)
        return {
            "emotion": emotion,
            "recommendations": tracks
        }
    except Exception as e:
        logging.error(f"Spotify recommendation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Spotify recommendation failed"
        )
