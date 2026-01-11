import os
import numpy as np
import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ---------------- CONFIG ----------------
DATASET_PATH = "datasets/fer2013/train"   # ✅ FIXED
IMG_SIZE = 64
EPOCHS = 30
BATCH_SIZE = 64
EMOTIONS = ["angry", "fearful", "happy", "neutral", "sad"]

# ---------------- LOAD DATA ----------------
X, y = [], []

for emotion in EMOTIONS:
    folder = os.path.join(DATASET_PATH, emotion)
    if not os.path.exists(folder):
        raise FileNotFoundError(f"❌ Folder not found: {folder}")

    for img_name in os.listdir(folder):
        img_path = os.path.join(folder, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            continue

        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        X.append(img)
        y.append(emotion)

X = np.array(X, dtype="float32") / 255.0
X = X.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

# ---------------- LABEL ENCODING ----------------
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
y_cat = to_categorical(y_encoded)

# ---------------- TRAIN / VAL SPLIT ----------------
X_train, X_val, y_train, y_val = train_test_split(
    X,
    y_cat,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded   # ✅ FIXED
)

print("✅ Training samples:", X_train.shape)
print("✅ Validation samples:", X_val.shape)

# ---------------- MODEL ----------------
model = Sequential([
    Conv2D(32, (3,3), activation="relu", input_shape=(64,64,1)),
    MaxPooling2D(2,2),
    Dropout(0.25),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(2,2),
    Dropout(0.25),

    Conv2D(128, (3,3), activation="relu"),
    MaxPooling2D(2,2),
    Dropout(0.25),

    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),

    Dense(len(EMOTIONS), activation="softmax")
])

model.compile(
    optimizer=Adam(learning_rate=1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ---------------- TRAIN ----------------
model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE
)

# ---------------- SAVE ----------------
os.makedirs("model", exist_ok=True)

model.save("model/face_emotion_model.h5")
np.save("model/face_emotion_labels.npy", encoder.classes_)

print("✅ Face emotion model trained & saved successfully")
