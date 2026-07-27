from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


DEFAULT_MODELS = {
    "en-ga": "Helsinki-NLP/opus-mt-en-ga",
    "ga-en": "Helsinki-NLP/opus-mt-ga-en",
}


@dataclass
class Translator:
    direction: str
    model_id: str | None = None
    device: str = "cpu"
    max_length: int = 256

    def __post_init__(self) -> None:
        model_id = self.model_id or DEFAULT_MODELS[self.direction]
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(self.device)
        self.model.eval()
        self._model_id = model_id

    @property
    def name(self) -> str:
        return self._model_id

    def translate(self, texts: Iterable[str], batch_size: int = 16) -> list[str]:
        import torch

        batch = list(texts)
        out: list[str] = []
        with torch.no_grad():
            for i in range(0, len(batch), batch_size):
                chunk = batch[i : i + batch_size]
                enc = self.tokenizer(chunk, return_tensors="pt", padding=True, truncation=True, max_length=self.max_length).to(self.device)
                gen = self.model.generate(**enc, max_length=self.max_length, num_beams=4)
                out.extend(self.tokenizer.batch_decode(gen, skip_special_tokens=True))
        return out
