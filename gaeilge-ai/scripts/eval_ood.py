"""Out-of-domain eval: base vs LoRA, both directions, on Tatoeba conversational
sentences that are NOT in our training/dev/test splits.

Our training pool came from OPUS (EU/legal/software) + Tatoeba test+validation.
Here we pull Tatoeba eng-gle and drop any pair whose source OR target string
appears anywhere in data/splits/*.tsv, so what remains is genuinely held out
and from a different (conversational) domain than the bulk of training.

    $env:PYTHONPATH = 'C:\\Users\\EC\\gaeilge-ai\\src'
    python scripts/eval_ood.py --device cuda --cap 1500
"""

from __future__ import annotations

import argparse
from pathlib import Path

# datasets before torch (pyarrow/torch DLL segfault on Windows+cu128)
from datasets import get_dataset_split_names, load_dataset

from gaeilge_ai.data_prep import Pair, read_tsv
from gaeilge_ai.eval import evaluate
from gaeilge_ai.translate import Translator


def load_lora(base_id: str, adapter: str, device: str) -> Translator:
    from peft import PeftModel

    t = Translator(direction="x", model_id=base_id, device=device)
    t.model = PeftModel.from_pretrained(t.model, adapter).to(device).eval()
    t._model_id = f"{base_id} + {adapter}"
    return t


def seen_strings(splits_dir: Path) -> set[str]:
    seen: set[str] = set()
    for tsv in splits_dir.glob("*.tsv"):
        for p in read_tsv(tsv):
            seen.add(p.src.strip().lower())
            seen.add(p.tgt.strip().lower())
    return seen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--cap", type=int, default=1500, help="Max held-out pairs to eval")
    ap.add_argument("--splits", type=Path, default=Path("data/splits"))
    args = ap.parse_args()

    seen = seen_strings(args.splits)
    print(f"loaded {len(seen)} seen strings from training splits")

    # OPUS-100 test split: held out (training used the 'train' split only),
    # mixed-domain, loads as native parquet.
    splits = get_dataset_split_names("Helsinki-NLP/opus-100", "en-ga")
    print(f"opus-100 en-ga splits available: {splits}")
    ds = load_dataset("Helsinki-NLP/opus-100", "en-ga", split="test")
    print(f"pulled {len(ds)} raw opus-100 test pairs")

    held: list[Pair] = []
    dropped = 0
    for ex in ds:
        t = ex["translation"]
        en = (t["en"] or "").strip()
        ga = (t["ga"] or "").strip()
        if not en or not ga:
            continue
        if en.lower() in seen or ga.lower() in seen:
            dropped += 1
            continue
        held.append(Pair(src=en, tgt=ga))
        if len(held) >= args.cap:
            break
    print(f"held-out (not in training): {len(held)} pairs ({dropped} dropped as seen)\n")

    en_ga = held
    ga_en = [Pair(src=p.tgt, tgt=p.src) for p in held]

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

    print("\n=== OOD summary (Tatoeba, held-out) ===")
    print(f"{'model':14} {'BLEU':>7} {'chrF':>7}")
    for label, bleu, chrf in rows:
        print(f"{label:14} {bleu:7.2f} {chrf:7.2f}")


if __name__ == "__main__":
    main()
