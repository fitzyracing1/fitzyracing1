from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean
from typing import List, Sequence

from crypto_context_ai.api import PricePoint


@dataclass(frozen=True)
class Prediction:
    direction: str
    expected_return: float
    confidence: float
    samples_used: int
    neighbors_used: int
    last_price: float


def _normalize_window(window: Sequence[float]) -> List[float]:
    base = window[0]
    if base == 0:
        return [0.0 for _ in window]
    return [(value / base) - 1.0 for value in window]


def _euclidean_distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((left - right) ** 2 for left, right in zip(a, b)))


def predict_from_price_context(
    prices: Sequence[PricePoint],
    window_size: int = 24,
    neighbors: int = 8,
    flat_threshold: float = 0.002,
) -> Prediction:
    if window_size < 4:
        raise ValueError("window_size must be at least 4.")
    if neighbors < 1:
        raise ValueError("neighbors must be at least 1.")
    if len(prices) <= window_size + 1:
        raise ValueError("Not enough price history for the chosen window_size.")

    values = [point.price for point in prices]
    target_window = _normalize_window(values[-window_size:])

    comparisons = []
    upper_bound = len(values) - window_size - 1
    for start in range(0, upper_bound):
        historical_window = values[start : start + window_size]
        next_price = values[start + window_size]

        normalized = _normalize_window(historical_window)
        distance = _euclidean_distance(target_window, normalized)
        future_return = (next_price / historical_window[-1]) - 1.0
        comparisons.append((distance, future_return))

    if not comparisons:
        raise ValueError("No historical comparison windows were built.")

    comparisons.sort(key=lambda item: item[0])
    nearest = comparisons[: min(neighbors, len(comparisons))]
    returns = [item[1] for item in nearest]
    expected_return = mean(returns)

    if expected_return > flat_threshold:
        direction = "up"
    elif expected_return < -flat_threshold:
        direction = "down"
    else:
        direction = "flat"

    agreement = 0
    for value in returns:
        if direction == "up" and value > 0:
            agreement += 1
        elif direction == "down" and value < 0:
            agreement += 1
        elif direction == "flat" and abs(value) <= flat_threshold:
            agreement += 1

    confidence = agreement / len(returns)

    return Prediction(
        direction=direction,
        expected_return=expected_return,
        confidence=confidence,
        samples_used=len(comparisons),
        neighbors_used=len(nearest),
        last_price=values[-1],
    )
