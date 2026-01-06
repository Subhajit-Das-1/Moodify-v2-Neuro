from tensorflow.keras.models import load_model

MODEL_PATH = "ml_model/emotion_model.h5"

# Load model for inference only (no optimizer)
model = load_model(MODEL_PATH, compile=False)
