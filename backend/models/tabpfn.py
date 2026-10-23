"""TabPFN tabular foundation model wrapper (Prior Labs).

TabPFN-3.5 is open-weight and free once you sign the non-commercial license at
platform.priorlabs.ai. It excels at forecasting, classification, and anomaly
detection on small tabular datasets (CSV) - perfect for a "slow and steady"
agent that predicts things so you don't have to.

Falls back to a scikit-learn RandomForest if TabPFN isn't installed, so the
project runs end-to-end with zero extra installs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TabPFNPrediction:
    target_column: str
    prediction: str
    confidence: Optional[float]
    model: str
    local: bool
    cost_usd: float = 0.0


class TabPFNModel:
    def __init__(self):
        self.backend = self._pick_backend()

    def _pick_backend(self) -> str:
        try:
            import tabpfn  # noqa: F401
            return "tabpfn"
        except Exception:
            return "sklearn"

    def predict_from_csv(self, csv_path: str, target_column: str) -> TabPFNPrediction:
        import pandas as pd

        df = pd.read_csv(csv_path)
        if target_column not in df.columns:
            raise ValueError(f"Column '{target_column}' not found in {csv_path}")

        feature_cols = [c for c in df.select_dtypes(include="number").columns if c != target_column]
        if not feature_cols:
            raise ValueError("No numeric feature columns found for prediction.")

        df_clean = df.dropna(subset=[target_column] + feature_cols)
        if df_clean.empty:
            raise ValueError("No clean rows available for training/prediction.")

        X = df_clean[feature_cols]
        y = df_clean[target_column]

        # Use the last row as the "forecast target" - predict what comes next.
        last_row = X.tail(1)
        history_X = X.iloc[:-1]
        history_y = y.iloc[:-1]

        if self.backend == "tabpfn":
            return self._predict_tabpfn(history_X, history_y, last_row, target_column)
        return self._predict_sklearn(history_X, history_y, last_row, target_column)

    def _predict_tabpfn(self, history_X, history_y, last_row, target_column):
        from tabpfn import TabPFNClassifier, TabPFNRegressor

        is_classification = history_y.nunique() <= 10 and history_y.dtype != float
        Model = TabPFNClassifier if is_classification else TabPFNRegressor
        model = Model(device="cpu", n_ensemble_configurations=4)
        model.fit(history_X.values, history_y.values)
        pred = model.predict(last_row.values)
        return TabPFNPrediction(
            target_column=target_column,
            prediction=str(pred[0]),
            confidence=None,
            model="TabPFN-3.5 (Prior Labs)",
            local=True,
            cost_usd=0.0,
        )

    def _predict_sklearn(self, history_X, history_y, last_row, target_column):
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

        is_classification = history_y.nunique() <= 10 and history_y.dtype != float
        Model = RandomForestClassifier if is_classification else RandomForestRegressor
        model = Model(n_estimators=100, random_state=42)
        model.fit(history_X.values, history_y.values)
        pred = model.predict(last_row.values)
        conf = None
        if hasattr(model, "predict_proba"):
            try:
                conf = float(model.predict_proba(last_row.values).max())
            except Exception:
                conf = None
        return TabPFNPrediction(
            target_column=target_column,
            prediction=str(pred[0]),
            confidence=conf,
            model="RandomForest (TabPFN fallback)",
            local=True,
            cost_usd=0.0,
        )


tabpfn = TabPFNModel()
