import os
from keras.models import load_model
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "model", "vocalvibe_model.h5")
LABEL_PATH = os.path.join(BASE_DIR, "model", "label_classes.npy")

model = load_model(MODEL_PATH, compile=False)
labels = np.load(LABEL_PATH, allow_pickle=True)
print("MODEL PATH:", MODEL_PATH)
print("MODEL EXISTS:", os.path.exists(MODEL_PATH))
