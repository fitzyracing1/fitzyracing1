from __future__ import annotations

import argparse
import csv
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Sequence

import numpy as np

from .system import AdaptiveWeightedSystem
from .rag import ask_with_context, build_index, load_index, save_index, search_index
from .plugins import bootstrap_ready_player_one, bootstrap_ready_player_one_live_ops
from .distributed import compute_ready_player_one_score


def _parse_cols(value: str | None) -> list[str] | None:
    if value is None or value.strip() == "":
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def _load_csv(path: Path) -> np.ndarray:
    data = np.genfromtxt(path, delimiter=",", names=True, dtype=float, encoding="utf-8")
    if data.size == 0:
        raise ValueError(f"No rows found in {path}")
    if data.ndim == 0:
        data = np.array([data], dtype=data.dtype)
    return data


def _to_matrix(data: np.ndarray, cols: Sequence[str]) -> np.ndarray:
    missing = [c for c in cols if c not in data.dtype.names]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")
    return np.column_stack([data[c] for c in cols]).astype(float)


def _infer_feature_cols(all_cols: Sequence[str], target_col: str | None, context_cols: Sequence[str] | None) -> list[str]:
    excluded = set(context_cols or [])
    if target_col:
        excluded.add(target_col)
    return [c for c in all_cols if c not in excluded]


def cmd_train(args: argparse.Namespace) -> None:
    csv_path = Path(args.train_csv)
    model_path = Path(args.model_out)

    data = _load_csv(csv_path)
    all_cols = list(data.dtype.names or [])

    context_cols = _parse_cols(args.context_cols)
    feature_cols = _parse_cols(args.feature_cols)
    if feature_cols is None:
        feature_cols = _infer_feature_cols(all_cols, args.target_col, context_cols)

    if args.target_col not in all_cols:
        raise ValueError(f"Target column '{args.target_col}' not found in CSV")

    X = _to_matrix(data, feature_cols)
    y = np.asarray(data[args.target_col], dtype=float)
    Z = _to_matrix(data, context_cols) if context_cols else None

    model = AdaptiveWeightedSystem()
    model.fit(X, y, Z)
    model.save(model_path)

    print("trained")
    print(f"model={model_path}")
    print(f"rows={X.shape[0]}")
    print(f"features={feature_cols}")
    print(f"context={context_cols if context_cols else 'auto'}")


def cmd_predict(args: argparse.Namespace) -> None:
    csv_path = Path(args.input_csv)
    model_path = Path(args.model_in)
    pred_out = Path(args.pred_out)

    data = _load_csv(csv_path)
    all_cols = list(data.dtype.names or [])

    context_cols = _parse_cols(args.context_cols)
    feature_cols = _parse_cols(args.feature_cols)
    if feature_cols is None:
        feature_cols = _infer_feature_cols(all_cols, None, context_cols)

    X = _to_matrix(data, feature_cols)
    Z = _to_matrix(data, context_cols) if context_cols else None

    model = AdaptiveWeightedSystem.load(model_path)
    preds = model.predict(X, Z)
    assert isinstance(preds, np.ndarray)

    pred_out.parent.mkdir(parents=True, exist_ok=True)
    with pred_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["prediction"])
        for p in preds:
            writer.writerow([float(p)])

    print("predicted")
    print(f"model={model_path}")
    print(f"input={csv_path}")
    print(f"predictions={pred_out}")
    print(f"rows={X.shape[0]}")


def cmd_ingest(args: argparse.Namespace) -> None:
    source_path = Path(args.source)
    index_path = Path(args.index_out)

    index = build_index(source_path, chunk_size=args.chunk_size, overlap=args.chunk_overlap)
    save_index(index, index_path)

    print("indexed")
    print(f"source={source_path}")
    print(f"index={index_path}")
    print(f"chunks={len(index.chunks)}")
    print(f"vocab_terms={len(index.vocab)}")


def cmd_search(args: argparse.Namespace) -> None:
    index_path = Path(args.index_in)
    index = load_index(index_path)
    results = search_index(index, query=args.query, top_k=args.top_k)

    payload = [
        {
            "rank": r.rank,
            "score": round(r.score, 6),
            "source": r.source,
            "text": r.text,
        }
        for r in results
    ]

    if args.out_json:
        out_path = Path(args.out_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("search_results")
    print(f"index={index_path}")
    print(f"query={args.query}")
    print(f"count={len(results)}")
    for r in results:
        print(f"[{r.rank}] score={r.score:.4f} source={r.source}")
        print(r.text[:300].replace("\n", " "))
        print("---")


def cmd_ask(args: argparse.Namespace) -> None:
    index_path = Path(args.index_in)
    index = load_index(index_path)
    results = search_index(index, query=args.query, top_k=args.top_k)

    answer = ask_with_context(
        query=args.query,
        results=results,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
    )
    print("answer")
    print(answer)


def cmd_plugin(args: argparse.Namespace) -> None:
    if args.name == "ready_player_one":
        result = bootstrap_ready_player_one(Path(args.output_dir))
    elif args.name == "ready_player_one_live_ops":
        result = bootstrap_ready_player_one_live_ops(Path(args.output_dir))
    else:
        raise ValueError(f"Unsupported plugin: {args.name}")
    print("plugin_bootstrap_complete")
    print(f"plugin={result.plugin}")
    print(f"profile={result.profile}")
    print(f"output_dir={result.output_dir}")
    print(f"index={result.index_path}")
    print(f"model={result.model_path}")
    print(f"train_csv={result.train_csv}")
    print(f"predict_csv={result.predict_csv}")
    print(f"predictions_csv={result.predictions_csv}")
    print(f"documents={result.document_count}")
    print(f"train_rows={result.train_rows}")
    print(f"predict_rows={result.predict_rows}")


def _post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_contribute(args: argparse.Namespace) -> None:
    base = args.server_url.rstrip("/")
    worker_id = args.worker_id
    processed = 0

    while processed < args.max_jobs:
        try:
            nxt = _post_json(base + "/v1/contrib/task/next", {"worker_id": worker_id})
        except urllib.error.URLError as e:
            raise RuntimeError(f"Cannot reach hosted site: {e}")

        if not nxt.get("has_task"):
            break

        task_id = nxt["task_id"]
        task_type = nxt.get("task_type", "")
        payload = nxt.get("payload", {})

        if task_type == "rpo_match_score":
            score = compute_ready_player_one_score(payload)
            result = {"score": score}
        else:
            # Generic fallback: echo payload hashable size as progress unit.
            result = {"processed_fields": len(payload)}

        submit_payload = {
            "worker_id": worker_id,
            "task_id": task_id,
            "result": result,
        }
        _post_json(base + "/v1/contrib/task/submit", submit_payload)
        processed += 1

    print("contribution_complete")
    print(f"worker_id={worker_id}")
    print(f"processed_jobs={processed}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Use AdaptiveWeightedSystem and retrieval CLI commands")
    sub = parser.add_subparsers(dest="command", required=True)

    train = sub.add_parser("train", help="Train model from CSV and save .pkl")
    train.add_argument("--train-csv", required=True, help="Path to training CSV (header required)")
    train.add_argument("--target-col", required=True, help="Name of target column")
    train.add_argument("--feature-cols", default=None, help="Comma-separated feature columns (default: infer)")
    train.add_argument("--context-cols", default=None, help="Comma-separated context columns for meta-layer")
    train.add_argument("--model-out", default="artifacts/model.pkl", help="Output path for saved model")
    train.set_defaults(func=cmd_train)

    predict = sub.add_parser("predict", help="Run predictions from saved .pkl model")
    predict.add_argument("--model-in", required=True, help="Path to saved model .pkl")
    predict.add_argument("--input-csv", required=True, help="Path to input CSV (header required)")
    predict.add_argument("--feature-cols", default=None, help="Comma-separated feature columns (default: infer)")
    predict.add_argument("--context-cols", default=None, help="Comma-separated context columns for meta-layer")
    predict.add_argument("--pred-out", default="artifacts/predictions.csv", help="Path to write predictions CSV")
    predict.set_defaults(func=cmd_predict)

    ingest = sub.add_parser("ingest", help="Build a local retrieval index from files")
    ingest.add_argument("--source", required=True, help="File or directory with source text files")
    ingest.add_argument("--index-out", default="artifacts/search_index.pkl", help="Output path for index file")
    ingest.add_argument("--chunk-size", type=int, default=140, help="Chunk size in words")
    ingest.add_argument("--chunk-overlap", type=int, default=30, help="Chunk overlap in words")
    ingest.set_defaults(func=cmd_ingest)

    search = sub.add_parser("search", help="Search local index for relevant chunks")
    search.add_argument("--index-in", required=True, help="Path to index file")
    search.add_argument("--query", required=True, help="Search query")
    search.add_argument("--top-k", type=int, default=5, help="Number of results")
    search.add_argument("--out-json", default=None, help="Optional output JSON file for results")
    search.set_defaults(func=cmd_search)

    ask = sub.add_parser("ask", help="Retrieve context and ask an LLM (or return context fallback)")
    ask.add_argument("--index-in", required=True, help="Path to index file")
    ask.add_argument("--query", required=True, help="Question to ask")
    ask.add_argument("--top-k", type=int, default=5, help="Number of retrieved chunks")
    ask.add_argument("--model", default="gpt-4o-mini", help="LLM model name")
    ask.add_argument("--api-key", default=None, help="Optional API key override (else OPENAI_API_KEY)")
    ask.add_argument("--base-url", default=None, help="Optional OpenAI-compatible base URL")
    ask.set_defaults(func=cmd_ask)

    plugin = sub.add_parser("plugin", help="Run built-in bootstrap plugins")
    plugin.add_argument(
        "--name",
        required=True,
        choices=["ready_player_one", "ready_player_one_live_ops"],
        help="Plugin name",
    )
    plugin.add_argument(
        "--output-dir",
        default="artifacts/ready_player_one",
        help="Directory for generated docs, index, model, and CSV files",
    )
    plugin.set_defaults(func=cmd_plugin)

    contribute = sub.add_parser("contribute", help="Join hosted volunteer compute and process queued tasks")
    contribute.add_argument("--server-url", required=True, help="Hosted API base URL")
    contribute.add_argument("--worker-id", required=True, help="Unique worker identifier")
    contribute.add_argument("--max-jobs", type=int, default=25, help="Max jobs to process this run")
    contribute.set_defaults(func=cmd_contribute)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
