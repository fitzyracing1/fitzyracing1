from __future__ import annotations

import unittest

import numpy as np

from weighted_models import AdaptiveSystemConfig, AdaptiveWeightedSystem
from weighted_models.drift import DriftConfig


def make_dataset(n: int, seed: int = 10, drift: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 8))
    regime = (X[:, 0] > 0).astype(float)
    quality = np.clip(1.0 - 0.2 * np.abs(X[:, 1]), 0.2, 1.0)
    segment = (np.sin(X[:, 2]) + 1.0) / 2.0
    Z = np.column_stack([regime, quality, segment])

    if not drift:
        y = 1.6 * X[:, 0] - 0.7 * X[:, 1] + 0.5 * X[:, 2] + 0.3 * regime + rng.normal(0, 0.2, n)
    else:
        y = -1.2 * X[:, 0] + 1.1 * X[:, 3] - 0.6 * X[:, 4] + 0.6 * (1.0 - regime) + rng.normal(0, 0.25, n)
    return X, y, Z


class AdaptiveSystemTests(unittest.TestCase):
    def test_predict_and_alpha_shapes(self) -> None:
        X, y, Z = make_dataset(300, seed=1, drift=False)
        system = AdaptiveWeightedSystem()
        system.fit(X, y, Z)

        pred, alpha = system.predict(X[:40], Z[:40], return_alphas=True)
        self.assertEqual(pred.shape, (40,))
        self.assertEqual(alpha.shape[0], 40)
        self.assertTrue(np.allclose(alpha.sum(axis=1), 1.0, atol=1e-6))

    def test_warm_start_retrain_changes_predictions(self) -> None:
        X, y, Z = make_dataset(400, seed=2, drift=False)
        X_new, y_new, Z_new = make_dataset(150, seed=3, drift=True)

        system = AdaptiveWeightedSystem()
        system.fit(X, y, Z)
        pred_before = system.predict(X_new, Z_new)

        system.retrain(X_new, y_new, Z_new, warm_start=True)
        pred_after = system.predict(X_new, Z_new)

        delta = float(np.mean(np.abs(pred_after - pred_before)))
        self.assertGreater(delta, 0.01)

    def test_drift_triggers_auto_retrain(self) -> None:
        X, y, Z = make_dataset(700, seed=11, drift=False)
        X_drift, y_drift, Z_drift = make_dataset(120, seed=99, drift=True)

        system = AdaptiveWeightedSystem(
            drift_config=DriftConfig(window_size=30, min_samples=8, relative_increase_threshold=0.08),
            system_config=AdaptiveSystemConfig(retrain_min_samples=80, retrain_lookback=500, auto_retrain=True),
        )
        system.fit(X, y, Z)
        report = system.update_and_maybe_retrain(X_drift, y_drift, Z_drift)

        self.assertTrue(bool(report["drift_detected"]))
        self.assertTrue(bool(report["retrained"]))


if __name__ == "__main__":
    unittest.main()
