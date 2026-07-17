import os
import joblib

_BASE_DIR = os.path.dirname(__file__)
_MODEL_PATH = os.path.join(_BASE_DIR, "baseline_model.pkl")
_VECTORIZER_PATH = os.path.join(_BASE_DIR, "baseline_vectorizer.pkl")

_model = joblib.load(_MODEL_PATH)
_vectorizer = joblib.load(_VECTORIZER_PATH)


def predict_risk(text: str):
    """Returns (risk_label, confidence_score) for a given piece of text."""
    vec = _vectorizer.transform([text])
    label = _model.predict(vec)[0]
    proba = _model.predict_proba(vec)[0]
    confidence = float(max(proba))
    return label, confidence