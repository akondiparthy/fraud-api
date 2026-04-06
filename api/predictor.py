import pickle
import shap
import numpy as np
import pandas as pd
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from model.features import engineer_features

MODEL_PATH  = Path(__file__).parent.parent / "model/artifacts/model.pkl"
SCALER_PATH = Path(__file__).parent.parent / "model/artifacts/scaler.pkl"

FEATURE_NAMES = [f"V{i}" for i in range(1, 29)] + [
    "amount_log", "hour_of_day", "is_night",
    "is_round_amount", "is_micro_txn", "is_high_value"
]

class FraudPredictor:
    def __init__(self):
        print("Loading model artifacts...")
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)
        with open(SCALER_PATH, "rb") as f:
            self.scaler = pickle.load(f)
        self.explainer = shap.TreeExplainer(self.model)
        print("✅ Model ready!")

    def _decision(self, score: float) -> str:
        if score < 0.3:   return "approved"
        if score < 0.7:   return "review"
        return "blocked"

    def _top_factors(self, shap_vals: np.ndarray) -> list[str]:
        pairs = sorted(
            zip(FEATURE_NAMES, np.abs(shap_vals)),
            key=lambda x: x[1],
            reverse=True
        )
        return [name for name, _ in pairs[:3]]

    def predict(self, txn: dict) -> dict:
        start = time.time()

        raw = pd.DataFrame([{
            "Time":   txn["time_seconds"],
            "Amount": txn["amount"],
            **{f"V{i}": txn[f"V{i}"] for i in range(1, 29)}
        }])

        features = engineer_features(raw)
        scaled   = self.scaler.transform(features)

        score = float(self.model.predict_proba(scaled)[0][1])

        shap_vals = self.explainer.shap_values(scaled)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[1]
        factors = self._top_factors(shap_vals[0])

        decision = self._decision(score)

        return {
            "fraud_score":       round(score, 4),
            "decision":          decision,
            "top_risk_factors":  factors,
            "explanation":       (
                f"Transaction scored {score:.1%} fraud probability. "
                f"Decision: {decision.upper()}. "
                f"Top signals: {', '.join(factors)}."
            ),
            "latency_ms":        round((time.time() - start) * 1000, 2),
            "model_version":     "v1.0"
        }

predictor = FraudPredictor()