# gaeilge-ai

Irish-language (Gaeilge) translation models. Stage 1 fine-tunes the Helsinki-NLP Marian models on EN↔GA parallel data and evaluates with BLEU and chrF. Stage 2 adds a meta-router on top of multiple checkpoints via the user's `adaptive_weighted_models` ensemble.

## Layout

```
src/gaeilge_ai/
  data_prep.py   # pull + dedupe + split parallel corpora
  translate.py   # single-model HF translation wrapper
  eval.py        # BLEU / chrF on a held-out set
  router.py      # adaptive ensemble across N checkpoints
scripts/         # CLI entry points
notebooks/       # Colab fine-tuning notebooks
tests/           # unit + smoke tests
data/raw/        # downloaded corpora (gitignored)
data/splits/     # train/dev/test TSVs (gitignored)
```

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .

# Pull + split EN-GA parallel data (Tatoeba + OPUS-100)
python scripts/prepare_data.py --pair en-ga --out data/splits

# Baseline eval of the off-the-shelf Helsinki-NLP/opus-mt-en-ga
python scripts/eval_baseline.py --pair en-ga --test data/splits/test.tsv
```

## Fine-tuning

Local CPU is too slow for the full fine-tune. Open `notebooks/train_lora.ipynb` in Google Colab (free T4 tier is enough for LoRA on opus-mt-en-ga). Upload the train/dev splits, run all cells, download the adapter into `models/`.

## Meta-router

Once two or more checkpoints exist (e.g., baseline + LoRA-tuned), `router.py` calibrates `adaptive_weighted_models.AdaptiveWeightedSystem` against per-input chrF on a held-out calibration set, then at inference picks the expected-best model per input from context features (input length, char-class distribution, etc.).
