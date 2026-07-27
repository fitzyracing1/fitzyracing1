from __future__ import annotations

import json
import os
import pickle
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


@dataclass
class RetrievalIndex:
    chunks: list[str]
    sources: list[str]
    vocab: dict[str, int]
    idf: np.ndarray
    matrix: np.ndarray


@dataclass
class SearchResult:
    rank: int
    score: float
    source: str
    text: str


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        end = start + chunk_size
        segment = words[start:end]
        if segment:
            chunks.append(" ".join(segment))
        if end >= len(words):
            break
    return chunks


def _read_source_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".rst", ".log", ".py", ".json", ".csv"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {path}")


def _iter_source_files(source_path: Path) -> Iterable[Path]:
    if source_path.is_file():
        yield source_path
        return

    for ext in ("*.txt", "*.md", "*.rst", "*.log", "*.py", "*.json", "*.csv"):
        yield from source_path.rglob(ext)


def _build_index_from_chunks(chunks: list[str], sources: list[str]) -> RetrievalIndex:
    if not chunks:
        raise ValueError("No text chunks were created. Add source files and retry.")

    vocab: dict[str, int] = {}
    tokenized_chunks: list[list[str]] = []
    df_counts: dict[int, int] = {}

    for chunk in chunks:
        tokens = _tokenize(chunk)
        tokenized_chunks.append(tokens)
        seen: set[int] = set()
        for tok in tokens:
            idx = vocab.setdefault(tok, len(vocab))
            if idx not in seen:
                df_counts[idx] = df_counts.get(idx, 0) + 1
                seen.add(idx)

    n_docs = len(chunks)
    n_terms = len(vocab)
    idf = np.ones(n_terms, dtype=float)
    for idx in range(n_terms):
        df = df_counts.get(idx, 0)
        idf[idx] = np.log((1.0 + n_docs) / (1.0 + df)) + 1.0

    matrix = np.zeros((n_docs, n_terms), dtype=float)
    for i, tokens in enumerate(tokenized_chunks):
        if not tokens:
            continue
        counts: dict[int, int] = {}
        for tok in tokens:
            idx = vocab[tok]
            counts[idx] = counts.get(idx, 0) + 1
        total = float(len(tokens))
        for idx, cnt in counts.items():
            tf = cnt / total
            matrix[i, idx] = tf * idf[idx]

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    matrix = matrix / norms

    return RetrievalIndex(chunks=chunks, sources=sources, vocab=vocab, idf=idf, matrix=matrix)


def build_index_from_documents(documents: list[tuple[str, str]], chunk_size: int = 140, overlap: int = 30) -> RetrievalIndex:
    chunks: list[str] = []
    sources: list[str] = []

    for source, text in documents:
        for chunk in _split_text(text, chunk_size=chunk_size, overlap=overlap):
            chunks.append(chunk)
            sources.append(source)

    return _build_index_from_chunks(chunks, sources)


def build_index(source_path: Path, chunk_size: int = 140, overlap: int = 30) -> RetrievalIndex:
    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source_path}")

    chunks: list[str] = []
    sources: list[str] = []

    for file_path in _iter_source_files(source_path):
        text = _read_source_file(file_path)
        for chunk in _split_text(text, chunk_size=chunk_size, overlap=overlap):
            chunks.append(chunk)
            sources.append(str(file_path))

    return _build_index_from_chunks(chunks, sources)


def save_index(index: RetrievalIndex, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(index, f)


def load_index(path: Path) -> RetrievalIndex:
    with path.open("rb") as f:
        obj = pickle.load(f)
    if not isinstance(obj, RetrievalIndex):
        raise TypeError("Index file does not contain a RetrievalIndex")
    return obj


def search_index(index: RetrievalIndex, query: str, top_k: int = 5) -> list[SearchResult]:
    tokens = _tokenize(query)
    if not tokens:
        return []

    q = np.zeros(len(index.vocab), dtype=float)
    counts: dict[int, int] = {}
    for tok in tokens:
        idx = index.vocab.get(tok)
        if idx is not None:
            counts[idx] = counts.get(idx, 0) + 1

    total = float(sum(counts.values()))
    if total == 0.0:
        return []

    for idx, cnt in counts.items():
        q[idx] = (cnt / total) * index.idf[idx]

    q_norm = np.linalg.norm(q)
    if q_norm == 0.0:
        return []
    q = q / q_norm

    scores = index.matrix @ q
    order = np.argsort(-scores)[: max(1, top_k)]

    results: list[SearchResult] = []
    rank = 1
    for i in order:
        score = float(scores[i])
        if score <= 0.0:
            continue
        results.append(SearchResult(rank=rank, score=score, source=index.sources[i], text=index.chunks[i]))
        rank += 1
    return results


def _build_context(results: list[SearchResult], max_chars: int = 6000) -> str:
    parts: list[str] = []
    used = 0
    for item in results:
        block = f"[rank={item.rank} score={item.score:.4f} source={item.source}]\n{item.text}\n"
        if used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)
    return "\n".join(parts)


def ask_with_context(
    query: str,
    results: list[SearchResult],
    model: str = "gpt-4o-mini",
    api_key: str | None = None,
    base_url: str | None = None,
) -> str:
    context = _build_context(results)
    if not context:
        return "No relevant context found in index."

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        return (
            "No OPENAI_API_KEY detected. Retrieved context:\n\n"
            + context
            + "\n\nSet OPENAI_API_KEY to get a generated answer."
        )

    endpoint = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com").rstrip("/")
    url = endpoint + "/v1/chat/completions"

    prompt = (
        "Answer only from the provided context. "
        "If the context is insufficient, say exactly what is missing.\n\n"
        f"Question: {query}\n\n"
        f"Context:\n{context}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise retrieval-augmented assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        return f"LLM request failed: HTTP {e.code}\n{detail}"
    except urllib.error.URLError as e:
        return f"LLM request failed: {e}"

    parsed = json.loads(body)
    choices = parsed.get("choices", [])
    if not choices:
        return f"LLM response missing choices: {body}"

    message = choices[0].get("message", {})
    content = message.get("content", "")
    return str(content).strip() or "LLM returned an empty response."
