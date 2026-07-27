from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .data_prep import Pair

if TYPE_CHECKING:
    from .translate import Translator


@dataclass
class EvalResult:
    model: str
    n: int
    bleu: float
    chrf: float


def evaluate(translator: "Translator", test_set: list[Pair], batch_size: int = 16) -> EvalResult:
    from sacrebleu.metrics import BLEU, CHRF
    sources = [p.src for p in test_set]
    refs = [[p.tgt for p in test_set]]
    hyps = translator.translate(sources, batch_size=batch_size)
    bleu = BLEU().corpus_score(hyps, refs).score
    chrf = CHRF().corpus_score(hyps, refs).score
    return EvalResult(model=translator.name, n=len(test_set), bleu=bleu, chrf=chrf)


def per_sentence_chrf(translator: "Translator", calibration_set: list[Pair], batch_size: int = 16) -> list[float]:
    """chrF per input — used by the router to learn per-input model quality."""
    from sacrebleu.metrics import CHRF
    chrf = CHRF()
    hyps = translator.translate([p.src for p in calibration_set], batch_size=batch_size)
    return [chrf.sentence_score(h, [p.tgt]).score for h, p in zip(hyps, calibration_set)]
