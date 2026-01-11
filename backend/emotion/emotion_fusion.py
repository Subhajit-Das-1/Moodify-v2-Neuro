from typing import Dict

# Emotion priority list (used for tie-breaking)
EMOTION_PRIORITY = [
    "happy",
    "excited",
    "calm",
    "neutral",
    "sad",
    "angry"
]

def fuse_emotions(
    face_result: Dict,
    voice_result: Dict,
    face_weight: float = 0.6,
    voice_weight: float = 0.4
):
    """
    Combines face + voice emotion predictions
    """

    # If one modality failed, return the other
    if not face_result["success"]:
        return voice_result

    if not voice_result["success"]:
        return face_result

    # Weighted confidence
    face_score = face_result["confidence"] * face_weight
    voice_score = voice_result["confidence"] * voice_weight

    # Same emotion → boost confidence
    if face_result["emotion"] == voice_result["emotion"]:
        return {
            "success": True,
            "emotion": face_result["emotion"],
            "confidence": min(face_score + voice_score + 0.1, 1.0),
            "source": "face+voice"
        }

    # Different emotions → choose higher weighted confidence
    if face_score > voice_score:
        return {
            "success": True,
            "emotion": face_result["emotion"],
            "confidence": face_score,
            "source": "face-dominant"
        }

    if voice_score > face_score:
        return {
            "success": True,
            "emotion": voice_result["emotion"],
            "confidence": voice_score,
            "source": "voice-dominant"
        }

    # Tie → priority fallback
    for emo in EMOTION_PRIORITY:
        if emo in [face_result["emotion"], voice_result["emotion"]]:
            return {
                "success": True,
                "emotion": emo,
                "confidence": max(face_score, voice_score),
                "source": "priority"
            }

    # Fallback
    return {
        "success": True,
        "emotion": "neutral",
        "confidence": 0.5,
        "source": "fallback"
    }
