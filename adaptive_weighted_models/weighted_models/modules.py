from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .base import Array, Normalizer, WeightedModule


def _ridge_fit(X: Array, y: Array, l2: float, sample_weight: Array | None = None) -> tuple[Array, float]:
    if sample_weight is None:
        w = np.ones(X.shape[0], dtype=float)
    else:
        w = np.asarray(sample_weight, dtype=float)
    w = np.maximum(w, 1e-12)
    sqrt_w = np.sqrt(w)[:, None]
    Xw = X * sqrt_w
    yw = y * sqrt_w.ravel()

    xtx = Xw.T @ Xw
    xty = Xw.T @ yw
    reg = l2 * np.eye(X.shape[1], dtype=float)
    coef = np.linalg.solve(xtx + reg, xty)

    residual = y - X @ coef
    bias = float(np.average(residual, weights=w))
    return coef, bias


def _blend(old: Array, new: Array, blend: float) -> Array:
    b = float(np.clip(blend, 0.0, 1.0))
    return (1.0 - b) * old + b * new


@dataclass
class StaticWeightedSumModel(WeightedModule):
    name: str = "static_weighted_sum"
    l2: float = 1e-3
    blend: float = 0.5
    static_weights: Array | None = None

    def __post_init__(self) -> None:
        self.coef_: Array | None = None
        self.bias_: float = 0.0
        self.normalizer = Normalizer()

    def fit(self, X: Array, y: Array, **kwargs: object) -> None:
        Xn = self.normalizer.fit_transform(X)
        if self.static_weights is not None:
            weights = np.asarray(self.static_weights, dtype=float)
            if weights.shape[0] != Xn.shape[1]:
                raise ValueError("static_weights length must match feature dimension")
            self.coef_ = weights
            self.bias_ = float(np.mean(y - Xn @ self.coef_))
            return
        self.coef_, self.bias_ = _ridge_fit(Xn, y, l2=self.l2)

    def predict(self, X: Array, **kwargs: object) -> Array:
        if self.coef_ is None:
            raise ValueError("Model is not fitted.")
        Xn = self.normalizer.transform(X)
        return Xn @ self.coef_ + self.bias_

    def retrain(self, X: Array, y: Array, warm_start: bool = True, **kwargs: object) -> None:
        if self.coef_ is None or not warm_start or self.static_weights is not None:
            self.fit(X, y)
            return
        Xn = self.normalizer.transform(X)
        coef_new, bias_new = _ridge_fit(Xn, y, l2=self.l2)
        self.coef_ = _blend(self.coef_, coef_new, self.blend)
        self.bias_ = float((1.0 - self.blend) * self.bias_ + self.blend * bias_new)


@dataclass
class TimeDecayWeightedModel(WeightedModule):
    name: str = "time_decay_weighted"
    l2: float = 1e-3
    decay: float = 0.98
    blend: float = 0.65

    def __post_init__(self) -> None:
        self.coef_: Array | None = None
        self.bias_: float = 0.0
        self.normalizer = Normalizer()

    def _time_weights(self, n: int) -> Array:
        idx = np.arange(n, dtype=float)
        return np.power(self.decay, (n - 1.0) - idx)

    def fit(self, X: Array, y: Array, **kwargs: object) -> None:
        Xn = self.normalizer.fit_transform(X)
        tw = self._time_weights(Xn.shape[0])
        self.coef_, self.bias_ = _ridge_fit(Xn, y, l2=self.l2, sample_weight=tw)

    def predict(self, X: Array, **kwargs: object) -> Array:
        if self.coef_ is None:
            raise ValueError("Model is not fitted.")
        Xn = self.normalizer.transform(X)
        return Xn @ self.coef_ + self.bias_

    def retrain(self, X: Array, y: Array, warm_start: bool = True, **kwargs: object) -> None:
        if self.coef_ is None or not warm_start:
            self.fit(X, y)
            return
        Xn = self.normalizer.transform(X)
        tw = self._time_weights(Xn.shape[0])
        coef_new, bias_new = _ridge_fit(Xn, y, l2=self.l2, sample_weight=tw)
        self.coef_ = _blend(self.coef_, coef_new, self.blend)
        self.bias_ = float((1.0 - self.blend) * self.bias_ + self.blend * bias_new)


@dataclass
class RiskCostWeightedModel(WeightedModule):
    name: str = "risk_cost_weighted"
    l2: float = 1e-3
    risk_index: int = 0
    cost_index: int = 1
    risk_penalty: float = 0.15
    cost_penalty: float = 0.15
    blend: float = 0.6

    def __post_init__(self) -> None:
        self.coef_: Array | None = None
        self.bias_: float = 0.0
        self.normalizer = Normalizer()

    def fit(self, X: Array, y: Array, **kwargs: object) -> None:
        Xn = self.normalizer.fit_transform(X)
        self.coef_, self.bias_ = _ridge_fit(Xn, y, l2=self.l2)

    def _penalty(self, Xn: Array) -> Array:
        risk = Xn[:, self.risk_index]
        cost = Xn[:, self.cost_index]
        return self.risk_penalty * np.maximum(risk, 0.0) + self.cost_penalty * np.maximum(cost, 0.0)

    def predict(self, X: Array, **kwargs: object) -> Array:
        if self.coef_ is None:
            raise ValueError("Model is not fitted.")
        Xn = self.normalizer.transform(X)
        base = Xn @ self.coef_ + self.bias_
        return base - self._penalty(Xn)

    def retrain(self, X: Array, y: Array, warm_start: bool = True, **kwargs: object) -> None:
        if self.coef_ is None or not warm_start:
            self.fit(X, y)
            return
        Xn = self.normalizer.transform(X)
        coef_new, bias_new = _ridge_fit(Xn, y, l2=self.l2)
        self.coef_ = _blend(self.coef_, coef_new, self.blend)
        self.bias_ = float((1.0 - self.blend) * self.bias_ + self.blend * bias_new)


@dataclass
class HierarchicalWeightedModel(WeightedModule):
    name: str = "hierarchical_weighted"
    groups: Sequence[Sequence[int]] | None = None
    l2: float = 1e-3
    blend: float = 0.5

    def __post_init__(self) -> None:
        self.group_coefs_: list[Array] = []
        self.group_bias_: list[float] = []
        self.group_weights_: Array | None = None
        self.normalizer = Normalizer()

    def _resolve_groups(self, d: int) -> list[list[int]]:
        if self.groups is None:
            split = max(1, d // 3)
            g1 = list(range(0, split))
            g2 = list(range(split, min(2 * split, d)))
            g3 = list(range(min(2 * split, d), d))
            groups = [g for g in [g1, g2, g3] if g]
            return groups
        groups = [list(g) for g in self.groups if len(g) > 0]
        if not groups:
            raise ValueError("groups cannot be empty")
        return groups

    def _group_predict_matrix(self, Xn: Array, groups: list[list[int]]) -> Array:
        preds: list[Array] = []
        for idx, grp in enumerate(groups):
            preds.append(Xn[:, grp] @ self.group_coefs_[idx] + self.group_bias_[idx])
        return np.column_stack(preds)

    def fit(self, X: Array, y: Array, **kwargs: object) -> None:
        Xn = self.normalizer.fit_transform(X)
        groups = self._resolve_groups(Xn.shape[1])
        self.group_coefs_.clear()
        self.group_bias_.clear()
        for grp in groups:
            coef, bias = _ridge_fit(Xn[:, grp], y, l2=self.l2)
            self.group_coefs_.append(coef)
            self.group_bias_.append(bias)

        S = self._group_predict_matrix(Xn, groups)
        gw, _ = _ridge_fit(S, y, l2=self.l2)
        gw = np.maximum(gw, 0.0)
        if gw.sum() <= 1e-12:
            gw = np.ones_like(gw)
        self.group_weights_ = gw / gw.sum()
        self.groups = groups

    def predict(self, X: Array, **kwargs: object) -> Array:
        if self.group_weights_ is None or self.groups is None:
            raise ValueError("Model is not fitted.")
        Xn = self.normalizer.transform(X)
        S = self._group_predict_matrix(Xn, [list(g) for g in self.groups])
        return S @ self.group_weights_

    def retrain(self, X: Array, y: Array, warm_start: bool = True, **kwargs: object) -> None:
        if self.group_weights_ is None or self.groups is None or not warm_start:
            self.fit(X, y)
            return
        Xn = self.normalizer.transform(X)
        for i, grp in enumerate(self.groups):
            coef_new, bias_new = _ridge_fit(Xn[:, grp], y, l2=self.l2)
            self.group_coefs_[i] = _blend(self.group_coefs_[i], coef_new, self.blend)
            self.group_bias_[i] = float((1.0 - self.blend) * self.group_bias_[i] + self.blend * bias_new)

        S = self._group_predict_matrix(Xn, [list(g) for g in self.groups])
        gw_new, _ = _ridge_fit(S, y, l2=self.l2)
        gw_new = np.maximum(gw_new, 0.0)
        if gw_new.sum() <= 1e-12:
            gw_new = np.ones_like(gw_new)
        gw_new = gw_new / gw_new.sum()
        self.group_weights_ = _blend(self.group_weights_, gw_new, self.blend)
        self.group_weights_ = np.maximum(self.group_weights_, 1e-12)
        self.group_weights_ = self.group_weights_ / self.group_weights_.sum()


@dataclass
class EnsembleWeightedModel(WeightedModule):
    name: str = "ensemble_weighted"
    l2_values: Sequence[float] = (1e-2, 1e-3, 1e-1)

    def __post_init__(self) -> None:
        self.coefs_: list[Array] = []
        self.biases_: list[float] = []
        self.ensemble_weights_: Array | None = None
        self.normalizer = Normalizer()

    def fit(self, X: Array, y: Array, **kwargs: object) -> None:
        Xn = self.normalizer.fit_transform(X)
        self.coefs_.clear()
        self.biases_.clear()
        member_preds: list[Array] = []
        for l2 in self.l2_values:
            coef, bias = _ridge_fit(Xn, y, l2=l2)
            self.coefs_.append(coef)
            self.biases_.append(bias)
            member_preds.append(Xn @ coef + bias)

        P = np.column_stack(member_preds)
        w, _ = _ridge_fit(P, y, l2=1e-3)
        w = np.maximum(w, 0.0)
        if w.sum() <= 1e-12:
            w = np.ones_like(w)
        self.ensemble_weights_ = w / w.sum()

    def predict(self, X: Array, **kwargs: object) -> Array:
        if self.ensemble_weights_ is None:
            raise ValueError("Model is not fitted.")
        Xn = self.normalizer.transform(X)
        members = [Xn @ c + b for c, b in zip(self.coefs_, self.biases_)]
        P = np.column_stack(members)
        return P @ self.ensemble_weights_

    def retrain(self, X: Array, y: Array, warm_start: bool = True, **kwargs: object) -> None:
        self.fit(X, y)


@dataclass
class OnlineAdaptiveWeightedModel(WeightedModule):
    name: str = "online_adaptive_weighted"
    lr: float = 0.02
    l2: float = 1e-4
    epochs: int = 4

    def __post_init__(self) -> None:
        self.coef_: Array | None = None
        self.bias_: float = 0.0
        self.accum_grad_: Array | None = None
        self.normalizer = Normalizer()

    def _ensure_state(self, d: int) -> None:
        if self.coef_ is None:
            self.coef_ = np.zeros(d, dtype=float)
            self.accum_grad_ = np.ones(d, dtype=float) * 1e-6

    def _train_online(self, Xn: Array, y: Array, epochs: int) -> None:
        self._ensure_state(Xn.shape[1])
        assert self.coef_ is not None
        assert self.accum_grad_ is not None

        for _ in range(epochs):
            for xi, yi in zip(Xn, y):
                pred = float(xi @ self.coef_ + self.bias_)
                err = pred - float(yi)
                grad = err * xi + self.l2 * self.coef_
                self.accum_grad_ += grad * grad
                step = self.lr / np.sqrt(self.accum_grad_)
                self.coef_ -= step * grad
                self.bias_ -= self.lr * err

    def fit(self, X: Array, y: Array, **kwargs: object) -> None:
        Xn = self.normalizer.fit_transform(X)
        self.coef_ = None
        self.accum_grad_ = None
        self.bias_ = 0.0
        self._train_online(Xn, y, epochs=self.epochs)

    def predict(self, X: Array, **kwargs: object) -> Array:
        if self.coef_ is None:
            raise ValueError("Model is not fitted.")
        Xn = self.normalizer.transform(X)
        return Xn @ self.coef_ + self.bias_

    def retrain(self, X: Array, y: Array, warm_start: bool = True, **kwargs: object) -> None:
        if self.coef_ is None or not warm_start:
            self.fit(X, y)
            return
        Xn = self.normalizer.transform(X)
        self._train_online(Xn, y, epochs=max(1, self.epochs // 2))


@dataclass
class SuperWeightedModel(WeightedModule):
    """Model that identifies and amplifies the top-k most influential weights.

    After an initial ridge fit, features are ranked by absolute coefficient
    magnitude.  The ``top_k`` highest-magnitude features are designated
    *super weights* and receive an additional ``boost`` multiplier, while all
    remaining feature coefficients are zeroed out.  This produces a sparse,
    interpretable model dominated by its most predictive features.

    Parameters
    ----------
    top_k:
        Number of super-weight features to retain.  Set to 0 to use
        ``top_k_ratio`` instead.
    top_k_ratio:
        Fraction of features to retain when ``top_k`` is 0 (e.g. 0.25 keeps
        the top 25 %).  Clipped to [1, d].
    boost:
        Multiplicative amplification applied to the retained super weights.
    l2:
        Ridge regularisation strength used during the initial fit.
    blend:
        Blending factor for warm-start retrain (0 = keep old, 1 = full new).
    """

    name: str = "super_weighted"
    top_k: int = 0
    top_k_ratio: float = 0.25
    boost: float = 1.5
    l2: float = 1e-3
    blend: float = 0.5
    enabled: bool = True

    def __post_init__(self) -> None:
        self.coef_: Array | None = None
        self._raw_coef_: Array | None = None  # un-boosted coefficients for fallback
        self.bias_: float = 0.0
        self.super_indices_: Array | None = None
        self.normalizer = Normalizer()

    def toggle(self, enabled: bool | None = None) -> bool:
        """Enable or disable super-weight boosting.

        Parameters
        ----------
        enabled:
            Pass ``True`` to enable, ``False`` to disable, or ``None`` to
            flip the current state.

        Returns
        -------
        bool
            The new ``enabled`` state.
        """
        self.enabled = not self.enabled if enabled is None else bool(enabled)
        return self.enabled

    def _select_super(self, coef: Array) -> Array:
        d = coef.shape[0]
        k = self.top_k if self.top_k > 0 else max(1, int(round(self.top_k_ratio * d)))
        k = int(np.clip(k, 1, d))
        return np.argsort(np.abs(coef))[-k:]

    def _apply_super(self, coef: Array, indices: Array) -> Array:
        out = np.zeros_like(coef)
        out[indices] = coef[indices] * self.boost
        return out

    def fit(self, X: Array, y: Array, **kwargs: object) -> None:
        Xn = self.normalizer.fit_transform(X)
        raw_coef, self.bias_ = _ridge_fit(Xn, y, l2=self.l2)
        self._raw_coef_ = raw_coef.copy()
        self.super_indices_ = self._select_super(raw_coef)
        self.coef_ = self._apply_super(raw_coef, self.super_indices_)
        # Refine bias after masking
        self.bias_ = float(np.mean(y - Xn @ self.coef_))

    def predict(self, X: Array, **kwargs: object) -> Array:
        if self.coef_ is None or self._raw_coef_ is None:
            raise ValueError("Model is not fitted.")
        Xn = self.normalizer.transform(X)
        coef = self.coef_ if self.enabled else self._raw_coef_
        return Xn @ coef + self.bias_

    def retrain(self, X: Array, y: Array, warm_start: bool = True, **kwargs: object) -> None:
        if self.coef_ is None or not warm_start:
            self.fit(X, y)
            return
        Xn = self.normalizer.transform(X)
        raw_coef, bias_new = _ridge_fit(Xn, y, l2=self.l2)
        new_indices = self._select_super(raw_coef)
        new_coef = self._apply_super(raw_coef, new_indices)
        self._raw_coef_ = _blend(self._raw_coef_, raw_coef, self.blend) if self._raw_coef_ is not None else raw_coef
        self.coef_ = _blend(self.coef_, new_coef, self.blend)
        self.bias_ = float((1.0 - self.blend) * self.bias_ + self.blend * bias_new)
        # Update super indices to reflect blended coefficients
        self.super_indices_ = self._select_super(self.coef_)


def default_modules(feature_dim: int) -> list[WeightedModule]:
    return [
        StaticWeightedSumModel(),
        TimeDecayWeightedModel(),
        RiskCostWeightedModel(risk_index=0, cost_index=min(1, feature_dim - 1)),
        HierarchicalWeightedModel(),
        EnsembleWeightedModel(),
        OnlineAdaptiveWeightedModel(),
        SuperWeightedModel(),
    ]
