import cv2
import numpy as np
import os
from fastapi import UploadFile

from ml_model.load_model import model
from ml_model.emotion_labels import emotion_labels

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROTO_PATH = os.path.join(
    BASE_DIR, "models", "dnn_face", "deploy.prototxt"
)

MODEL_PATH = os.path.join(
    BASE_DIR, "models", "dnn_face", "res10_300x300_ssd_iter_140000.caffemodel"
)

face_net = cv2.dnn.readNetFromCaffe(PROTO_PATH, MODEL_PATH)

# ---------------- PREPROCESS ----------------
def preprocess_face(face_img):
    face_img = cv2.resize(face_img, (64, 64))
    face_img = face_img.astype("float32") / 255.0
    face_img = np.reshape(face_img, (1, 64, 64, 1))
    return face_img

# ---------------- MAIN ----------------
def detect_emotion(image: UploadFile):
    """
    Returns:
    {
        emotion: str,
        confidence: float
    }
    """

    try:
        data = image.file.read()
        np_img = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img is None:
            return {"emotion": "neutral", "confidence": 0.0}

        (h, w) = img.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(img, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )

        face_net.setInput(blob)
        detections = face_net.forward()

        for i in range(detections.shape[2]):
            face_confidence = float(detections[0, 0, i, 2])
            print(f"🧪 Face confidence: {face_confidence:.2f}")

            if face_confidence > 0.3:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")

                # Safe clipping
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                face_roi = img[y1:y2, x1:x2]
                if face_roi.size == 0:
                    continue

                gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

                processed_face = preprocess_face(gray_face)
                preds = model.predict(processed_face)[0]

                emotion_index = int(np.argmax(preds))
                emotion = emotion_labels[emotion_index]
                emotion_confidence = float(np.max(preds))

                print(f"🎯 Emotion: {emotion}, Confidence: {emotion_confidence:.2f}")

                return {
                    "emotion": emotion,
                    "confidence": emotion_confidence
                }

        return {"emotion": "neutral", "confidence": 0.0}

    except Exception as e:
        print("❌ Emotion detection error:", e)
        return {"emotion": "neutral", "confidence": 0.0}
