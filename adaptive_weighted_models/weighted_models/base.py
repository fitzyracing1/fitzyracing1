from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


Array = np.ndarray


class WeightedModule(ABC):
    """Interface for all weighted model modules."""

    name: str

    @abstractmethod
    def fit(self, X: Array, y: Array, **kwargs: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: Array, **kwargs: object) -> Array:
        raise NotImplementedError

    @abstractmethod
    def retrain(self, X: Array, y: Array, warm_start: bool = True, **kwargs: object) -> None:
        raise NotImplementedError


class Normalizer:
    """Feature standardizer for stable optimization."""

    def __init__(self) -> None:
        self.mean_: Optional[Array] = None
        self.std_: Optional[Array] = None

    def fit(self, X: Array) -> None:
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0) + 1e-8

    def transform(self, X: Array) -> Array:
        if self.mean_ is None or self.std_ is None:
            raise ValueError("Normalizer is not fitted.")
        return (X - self.mean_) / self.std_

    def fit_transform(self, X: Array) -> Array:
        self.fit(X)
        return self.transform(X)
