from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Pair:
    src: str
    tgt: str


def _from_tatoeba(direction: str) -> list[Pair]:
    from datasets import load_dataset
    src, tgt = direction.split("-")
    iso3 = {"en": "eng", "ga": "gle"}
    cfg = f"{iso3[src]}-{iso3[tgt]}"
    ds = load_dataset("Helsinki-NLP/tatoeba_mt", cfg, split="test+validation", trust_remote_code=True)
    return [Pair(ex["sourceString"], ex["targetString"]) for ex in ds]


def _from_opus100(direction: str) -> list[Pair]:
    from datasets import load_dataset
    src, tgt = direction.split("-")
    cfg = f"{src}-{tgt}" if src < tgt else f"{tgt}-{src}"
    ds = load_dataset("Helsinki-NLP/opus-100", cfg, split="train")
    out = []
    for ex in ds:
        t = ex["translation"]
        out.append(Pair(t[src], t[tgt]))
    return out


def collect(direction: str) -> list[Pair]:
    pairs: list[Pair] = []
    for loader in (_from_tatoeba, _from_opus100):
        try:
            pairs.extend(loader(direction))
        except Exception as e:
            print(f"[warn] {loader.__name__} failed: {e}")
    return pairs


def dedupe(pairs: list[Pair]) -> list[Pair]:
    seen: set[str] = set()
    out = []
    for p in pairs:
        key = p.src.strip().lower()
        if not key or key in seen:
            continue
        if not p.tgt.strip():
            continue
        seen.add(key)
        out.append(p)
    return out


def split(pairs: list[Pair], dev_frac: float = 0.05, test_frac: float = 0.05, seed: int = 13) -> dict[str, list[Pair]]:
    rng = random.Random(seed)
    shuffled = pairs[:]
    rng.shuffle(shuffled)
    n = len(shuffled)
    n_test = int(n * test_frac)
    n_dev = int(n * dev_frac)
    return {
        "test": shuffled[:n_test],
        "dev": shuffled[n_test : n_test + n_dev],
        "train": shuffled[n_test + n_dev :],
    }


def write_tsv(pairs: list[Pair], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writerow(["src", "tgt"])
        for p in pairs:
            w.writerow([p.src.replace("\t", " "), p.tgt.replace("\t", " ")])


def read_tsv(path: Path) -> list[Pair]:
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        return [Pair(row["src"], row["tgt"]) for row in r]
