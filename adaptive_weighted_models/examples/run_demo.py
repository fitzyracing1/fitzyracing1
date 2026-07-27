from __future__ import annotations

import numpy as np

from weighted_models import AdaptiveSystemConfig, AdaptiveWeightedSystem
from weighted_models.drift import DriftConfig


def make_dataset(n: int, seed: int = 42, drift: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 8))

    # Context z: regime, data-quality proxy, segment id (continuous embedding)
    regime = (X[:, 0] > 0).astype(float)
    quality = np.clip(1.0 - 0.2 * np.abs(X[:, 1]), 0.2, 1.0)
    segment = (np.sin(X[:, 2]) + 1.0) / 2.0
    Z = np.column_stack([regime, quality, segment])

    # Ground truth changes under drift to trigger performance degradation.
    if not drift:
        y = 1.8 * X[:, 0] - 0.8 * X[:, 1] + 0.6 * X[:, 2] + 0.4 * regime + rng.normal(0, 0.2, n)
    else:
        y = -1.1 * X[:, 0] + 1.4 * X[:, 3] - 0.5 * X[:, 4] + 0.7 * (1.0 - regime) + rng.normal(0, 0.25, n)

    return X, y, Z


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean((y_true - y_pred) ** 2))


def main() -> None:
    X_train, y_train, Z_train = make_dataset(900, seed=11, drift=False)
    X_test, y_test, Z_test = make_dataset(300, seed=77, drift=False)

    system = AdaptiveWeightedSystem(
        drift_config=DriftConfig(window_size=40, min_samples=10, relative_increase_threshold=0.08),
        system_config=AdaptiveSystemConfig(retrain_min_samples=100, retrain_lookback=900, auto_retrain=True),
    )
    system.fit(X_train, y_train, Z_train)

    pred_before = system.predict(X_test, Z_test)
    assert isinstance(pred_before, np.ndarray)
    print(f"Initial test MSE: {mse(y_test, pred_before):.4f}")

    # Introduce drift data in mini-batches.
    X_drift, y_drift, Z_drift = make_dataset(400, seed=123, drift=True)
    batch_size = 40
    drift_events = 0
    retrain_events = 0

    for i in range(0, X_drift.shape[0], batch_size):
        xb = X_drift[i : i + batch_size]
        yb = y_drift[i : i + batch_size]
        zb = Z_drift[i : i + batch_size]

        report = system.update_and_maybe_retrain(xb, yb, zb)
        if report["drift_detected"]:
            drift_events += 1
        if report["retrained"]:
            retrain_events += 1

    pred_after = system.predict(X_drift, Z_drift)
    assert isinstance(pred_after, np.ndarray)

    system.save("artifacts/adaptive_weighted_system.pkl")
    restored = AdaptiveWeightedSystem.load("artifacts/adaptive_weighted_system.pkl")
    restored_pred = restored.predict(X_drift, Z_drift)
    assert isinstance(restored_pred, np.ndarray)

    print(f"Drift batches with alert: {drift_events}")
    print(f"Auto-retrain events: {retrain_events}")
    print(f"Post-drift MSE after adaptation: {mse(y_drift, pred_after):.4f}")
    print(f"Persistence roundtrip max diff: {np.max(np.abs(restored_pred - pred_after)):.10f}")


if __name__ == "__main__":
    main()
