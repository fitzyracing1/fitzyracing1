from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass
class DriftConfig:
    window_size: int = 80
    min_samples: int = 20
    relative_increase_threshold: float = 0.15


class PerformanceDriftDetector:
    """Flags drift when recent error rises relative to baseline."""

    def __init__(self, config: DriftConfig | None = None) -> None:
        self.config = config or DriftConfig()
        self.baseline_errors: deque[float] = deque(maxlen=self.config.window_size)
        self.recent_errors: deque[float] = deque(maxlen=self.config.window_size)

    def update(self, error: float) -> bool:
        self.recent_errors.append(float(error))
        if len(self.baseline_errors) < self.config.window_size:
            self.baseline_errors.append(float(error))
            return False
        return self.has_drift()

    def has_drift(self) -> bool:
        if len(self.recent_errors) < self.config.min_samples:
            return False
        baseline = sum(self.baseline_errors) / len(self.baseline_errors)
        recent = sum(self.recent_errors) / len(self.recent_errors)
        if baseline <= 1e-8:
            return recent > 0.0
        return (recent - baseline) / baseline >= self.config.relative_increase_threshold

    def prime_baseline(self, errors: list[float] | tuple[float, ...]) -> None:
        self.baseline_errors.clear()
        self.recent_errors.clear()
        for err in errors[-self.config.window_size :]:
            self.baseline_errors.append(float(err))

    def reset_baseline_from_recent(self) -> None:
        self.baseline_errors.clear()
        self.baseline_errors.extend(self.recent_errors)
