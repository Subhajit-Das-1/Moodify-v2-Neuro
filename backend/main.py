from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from emotion.face_emotion import detect_emotion
from emotion.voice_emotion import detect_voice_emotion
from emotion.emotion_fusion import fuse_emotions
from recommender.spotify import get_spotify_recommendations
from recommender.spotify_auth import get_access_token

# ---------------- Logging Setup ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- App Init ----------------
app = FastAPI(title="Moodify-v2-Neuro Backend")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔒 restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "Moodify-v2-Neuro backend running 🚀"}

# ---------------- SPOTIFY AUTH TEST ----------------
@app.get("/spotify-test")
def spotify_test():
    token = get_access_token()
    return {
        "success": True,
        "message": "Spotify auth working ✅",
        "token_length": len(token)
    }

# ======================================================
# 🎭 FACE EMOTION + SONGS
# ======================================================
@app.post("/analyze-emotion")
async def analyze_emotion(image: UploadFile = File(...)):
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format: {image.content_type}"
        )

    result = detect_emotion(image)

    if not result.get("success"):
        return {
            "success": False,
            "message": "Face not detected"
        }

    songs = get_spotify_recommendations(result["emotion"])

    logging.info(
        f"FACE emotion: {result['emotion']} "
        f"(confidence={result['confidence']:.2f})"
    )

    return {
        "success": True,
        "source": "face",
        "emotion": result["emotion"],
        "confidence": result["confidence"],
        "songs": songs
    }

# ======================================================
# 🎤 VOICE EMOTION + SONGS
# ======================================================
@app.post("/analyze-voice")
async def analyze_voice(audio: UploadFile = File(...)):
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {audio.content_type}"
        )

    result = detect_voice_emotion(audio)

    if not result.get("success"):
        return {
            "success": False,
            "message": "Voice emotion detection failed"
        }

    songs = get_spotify_recommendations(result["emotion"])

    logging.info(
        f"VOICE emotion: {result['emotion']} "
        f"(confidence={result['confidence']:.2f})"
    )

    return {
        "success": True,
        "source": "voice",
        "emotion": result["emotion"],
        "confidence": result["confidence"],
        "songs": songs
    }

# ======================================================
# 🔥 FUSED EMOTION + SONGS (OPTIONAL)
# ======================================================
@app.post("/analyze-fused-emotion")
async def analyze_fused_emotion(
    image: UploadFile = File(...),
    audio: UploadFile = File(...)
):
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format")

    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio format")

    # Reset file pointers
    image.file.seek(0)
    audio.file.seek(0)

    face_result = detect_emotion(image)

    audio.file.seek(0)
    voice_result = detect_voice_emotion(audio)

    fused = fuse_emotions(face_result, voice_result)

    songs = get_spotify_recommendations(fused["emotion"])

    logging.info(
        f"FUSED emotion: {fused['emotion']} "
        f"(confidence={fused['confidence']:.2f}, source={fused['source']})"
    )

    return {
        "success": True,
        "source": fused["source"],
        "emotion": fused["emotion"],
        "confidence": fused["confidence"],
        "songs": songs
    }

# ======================================================
# 🎵 DIRECT MUSIC REQUEST (MANUAL)
# ======================================================
@app.get("/recommend")
def recommend_music(emotion: str = "neutral"):
    try:
        tracks = get_spotify_recommendations(emotion)
        return {
            "success": True,
            "emotion": emotion,
            "songs": tracks
        }
    except Exception as e:
        logging.error(f"Spotify recommendation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Spotify recommendation failed"
        )
