from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from weighted_models import AdaptiveWeightedSystem


def make_dataset(n: int, seed: int = 4) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 8))
    regime = (X[:, 0] > 0).astype(float)
    quality = np.clip(1.0 - 0.2 * np.abs(X[:, 1]), 0.2, 1.0)
    segment = (np.sin(X[:, 2]) + 1.0) / 2.0
    Z = np.column_stack([regime, quality, segment])
    y = 1.6 * X[:, 0] - 0.7 * X[:, 1] + 0.5 * X[:, 2] + 0.3 * regime + rng.normal(0, 0.2, n)
    return X, y, Z


class PersistenceTests(unittest.TestCase):
    def test_save_and_load_roundtrip(self) -> None:
        X, y, Z = make_dataset(500)
        system = AdaptiveWeightedSystem()
        system.fit(X, y, Z)

        probe_X = X[:25]
        probe_Z = Z[:25]
        pred_before = system.predict(probe_X, probe_Z)

        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "weighted_system.pkl"
            system.save(model_path)
            loaded = AdaptiveWeightedSystem.load(model_path)

        pred_after = loaded.predict(probe_X, probe_Z)
        self.assertTrue(np.allclose(pred_before, pred_after, atol=1e-9))


if __name__ == "__main__":
    unittest.main()
