import io
import numpy as np
import librosa
import soundfile as sf
from fastapi import UploadFile
from scipy.stats import entropy

from ml_model.load_model import model, labels

TARGET_SR = 22050
N_MFCC = 40
MIN_DURATION = 2.5

# ---------- MEMORY (prevents sticking) ----------
LAST_EMOTION = None
STREAK = 0
MAX_STREAK = 3   # after this → neutral allowed


# ---------- FEATURE EXTRACTION ----------
def extract_features(audio, sr):
    audio = audio / (np.max(np.abs(audio)) + 1e-6)

    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=N_MFCC)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)

    return np.hstack([
        np.mean(mfcc, axis=1),
        np.std(mfcc, axis=1),
        np.mean(delta, axis=1),
        np.mean(delta2, axis=1)
    ])


# ---------- STEERING ----------
def steer_emotion(preds, audio, sr):
    global LAST_EMOTION, STREAK

    rms = librosa.feature.rms(y=audio)[0]
    rms_mean, rms_std = np.mean(rms), np.std(rms)

    f0, _, _ = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7")
    )
    f0 = np.nan_to_num(f0)
    pitch_mean, pitch_std = np.mean(f0), np.std(f0)

    centroid = np.mean(
        librosa.feature.spectral_centroid(y=audio, sr=sr)
    )

    print(
        f"🎚️ RMS μ={rms_mean:.4f} σ={rms_std:.4f} | "
        f"Pitch μ={pitch_mean:.1f} σ={pitch_std:.1f} | "
        f"Centroid={centroid:.0f}"
    )

    probs = preds.copy()
    label_list = labels.tolist()

    # ---------- LOW CONFIDENCE ----------
    ent = entropy(probs)
    if ent > 1.5:
        print("⚠️ High uncertainty → neutral")
        emotion = "neutral"
    else:
        emotion = label_list[int(np.argmax(probs))]

    # ---------- SOFT RULES ----------
    if rms_mean < 0.03 and pitch_mean < 130:
        emotion = "sad"

    elif pitch_mean > 180 and centroid > 2500:
        emotion = "happy"

    elif pitch_std > 80 and rms_std > 0.05 and rms_mean > 0.05:
        emotion = "angry"

    elif pitch_mean > 200 and rms_mean < 0.04:
        emotion = "fearful"

    # ---------- STICKINESS CONTROL ----------
    if emotion == LAST_EMOTION:
        STREAK += 1
        if STREAK >= MAX_STREAK:
            print("🔄 Emotion stuck → reset to neutral")
            emotion = "neutral"
            STREAK = 0
    else:
        STREAK = 0

    LAST_EMOTION = emotion
    confidence = float(np.max(probs))

    return emotion, confidence


# ---------- API ----------
def detect_voice_emotion(audio_file: UploadFile):
    try:
        audio_bytes = audio_file.file.read()

        audio, sr = sf.read(io.BytesIO(audio_bytes))
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        if sr != TARGET_SR:
            audio = librosa.resample(audio, sr, TARGET_SR)
            sr = TARGET_SR

        duration = len(audio) / sr
        print(f"🎧 Duration: {duration:.2f}s")

        if duration < MIN_DURATION:
            return {
                "success": False,
                "emotion": "neutral",
                "confidence": 0.0
            }

        features = extract_features(audio, sr).reshape(1, -1)
        preds = model.predict(features, verbose=0)[0]

        print("📊 Model preds:", preds)

        emotion, confidence = steer_emotion(preds, audio, sr)

        print(f"🎯 Final voice emotion: {emotion}")

        return {
            "success": True,
            "emotion": emotion,
            "confidence": confidence
        }

    except Exception as e:
        print("❌ Voice emotion error:", e)
        return {
            "success": False,
            "emotion": "neutral",
            "confidence": 0.0
        }
