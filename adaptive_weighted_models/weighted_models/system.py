from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
import pickle

import numpy as np

from .base import Array, WeightedModule
from .drift import DriftConfig, PerformanceDriftDetector
from .meta import MetaWeightingLayer
from .modules import default_modules


@dataclass
class AdaptiveSystemConfig:
    history_size: int = 4000
    retrain_min_samples: int = 120
    auto_retrain: bool = True
    retrain_lookback: int = 1200


class AdaptiveWeightedSystem:
    """End-to-end adaptive weighted model with module ensemble and drift retraining."""

    def __init__(
        self,
        modules: list[WeightedModule] | None = None,
        drift_config: DriftConfig | None = None,
        system_config: AdaptiveSystemConfig | None = None,
    ) -> None:
        self.modules = modules
        self.meta: MetaWeightingLayer | None = None
        self.drift_detector = PerformanceDriftDetector(drift_config)
        self.config = system_config or AdaptiveSystemConfig()

        self._is_fitted = False
        self._X_hist: deque[Array] = deque(maxlen=self.config.history_size)
        self._y_hist: deque[float] = deque(maxlen=self.config.history_size)
        self._Z_hist: deque[Array] = deque(maxlen=self.config.history_size)

    def _default_context(self, X: Array) -> Array:
        missing_frac = np.mean(~np.isfinite(X), axis=1, keepdims=True)
        quality = 1.0 - missing_frac
        filled = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        magnitude = np.mean(np.abs(filled), axis=1, keepdims=True)
        return np.column_stack([quality, magnitude])

    def _resolve_context(self, X: Array, Z: Array | None) -> Array:
        if Z is None:
            return self._default_context(X)
        if Z.shape[0] != X.shape[0]:
            raise ValueError("Z must have the same number of rows as X")
        return Z

    def _stack_module_predictions(self, X: Array) -> Array:
        preds = [m.predict(X) for m in self.modules]
        return np.column_stack(preds)

    def _append_history(self, X: Array, y: Array, Z: Array) -> None:
        for xi, yi, zi in zip(X, y, Z):
            self._X_hist.append(np.asarray(xi, dtype=float).copy())
            self._y_hist.append(float(yi))
            self._Z_hist.append(np.asarray(zi, dtype=float).copy())

    def _history_arrays(self) -> tuple[Array, Array, Array]:
        Xh = np.vstack(self._X_hist) if self._X_hist else np.empty((0, 0), dtype=float)
        yh = np.asarray(self._y_hist, dtype=float)
        Zh = np.vstack(self._Z_hist) if self._Z_hist else np.empty((0, 0), dtype=float)
        return Xh, yh, Zh

    def _recent_history_arrays(self) -> tuple[Array, Array, Array]:
        Xh, yh, Zh = self._history_arrays()
        if Xh.shape[0] == 0:
            return Xh, yh, Zh
        lookback = min(self.config.retrain_lookback, Xh.shape[0])
        return Xh[-lookback:], yh[-lookback:], Zh[-lookback:]

    def fit(self, X: Array, y: Array, Z: Array | None = None) -> None:
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        Zr = self._resolve_context(X, Z)

        if self.modules is None:
            self.modules = default_modules(X.shape[1])

        for module in self.modules:
            module.fit(X, y)

        S = self._stack_module_predictions(X)
        self.meta = MetaWeightingLayer(n_modules=S.shape[1], context_dim=Zr.shape[1])
        self.meta.fit(S, Zr, y, warm_start=False)

        y_fit, _ = self.meta.predict(S, Zr)
        fit_errors = np.abs(y_fit - y).tolist()
        self.drift_detector.prime_baseline(fit_errors)

        self._append_history(X, y, Zr)
        self._is_fitted = True

    def predict(self, X: Array, Z: Array | None = None, return_alphas: bool = False) -> Array | tuple[Array, Array]:
        if not self._is_fitted or self.meta is None:
            raise ValueError("System is not fitted.")

        X = np.asarray(X, dtype=float)
        Zr = self._resolve_context(X, Z)
        S = self._stack_module_predictions(X)
        y_hat, alpha = self.meta.predict(S, Zr)
        if return_alphas:
            return y_hat, alpha
        return y_hat

    def retrain(self, X: Array, y: Array, Z: Array | None = None, warm_start: bool = True) -> None:
        if self.modules is None:
            raise ValueError("Modules are not initialized. Call fit first.")

        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        Zr = self._resolve_context(X, Z)

        for module in self.modules:
            module.retrain(X, y, warm_start=warm_start)

        S = self._stack_module_predictions(X)
        if self.meta is None:
            self.meta = MetaWeightingLayer(n_modules=S.shape[1], context_dim=Zr.shape[1])
            warm = False
        else:
            warm = warm_start
        self.meta.fit(S, Zr, y, warm_start=warm)

        y_fit, _ = self.meta.predict(S, Zr)
        fit_errors = np.abs(y_fit - y).tolist()
        self.drift_detector.prime_baseline(fit_errors)

        self._append_history(X, y, Zr)
        self._is_fitted = True

    def update_and_maybe_retrain(self, X_new: Array, y_new: Array, Z_new: Array | None = None) -> dict[str, float | bool]:
        if not self._is_fitted:
            raise ValueError("System is not fitted.")

        X_new = np.asarray(X_new, dtype=float)
        y_new = np.asarray(y_new, dtype=float)
        Zr = self._resolve_context(X_new, Z_new)

        preds = self.predict(X_new, Zr)
        assert isinstance(preds, np.ndarray)
        mae = float(np.mean(np.abs(preds - y_new)))

        drift_flag = False
        for err in np.abs(preds - y_new):
            if self.drift_detector.update(float(err)):
                drift_flag = True

        self._append_history(X_new, y_new, Zr)

        retrained = False
        if self.config.auto_retrain and drift_flag:
            Xh, yh, Zh = self._recent_history_arrays()
            if Xh.shape[0] >= self.config.retrain_min_samples:
                self.retrain(Xh, yh, Zh, warm_start=True)
                self.drift_detector.reset_baseline_from_recent()
                retrained = True

        return {
            "mae": mae,
            "drift_detected": drift_flag,
            "retrained": retrained,
        }

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: str | Path) -> "AdaptiveWeightedSystem":
        target = Path(path)
        with target.open("rb") as f:
            obj = pickle.load(f)
        if not isinstance(obj, AdaptiveWeightedSystem):
            raise TypeError("Loaded object is not an AdaptiveWeightedSystem.")
        return obj
