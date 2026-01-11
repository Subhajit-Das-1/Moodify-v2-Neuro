import cv2
import numpy as np
import os
from fastapi import UploadFile
from tensorflow.keras.models import load_model

# ================= BASE PATH =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ================= FACE DETECTOR (DNN) =================
PROTO_PATH = os.path.join(
    BASE_DIR, "models", "dnn_face", "deploy.prototxt"
)

DNN_MODEL_PATH = os.path.join(
    BASE_DIR, "models", "dnn_face", "res10_300x300_ssd_iter_140000.caffemodel"
)

face_net = cv2.dnn.readNetFromCaffe(PROTO_PATH, DNN_MODEL_PATH)

print("🙂 Face detector loaded (DNN)")
print("📁 DNN model:", DNN_MODEL_PATH)

# ================= FACE EMOTION MODEL =================
FACE_MODEL_PATH = os.path.join(
    BASE_DIR, "model", "face_emotion_model.h5"
)

FACE_LABEL_PATH = os.path.join(
    BASE_DIR, "model", "face_emotion_labels.npy"
)

print("🧠 Loading FACE emotion model from:", FACE_MODEL_PATH)
print("MODEL EXISTS:", os.path.exists(FACE_MODEL_PATH))

face_emotion_model = load_model(FACE_MODEL_PATH, compile=False)
emotion_labels = np.load(FACE_LABEL_PATH)

print("🧠 Face emotion model loaded")
print("🏷️ Labels:", emotion_labels)

# ================= PREPROCESS =================
def preprocess_face(face_img):
    face_img = cv2.resize(face_img, (64, 64))
    face_img = face_img.astype("float32") / 255.0
    face_img = np.reshape(face_img, (1, 64, 64, 1))
    return face_img

# ================= MAIN API =================
def detect_emotion(image: UploadFile):
    """
    Detects face and predicts facial emotion
    Returns:
    {
        success: bool,
        emotion: str,
        confidence: float,
        face_detected: bool
    }
    """

    try:
        data = image.file.read()
        np_img = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img is None:
            return {
                "success": False,
                "emotion": "neutral",
                "confidence": 0.0,
                "face_detected": False
            }

        (h, w) = img.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(img, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )

        face_net.setInput(blob)
        detections = face_net.forward()

        best_face = None
        best_conf = 0.0

        # ---------- Find strongest face ----------
        for i in range(detections.shape[2]):
            conf = float(detections[0, 0, i, 2])

            if conf > best_conf and conf > 0.4:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")

                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                face_roi = img[y1:y2, x1:x2]

                if face_roi.size > 0:
                    best_face = face_roi
                    best_conf = conf

        if best_face is None:
            return {
                "success": False,
                "emotion": "neutral",
                "confidence": 0.0,
                "face_detected": False
            }

        print(f"🧪 Face detected (confidence={best_conf:.2f})")

        # ---------- Emotion Prediction ----------
        gray_face = cv2.cvtColor(best_face, cv2.COLOR_BGR2GRAY)
        processed_face = preprocess_face(gray_face)

        preds = face_emotion_model.predict(processed_face, verbose=0)[0]

        emotion_index = int(np.argmax(preds))
        emotion = str(emotion_labels[emotion_index])
        emotion_conf = float(preds[emotion_index])

        print(f"🎯 Face emotion: {emotion} ({emotion_conf:.2f})")

        return {
            "success": True,
            "emotion": emotion,
            "confidence": emotion_conf,
            "face_detected": True
        }

    except Exception as e:
        print("❌ Face emotion error:", e)
        return {
            "success": False,
            "emotion": "neutral",
            "confidence": 0.0,
            "face_detected": False
        }
