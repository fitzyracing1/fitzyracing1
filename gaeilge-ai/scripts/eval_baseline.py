from __future__ import annotations

import argparse
from pathlib import Path

from gaeilge_ai.data_prep import read_tsv
from gaeilge_ai.eval import evaluate
from gaeilge_ai.translate import DEFAULT_MODELS, Translator


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", default="en-ga")
    ap.add_argument("--model", default=None, help="HF model id (defaults to Helsinki-NLP/opus-mt-<pair>)")
    ap.add_argument("--test", type=Path, default=Path("data/splits/test.tsv"))
    ap.add_argument("--limit", type=int, default=0, help="Eval on first N pairs only (0 = all)")
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    test = read_tsv(args.test)
    if args.limit:
        test = test[: args.limit]
    print(f"loaded {len(test)} test pairs from {args.test}")

    translator = Translator(
        direction=args.pair,
        model_id=args.model or DEFAULT_MODELS[args.pair],
        device=args.device,
    )
    result = evaluate(translator, test)
    print(f"model:  {result.model}")
    print(f"n:      {result.n}")
    print(f"BLEU:   {result.bleu:.2f}")
    print(f"chrF:   {result.chrf:.2f}")


if __name__ == "__main__":
    main()
