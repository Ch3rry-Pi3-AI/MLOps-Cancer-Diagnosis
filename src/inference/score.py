import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL = None


def init():
    global MODEL
    model_dir = Path(
        # Azure ML sets AZUREML_MODEL_DIR for online endpoints
        # fallback to local "model" folder for dev testing
        # path can contain nested model artifact
        Path(__file__).resolve().parents[2] / "model"
    )
    azure_model_dir = Path(
        # environment variable is optional in local runs
        # avoid KeyError for local testing
        __import__("os").environ.get("AZUREML_MODEL_DIR", str(model_dir))
    )
    model_path = azure_model_dir / "model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")
    MODEL = joblib.load(model_path)


def run(raw_data):
    if MODEL is None:
        init()

    if isinstance(raw_data, str):
        payload = json.loads(raw_data)
    else:
        payload = raw_data

    records = payload.get("data") or payload.get("inputs") or payload.get("instances")
    if records is None:
        raise ValueError("Request must include 'data', 'inputs', or 'instances'.")

    df = pd.DataFrame(records)
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    preds = MODEL.predict(df)
    probs = MODEL.predict_proba(df)[:, 1]

    return {
        "predictions": preds.tolist(),
        "probabilities": np.round(probs, 6).tolist(),
    }
