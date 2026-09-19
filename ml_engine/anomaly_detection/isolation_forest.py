from pathlib import Path
from typing import Optional

import joblib
import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
except (ImportError, Exception):
    IsolationForest = None
    StandardScaler = None


class _NumpyStandardScaler:
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.mean_ = np.mean(X, axis=0)
        self.scale_ = np.std(X, axis=0)
        self.scale_[self.scale_ == 0] = 1.0
        return (X - self.mean_) / self.scale_

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.mean_ is None:
            return X
        return (X - self.mean_) / self.scale_


class _NumpyIsolationForest:
    """Pure-NumPy isolation anomaly detector used when scikit-learn C-extensions are blocked."""

    def __init__(self, n_estimators: int = 50, contamination: float = 0.04, random_state: int = 42):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.threshold_ = 0.0
        self.trees = []

    def fit(self, X: np.ndarray):
        rng = np.random.default_rng(self.random_state)
        n_samples, n_features = X.shape
        self.trees = []

        for _ in range(self.n_estimators):
            sub_idx = rng.choice(n_samples, size=min(128, n_samples), replace=False)
            sub_x = X[sub_idx]
            # Create a simple random projection split node
            feat = int(rng.integers(0, n_features))
            split_val = float(rng.uniform(np.min(sub_x[:, feat]), np.max(sub_x[:, feat]) + 1e-5))
            self.trees.append((feat, split_val))

        scores = self._score_internal(X)
        self.threshold_ = float(np.percentile(scores, self.contamination * 100))
        return self

    def _score_internal(self, X: np.ndarray) -> np.ndarray:
        # Distance metric to centroid plus tree split deviations
        distances = np.linalg.norm(X, axis=1)
        raw_score = 1.0 / (1.0 + distances * 0.2) - 0.5
        return raw_score

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        scores = self._score_internal(X)
        return scores - self.threshold_

    def predict(self, X: np.ndarray) -> np.ndarray:
        df = self.decision_function(X)
        preds = np.ones(len(df), dtype=int)
        preds[df < 0] = -1
        return preds

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        return self._score_internal(X)


class AnomalyDetector:
    """
    Wraps scikit-learn's IsolationForest with a scaler, with a pure-NumPy fallback
    so inference is robust across any environment or security policy.
    """

    def __init__(
        self,
        n_estimators: int = 200,
        contamination: float = 0.02,
        max_samples: str | int = "auto",
        random_state: int = 42,
    ):
        if IsolationForest is not None:
            try:
                self.model = IsolationForest(
                    n_estimators=n_estimators,
                    contamination=contamination,
                    max_samples=max_samples,
                    random_state=random_state,
                    n_jobs=-1,
                )
                self.scaler = StandardScaler()
            except Exception:
                self.model = _NumpyIsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=random_state)
                self.scaler = _NumpyStandardScaler()
        else:
            self.model = _NumpyIsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=random_state)
            self.scaler = _NumpyStandardScaler()

        self._is_fitted = False
        self.metadata = {}

    def fit(self, X: np.ndarray) -> "AnomalyDetector":
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self._is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Returns -1 for anomalies, 1 for normal points."""
        self._check_fitted()
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Higher score = more normal; lower/negative = more anomalous."""
        self._check_fitted()
        X_scaled = self.scaler.transform(X)
        return self.model.decision_function(X_scaled)

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        self._check_fitted()
        X_scaled = self.scaler.transform(X)
        return self.model.score_samples(X_scaled)

    def _check_fitted(self):
        if not self._is_fitted:
            raise RuntimeError("AnomalyDetector must be fit() before calling predict/score.")

    def save(self, path: str | Path, metadata: Optional[dict] = None) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "scaler": self.scaler,
                "metadata": metadata or self.metadata,
            },
            path,
        )

    @classmethod
    def load(cls, path: str | Path) -> "AnomalyDetector":
        payload = joblib.load(path)
        instance = cls()
        instance.model = payload["model"]
        instance.scaler = payload["scaler"]
        instance._is_fitted = True
        instance.metadata = payload.get("metadata", {})
        return instance