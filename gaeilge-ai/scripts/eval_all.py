"""Baseline vs LoRA eval on the test split, both directions.

Scores BLEU + chrF for the raw opus-mt base models and the trained LoRA
adapters, on the held-out test set. Runs on GPU if available.

    $env:PYTHONPATH = 'C:\\Users\\EC\\gaeilge-ai\\src'
    python scripts/eval_all.py --device cuda --limit 0
"""

from __future__ import annotations

import argparse
from pathlib import Path

from gaeilge_ai.data_prep import Pair, read_tsv
from gaeilge_ai.eval import evaluate
from gaeilge_ai.translate import Translator


def load_lora(base_id: str, adapter: str, device: str) -> Translator:
    """A Translator whose model is the base wrapped with a LoRA adapter."""
    from peft import PeftModel

    t = Translator(direction="x", model_id=base_id, device=device)
    t.model = PeftModel.from_pretrained(t.model, adapter).to(device).eval()
    t._model_id = f"{base_id} + {adapter}"
    return t


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", type=Path, default=Path("data/splits/test.tsv"))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0, help="Eval first N pairs only (0 = all)")
    args = ap.parse_args()

    test = read_tsv(args.test)
    if args.limit:
        test = test[: args.limit]
    # test.tsv columns are src=EN, tgt=GA
    en_ga = test
    ga_en = [Pair(src=p.tgt, tgt=p.src) for p in test]  # swap for reverse direction
    print(f"eval on {len(test)} test pairs (device={args.device})\n")

    jobs = [
        ("EN->GA base", Translator("en-ga", "Helsinki-NLP/opus-mt-en-ga", args.device), en_ga),
        ("EN->GA LoRA", load_lora("Helsinki-NLP/opus-mt-en-ga", "models/lora-en-ga", args.device), en_ga),
        ("GA->EN base", Translator("ga-en", "Helsinki-NLP/opus-mt-ga-en", args.device), ga_en),
        ("GA->EN LoRA", load_lora("Helsinki-NLP/opus-mt-ga-en", "models/lora-ga-en", args.device), ga_en),
    ]

    rows = []
    for label, translator, data in jobs:
        r = evaluate(translator, data, batch_size=args.batch_size)
        rows.append((label, r.bleu, r.chrf))
        print(f"{label:14}  BLEU {r.bleu:6.2f}   chrF {r.chrf:6.2f}")

    print("\n=== summary ===")
    print(f"{'model':14} {'BLEU':>7} {'chrF':>7}")
    for label, bleu, chrf in rows:
        print(f"{label:14} {bleu:7.2f} {chrf:7.2f}")


if __name__ == "__main__":
    main()
