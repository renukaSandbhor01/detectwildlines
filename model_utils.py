"""
model_utils.py — The ML core of WildLens.

Uses a pretrained MobileNetV2 (trained on ImageNet, 1000 classes, many of
them animals) so there's no need to collect/train on your own dataset.
OpenCV handles reading and resizing the image before it goes to the model.
"""

import cv2
import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import (
    preprocess_input,
    decode_predictions,
)

# Loaded once when the app starts, reused for every prediction.
print("Loading MobileNetV2 model (first run downloads ~14MB of weights)...")
model = MobileNetV2(weights="imagenet")
print("Model ready.")


def predict_image(image_path, top_n=3):
    """
    Reads an image from disk with OpenCV, preprocesses it, and returns
    the top_n predictions as a list of dicts: [{"label": ..., "confidence": ...}, ...]
    """
    # 1. Read image with OpenCV (loads as BGR by default)
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image — file may be corrupted or unsupported.")

    # 2. OpenCV loads BGR, but the model expects RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 3. MobileNetV2 expects 224x224 images
    img = cv2.resize(img, (224, 224))

    # 4. Add batch dimension: model expects shape (1, 224, 224, 3)
    img_array = np.expand_dims(img, axis=0)

    # 5. Scale pixel values the way MobileNetV2 was trained to expect
    img_array = preprocess_input(img_array)

    # 6. Run the prediction
    raw_predictions = model.predict(img_array, verbose=0)

    # 7. Convert raw model output into human-readable labels
    decoded = decode_predictions(raw_predictions, top=top_n)[0]

    results = [
        {"label": label.replace("_", " ").title(), "confidence": round(float(prob) * 100, 2)}
        for (_, label, prob) in decoded
    ]
    return results
