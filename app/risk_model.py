import os
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

_BASE_DIR = os.path.dirname(__file__)
_MAX_LEN = 100  # must match what we used during training

# Load everything once when the app starts, not on every request
_model = load_model(os.path.join(_BASE_DIR, "keras_model.h5"))

with open(os.path.join(_BASE_DIR, "tokenizer.pkl"), "rb") as f:
    _tokenizer = pickle.load(f)

with open(os.path.join(_BASE_DIR, "label_encoder.pkl"), "rb") as f:
    _label_encoder = pickle.load(f)


def predict_risk(text: str):
    """Returns (risk_label, confidence_score) for a given piece of text."""
    seq = _tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=_MAX_LEN, padding="post", truncating="post")

    probs = _model.predict(padded, verbose=0)[0]
    predicted_index = int(np.argmax(probs))
    label = _label_encoder.inverse_transform([predicted_index])[0]
    confidence = float(probs[predicted_index])

    return label, confidence