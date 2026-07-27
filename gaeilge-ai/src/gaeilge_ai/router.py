from __future__ import annotations

import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from .data_prep import Pair

if TYPE_CHECKING:
    from .translate import Translator


# Make the user's existing ensemble importable. Adjust the path if you move
# adaptive_weighted_models elsewhere.
_AWM_ROOT = Path(r"C:\Users\EC\adaptive_weighted_models")
if _AWM_ROOT.exists() and str(_AWM_ROOT) not in sys.path:
    sys.path.insert(0, str(_AWM_ROOT))


def features(text: str) -> np.ndarray:
    """Cheap per-input features used as both X and Z for the router."""
    n = max(len(text), 1)
    letters = sum(ch.isalpha() for ch in text)
    digits = sum(ch.isdigit() for ch in text)
    upper = sum(ch.isupper() for ch in text)
    fadas = sum(1 for ch in text if unicodedata.normalize("NFD", ch)[1:2] == "́")
    n_tokens = len(text.split()) or 1
    avg_tok = n / n_tokens
    return np.array([
        np.log1p(n),
        np.log1p(n_tokens),
        avg_tok,
        letters / n,
        digits / n,
        upper / n,
        fadas / n,
    ], dtype=float)


@dataclass
class AdaptiveTranslationRouter:
    experts: list["Translator"] = field(default_factory=list)
    _systems: list = field(default_factory=list, init=False)

    def add(self, translator: "Translator") -> None:
        self.experts.append(translator)

    def calibrate(self, calibration_set: list[Pair]) -> None:
        """Train one chrF-predictor per expert on the calibration set."""
        from weighted_models import AdaptiveWeightedSystem
        from .eval import per_sentence_chrf

        if not self.experts:
            raise ValueError("Add at least one expert before calibrating.")
        X = np.stack([features(p.src) for p in calibration_set])
        Z = X.copy()
        self._systems = []
        for expert in self.experts:
            y = np.array(per_sentence_chrf(expert, calibration_set), dtype=float)
            sys_ = AdaptiveWeightedSystem()
            sys_.fit(X, y, Z)
            self._systems.append(sys_)

    def _pick(self, text: str) -> int:
        if not self._systems:
            return 0
        x = features(text)[None, :]
        scores = [float(sys_.predict(x, x)[0]) for sys_ in self._systems]
        return int(np.argmax(scores))

    def translate(self, text: str) -> tuple[str, str]:
        """Returns (translation, chosen_model_name)."""
        if not self.experts:
            raise ValueError("No experts registered.")
        idx = self._pick(text)
        return self.experts[idx].translate([text])[0], self.experts[idx].name
