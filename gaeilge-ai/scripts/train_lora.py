"""Local LoRA fine-tune of opus-mt-en-ga.

Adapted from notebooks/train_lora.ipynb to run locally on a CUDA GPU with
transformers 5.x. Saves a LoRA adapter to --output.

Example:
    $env:PYTHONPATH = 'C:\\Users\\EC\\gaeilge-ai\\src'
    python scripts/train_lora.py --epochs 2 --batch-size 32
"""

from __future__ import annotations

import argparse
from pathlib import Path

# NOTE: datasets must be imported before torch. On this Windows + cu128 setup,
# `import torch` followed by importing datasets segfaults (pyarrow/torch DLL
# clash); importing datasets first avoids it.
from datasets import load_dataset

import torch
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model", default="Helsinki-NLP/opus-mt-en-ga")
    ap.add_argument("--train", type=Path, default=Path("data/splits/train.tsv"))
    ap.add_argument("--dev", type=Path, default=Path("data/splits/dev.tsv"))
    ap.add_argument("--output", type=Path, default=Path("models/lora-en-ga"))
    ap.add_argument("--epochs", type=float, default=2.0)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--limit", type=int, default=0, help="Use first N train pairs only (0 = all)")
    ap.add_argument("--swap", action="store_true", help="Swap src/tgt columns (e.g. train ga-en from en-ga TSVs)")
    args = ap.parse_args()

    use_cuda = torch.cuda.is_available()
    print(f"CUDA available: {use_cuda}")
    if use_cuda:
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    tok = AutoTokenizer.from_pretrained(args.base_model)
    base = AutoModelForSeq2SeqLM.from_pretrained(args.base_model)

    raw = load_dataset(
        "csv",
        data_files={"train": str(args.train), "dev": str(args.dev)},
        delimiter="\t",
    )
    if args.limit:
        raw["train"] = raw["train"].select(range(min(args.limit, len(raw["train"]))))
    print(raw)

    src_col, tgt_col = ("tgt", "src") if args.swap else ("src", "tgt")

    def preprocess(batch):
        src = [s or "" for s in batch[src_col]]
        tgt = [t or "" for t in batch[tgt_col]]
        enc = tok(src, text_target=tgt, max_length=args.max_len, truncation=True)
        return enc

    ds = raw.map(preprocess, batched=True, remove_columns=raw["train"].column_names)

    lora = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "out_proj"],
    )
    model = get_peft_model(base, lora)
    model.print_trainable_parameters()

    collator = DataCollatorForSeq2Seq(tok, model=model)
    targs = Seq2SeqTrainingArguments(
        output_dir=str(args.output / "trainer"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.lr,
        warmup_ratio=0.05,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        predict_with_generate=False,
        bf16=use_cuda,
        report_to="none",
    )
    trainer = Seq2SeqTrainer(
        model=model,
        args=targs,
        train_dataset=ds["train"],
        eval_dataset=ds["dev"],
        processing_class=tok,
        data_collator=collator,
    )
    trainer.train()

    args.output.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(args.output))
    tok.save_pretrained(str(args.output))
    print(f"saved LoRA adapter -> {args.output}")


if __name__ == "__main__":
    main()
