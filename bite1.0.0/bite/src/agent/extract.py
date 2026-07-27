import re
from collections import Counter


def keyword_density(text: str, words: list[str]) -> float:
    if not text:
        return 0.0
    tokens = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
    if not tokens:
        return 0.0
    c = Counter(tokens)
    hits = sum(c[w.lower()] for w in words)
    return hits / max(len(tokens), 1)


def confidence_score(reliability: float, relevance: float, novelty: float, weights: tuple[float, float, float]) -> float:
    rw, relw, nw = weights
    raw = rw * reliability + relw * relevance + nw * novelty
    return max(0.0, min(1.0, raw / max(rw + relw + nw, 1e-6)))


def summarize(text: str, max_chars: int = 280) -> str:
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def extraction_quality_score(title: str, text: str, min_chars: int = 160) -> float:
    clean_title = title.strip()
    clean_text = " ".join(text.split())
    if not clean_text:
        return 0.0

    text_score = min(1.0, len(clean_text) / max(min_chars * 2, 1))
    title_score = 1.0 if clean_title and clean_title.lower() != "untitled" else 0.3
    return max(0.0, min(1.0, 0.75 * text_score + 0.25 * title_score))


def calibrate_reliability(base_reliability: float, quality_score: float) -> float:
    scaled = base_reliability * (0.7 + 0.3 * quality_score)
    return max(0.0, min(1.0, scaled))
