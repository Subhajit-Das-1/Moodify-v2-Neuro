
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from features.extract_features import load_data

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.utils import to_categorical

# 👇 adjust import path if needed
from features.extract_features import load_data


# ---------- Ensure model directory exists ----------
MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)


# ---------- Load data ----------
X, y = load_data()

print("Feature shape:", X.shape)
print("Labels shape:", y.shape)

unique_labels, counts = np.unique(y, return_counts=True)
print("\nEmotion distribution:")
for label, count in zip(unique_labels, counts):
    print(f"{label}: {count}")


# ---------- Encode labels ----------
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)


# ---------- Train-test split ----------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_categorical,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ---------- Build model ----------
model = Sequential([
    Dense(256, activation="relu", input_shape=(X.shape[1],)),
    Dropout(0.4),

    Dense(128, activation="relu"),
    Dropout(0.3),

    Dense(y_categorical.shape[1], activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)


# ---------- Train ----------
model.fit(
    X_train,
    y_train,
    validation_data=(X_test, y_test),
    epochs=40,
    batch_size=32
)


# ---------- Save model & labels ----------
model.save(os.path.join(MODEL_DIR, "vocalvibe_model.h5"))
np.save(os.path.join(MODEL_DIR, "label_classes.npy"), encoder.classes_)

print("\n✅ Model training completed successfully")
print("📁 Saved:")
print(" - model/vocalvibe_model.h5")
print(" - model/label_classes.npy")
