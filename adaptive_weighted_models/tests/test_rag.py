from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from weighted_models.rag import ask_with_context, build_index, load_index, save_index, search_index


class RagTests(unittest.TestCase):
    def test_ingest_search_and_fallback_ask(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs = root / "docs"
            docs.mkdir(parents=True, exist_ok=True)

            (docs / "a.txt").write_text(
                "Adaptive weighted models combine module predictions with context-aware weights.",
                encoding="utf-8",
            )
            (docs / "b.md").write_text(
                "Drift detection can trigger warm-start retraining when recent error rises.",
                encoding="utf-8",
            )

            index = build_index(docs)
            idx_path = root / "index.pkl"
            save_index(index, idx_path)

            loaded = load_index(idx_path)
            results = search_index(loaded, "context-aware weights", top_k=3)

            self.assertGreaterEqual(len(results), 1)
            self.assertIn("weights", results[0].text.lower())

            answer = ask_with_context("How are weights used?", results, api_key=None)
            self.assertIn("No OPENAI_API_KEY detected", answer)


if __name__ == "__main__":
    unittest.main()
