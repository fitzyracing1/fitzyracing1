from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class GravityFeedObservation:
    head_m: float
    gate_open_fraction: float
    density_factor: float
    flow_rate_kg_s: float
    sample_weight: float = 1.0


class GravityFeedWeightedModel:
    """Weighted least-squares model for gravity-feed flow-rate estimation."""

    def __init__(self) -> None:
        self.coefficients = [0.0, 0.0, 0.0, 0.0]
        self.is_fitted = False

    @staticmethod
    def _features(obs: GravityFeedObservation) -> list[float]:
        if obs.head_m < 0:
            raise ValueError("head_m must be non-negative")
        if not 0.0 <= obs.gate_open_fraction <= 1.0:
            raise ValueError("gate_open_fraction must be in [0.0, 1.0]")
        if obs.sample_weight <= 0:
            raise ValueError("sample_weight must be positive")
        return [1.0, math.sqrt(obs.head_m), obs.gate_open_fraction, obs.density_factor]

    def fit(self, observations: list[GravityFeedObservation]) -> None:
        if len(observations) < 4:
            raise ValueError("at least 4 observations are required")

        xtwx = [[0.0 for _ in range(4)] for _ in range(4)]
        xtwy = [0.0 for _ in range(4)]

        for obs in observations:
            x = self._features(obs)
            w = obs.sample_weight
            y = obs.flow_rate_kg_s
            for i in range(4):
                xtwy[i] += w * x[i] * y
                for j in range(4):
                    xtwx[i][j] += w * x[i] * x[j]

        self.coefficients = self._solve_4x4(xtwx, xtwy)
        self.is_fitted = True

    def predict(self, head_m: float, gate_open_fraction: float, density_factor: float) -> float:
        if not self.is_fitted:
            raise RuntimeError("model must be fitted before prediction")

        obs = GravityFeedObservation(
            head_m=head_m,
            gate_open_fraction=gate_open_fraction,
            density_factor=density_factor,
            flow_rate_kg_s=0.0,
            sample_weight=1.0,
        )
        x = self._features(obs)
        return sum(c * f for c, f in zip(self.coefficients, x))

    @staticmethod
    def _solve_4x4(a: list[list[float]], b: list[float]) -> list[float]:
        # Solve Ax=b via Gaussian elimination with partial pivoting.
        n = 4
        aug = [row[:] + [rhs] for row, rhs in zip(a, b)]

        for col in range(n):
            pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
            if abs(aug[pivot_row][col]) < 1e-12:
                raise ValueError("singular system; observations are not informative enough")
            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

            pivot = aug[col][col]
            for j in range(col, n + 1):
                aug[col][j] /= pivot

            for r in range(n):
                if r == col:
                    continue
                factor = aug[r][col]
                for j in range(col, n + 1):
                    aug[r][j] -= factor * aug[col][j]

        return [aug[i][n] for i in range(n)]
