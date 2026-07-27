from __future__ import annotations

import argparse
from pathlib import Path

from gaeilge_ai.data_prep import collect, dedupe, split, write_tsv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", default="en-ga", help="e.g. en-ga or ga-en")
    ap.add_argument("--out", type=Path, default=Path("data/splits"))
    ap.add_argument("--dev-frac", type=float, default=0.05)
    ap.add_argument("--test-frac", type=float, default=0.05)
    args = ap.parse_args()

    raw = collect(args.pair)
    print(f"collected {len(raw)} pairs across all sources")
    deduped = dedupe(raw)
    print(f"after dedupe: {len(deduped)}")
    parts = split(deduped, dev_frac=args.dev_frac, test_frac=args.test_frac)
    for name, pairs in parts.items():
        out = args.out / f"{name}.tsv"
        write_tsv(pairs, out)
        print(f"wrote {len(pairs):>7d} -> {out}")


if __name__ == "__main__":
    main()
