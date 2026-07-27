# Adaptive Weighted Models

This project implements a retrainable plug-in architecture that combines multiple weighted model families through a context-conditioned meta-weighting layer.

## Implemented Module Families

- Static weighted sum
- Time-decay weighted
- Risk/cost weighted
- Hierarchical weighted
- Ensemble weighted
- Online adaptive weighted

Each module outputs a prediction `s_k`.
The meta-layer learns context-based weights:

alpha_k = exp(g_k(z)) / sum_j exp(g_j(z))

Final output:

y_hat = sum_k alpha_k * s_k

## Features

- Warm-start retraining for all modules and meta-layer
- Context-aware softmax gating
- Drift detection based on rising recent error
- Auto-retraining on drift with retained history
- Model persistence with save/load
- Tunable drift sensitivity and retrain lookback window

## Structure

- `weighted_models/modules.py`: module implementations
- `weighted_models/meta.py`: context-to-softmax meta-layer
- `weighted_models/system.py`: end-to-end training, prediction, retraining, drift handling
- `weighted_models/drift.py`: drift detector
- `examples/run_demo.py`: runnable demo

## Quick Start

Use the model directly on your own data (no demo):

1. Train from a CSV and save model:

```powershell
python -m weighted_models train --train-csv .\data\train.csv --target-col target --feature-cols f1,f2,f3,f4 --context-cols regime,quality,segment --model-out .\artifacts\model.pkl
```

2. Predict from a saved model:

```powershell
python -m weighted_models predict --model-in .\artifacts\model.pkl --input-csv .\data\predict.csv --feature-cols f1,f2,f3,f4 --context-cols regime,quality,segment --pred-out .\artifacts\predictions.csv
```

Notes:

- CSV files must include a header row.
- If you omit `--feature-cols`, features are inferred from all non-target, non-context columns.
- If you omit `--context-cols`, the system auto-generates context features.

Retrieval + LLM workflow (ingest/search/ask):

1. Build local search index from docs:

```powershell
python -m weighted_models ingest --source .\docs --index-out .\artifacts\search_index.pkl
```

2. Search top matching chunks:

```powershell
python -m weighted_models search --index-in .\artifacts\search_index.pkl --query "how does drift retraining work" --top-k 5
```

3. Ask with retrieved context (uses `OPENAI_API_KEY` if set):

```powershell
python -m weighted_models ask --index-in .\artifacts\search_index.pkl --query "Explain drift-triggered retraining" --top-k 5 --model gpt-4o-mini
```

If no `OPENAI_API_KEY` is set, `ask` returns the retrieved context so you can still inspect search quality locally.

Plugin bootstrap (immediate Ready Player One setup):

```powershell
python -m weighted_models plugin --name ready_player_one --output-dir .\artifacts\ready_player_one
```

Live-ops profile (seasonal drift + meta shifts + raid role balancing):

```powershell
python -m weighted_models plugin --name ready_player_one_live_ops --output-dir .\artifacts\ready_player_one_live_ops
```

This single command generates:

- themed docs for retrieval index
- `train.csv` and `predict.csv`
- trained model artifact
- predictions CSV
- search index artifact

Included mechanics in generated data:

- OASIS factions and avatar roles (encoded feature columns)
- quest progression scoring
- IOI threat and risk weighting
- team raid matchmaking features

Live-ops profile adds:

- seasonal leaderboard drift signals
- faction meta shift signals
- raid role balancing dynamics over time

Then you can run internet/API-ready retrieval and model calls immediately on those generated artifacts.

From project root:

```powershell
python -m examples.run_demo
```

Run automated tests:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Build deployable artifacts (wheel + source tarball):

```powershell
python -m pip install --upgrade build
python -m build
```

One-command Windows deploy flow (test + build + install locally):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1 -Mode local
```

Artifacts are generated in `dist/`.

Install the built wheel locally for smoke testing:

```powershell
python -m pip install --force-reinstall dist/adaptive_weighted_models-0.1.0-py3-none-any.whl
```

Version bump automation:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bump_version.ps1 -Part patch
```

Dry run a version bump without changing files:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bump_version.ps1 -Part minor -DryRun
```

If your environment has no NumPy installed:

```powershell
pip install numpy
```

## Tuning

You can tune responsiveness with:

- `DriftConfig.window_size`: baseline/recent comparison window
- `DriftConfig.min_samples`: minimum recent errors before evaluating drift
- `DriftConfig.relative_increase_threshold`: drift trigger threshold
- `AdaptiveSystemConfig.retrain_lookback`: number of most recent rows used during auto-retrain
- `AdaptiveSystemConfig.retrain_min_samples`: minimum rows required to retrain

## Deploy

### Internet API Deployment (Public HTTP Service)

If you want people to use this over the internet (not local CLI), deploy the API service.

Run API locally first:

```powershell
python -m pip install ".[server]"
python -m uvicorn weighted_models.api:app --host 0.0.0.0 --port 8000
```

Docker run locally:

```powershell
docker build -t adaptive-weighted-models-api .
docker run -p 8000:8000 adaptive-weighted-models-api
```

Public cloud deployment (Render/Railway/Fly.io/Azure):

1. Push repository to GitHub.
2. Create a new web service from this repo.
3. Deploy using Dockerfile in repo root.
4. Set env vars in the host dashboard if needed:
	- `OPENAI_API_KEY` (optional, for `/v1/ask` LLM answers)
	- `OPENAI_BASE_URL` (optional, for OpenAI-compatible providers)

For heavy self-hosted Grok-1 style deployment guidance, see:

- `docs/GROK1_SELF_HOSTING.md`

Reference model repo for self-hosting experiments:

- `https://github.com/xai-org/grok-1`

API endpoints after deploy:

- `GET /health`
- `POST /v1/index/build`
- `POST /v1/search`
- `POST /v1/ask`
- `POST /v1/contrib/tasks/seed`
- `POST /v1/contrib/task/next`
- `POST /v1/contrib/task/submit`
- `GET /v1/contrib/stats`

Volunteer compute mode (many computers contribute):

1. Host runs task seeding:

```powershell
curl -X POST "https://YOUR-APP-URL/v1/contrib/tasks/seed" -H "Content-Type: application/json" -d "{\"task_type\":\"rpo_match_score\",\"payloads\":[{\"agility\":0.8,\"focus\":0.7,\"teamwork\":0.6,\"resource_efficiency\":0.7,\"risk_control\":0.8,\"latency_ms\":55,\"ioi_risk_weight\":0.2,\"team_raid_matchmaking\":0.75,\"quest_progression_score\":0.68}]}"
```

2. Contributors run on their own computers:

```powershell
python -m weighted_models contribute --server-url https://YOUR-APP-URL --worker-id player-node-001 --max-jobs 100
```

3. Host checks progress:

```powershell
curl "https://YOUR-APP-URL/v1/contrib/stats"
```

Example build-index request:

```powershell
curl -X POST "https://YOUR-APP-URL/v1/index/build" -H "Content-Type: application/json" -d "{\"index_name\":\"public\",\"documents\":[{\"source\":\"doc-1\",\"text\":\"Drift retraining uses recent error increase to trigger warm-start updates.\"}]}"
```

Example ask request:

```powershell
curl -X POST "https://YOUR-APP-URL/v1/ask" -H "Content-Type: application/json" -d "{\"index_name\":\"public\",\"query\":\"How does retraining trigger?\",\"top_k\":3,\"model\":\"gpt-4o-mini\"}"
```

### Public Online Deployment (Anyone Can Install)

Goal: make this installable globally with:

```powershell
pip install adaptive-weighted-models
```

One-time setup:

1. Push this repo to GitHub (replace placeholder URLs in `pyproject.toml` with your real repo URL).
2. Create a project on PyPI with the same package name (`adaptive-weighted-models`).
3. In PyPI, configure Trusted Publishing for this GitHub repository.
4. In GitHub, allow Actions to publish to environment `pypi`.
5. Optional dry-run path: configure environment `testpypi` too.

Then publish:

1. Create a GitHub Release (tag like `v0.1.0`).
2. Workflow [ .github/workflows/publish-pypi.yml ] builds, tests, and publishes automatically.
3. Anyone can install with `pip install adaptive-weighted-models`.

Manual workflow trigger options:

- `testpypi` for safe trial publishing
- `pypi` for public release

For internal deployment (artifact copy):

1. Build with `python -m build`.
2. Copy the `.whl` from `dist/` to the target machine.
3. Install with `pip install adaptive_weighted_models-0.1.0-py3-none-any.whl`.
4. Run your application that imports `weighted_models`.

One-command artifact-only build (no local install):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1 -Mode artifact
```

For package index deployment (PyPI/private registry):

1. Build with `python -m build`.
2. Upload with Twine: `python -m twine upload dist/*`.
3. On target environments: `pip install adaptive-weighted-models`.

Optional one-command publish with Twine:

```powershell
# PyPI
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1 -Mode publish -Registry pypi

# TestPyPI
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1 -Mode publish -Registry testpypi

# Private registry
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1 -Mode publish -Registry private -RepositoryUrl "https://your-registry.example.com/repository/pypi"
```

Combined bump + publish example:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1 -Mode publish -Registry pypi -Bump patch
```
