from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .base import Array


def _softmax(logits: Array) -> Array:
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=1, keepdims=True)


@dataclass
class MetaWeightingLayer:
    """Context-conditioned softmax weighting over module predictions."""

    n_modules: int
    context_dim: int
    lr: float = 0.05
    l2: float = 1e-4
    epochs: int = 200

    def __post_init__(self) -> None:
        self.W = np.zeros((self.n_modules, self.context_dim), dtype=float)
        self.b = np.zeros(self.n_modules, dtype=float)

    def logits(self, Z: Array) -> Array:
        return Z @ self.W.T + self.b

    def alphas(self, Z: Array) -> Array:
        return _softmax(self.logits(Z))

    def predict(self, S: Array, Z: Array) -> tuple[Array, Array]:
        alpha = self.alphas(Z)
        y_hat = np.sum(alpha * S, axis=1)
        return y_hat, alpha

    def fit(self, S: Array, Z: Array, y: Array, warm_start: bool = True) -> None:
        if S.ndim != 2 or Z.ndim != 2:
            raise ValueError("S and Z must be 2D arrays")
        if S.shape[0] != Z.shape[0] or S.shape[0] != y.shape[0]:
            raise ValueError("S, Z, and y must have matching rows")

        if not warm_start:
            self.W.fill(0.0)
            self.b.fill(0.0)

        n = S.shape[0]
        for _ in range(self.epochs):
            logits = self.logits(Z)
            alpha = _softmax(logits)
            y_hat = np.sum(alpha * S, axis=1)
            err = y_hat - y

            # dL/dlogit_k = 2*err*alpha_k*(s_k - y_hat)
            dlogits = 2.0 * err[:, None] * alpha * (S - y_hat[:, None])
            grad_W = (dlogits.T @ Z) / n + self.l2 * self.W
            grad_b = np.mean(dlogits, axis=0)

            self.W -= self.lr * grad_W
            self.b -= self.lr * grad_b
