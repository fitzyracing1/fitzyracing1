# Autonomous Web Agent (Modular + Re-trainable)

This project is a bounded-autonomy software agent that can:
- Propose and track objectives
- Navigate the web (static fetch + optional browser mode)
- Extract findings
- Score confidence
- Produce reports
- Be trained on one specific task now and re-trained later on new tasks

## Why this design works for your goal
The core engine stays task-agnostic. Task-specific behavior is isolated in task modules and profiles.
That lets you train one task today without locking the system to only that task.

## Project layout
- `src/agent/main.py`: CLI entrypoint
- `src/agent/runner.py`: autonomous loop orchestration
- `src/agent/objectives.py`: objective generation and prioritization
- `src/agent/fetchers.py`: static + optional browser navigation
- `src/agent/extract.py`: extraction and scoring helpers
- `src/agent/store.py`: SQLite memory and run history
- `src/agent/reporter.py`: digest report generation
- `src/agent/tasks/`: task plugins

## Quick start
1. Create a virtual environment and install dependencies:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Optional (for browser mode):
   - `python -m playwright install chromium`
3. Run one cycle:
   - `PYTHONPATH=src python -m agent.main run --task trend_watch --cycles 1`
4. Run with Day 1 mission contract and thresholds:
   - `PYTHONPATH=src python -m agent.main run --task trend_watch --cycles 3 --interval 10 --mission-name daily_trend_intel --mission-statement "Track high-signal AI tooling changes daily with low false positives." --min-confidence 0.55 --min-findings 2 --max-error-rate 0.35`
5. Run with Day 2 loop hardening controls:
   - `PYTHONPATH=src python -m agent.main run --task trend_watch --cycles 3 --interval 10 --max-fetches-per-cycle 12 --max-retries-per-target 2 --retry-backoff-s 0.7 --max-consecutive-failures 6`
6. Run continuous mode:
   - `PYTHONPATH=src python -m agent.main run --task trend_watch --cycles 20 --interval 20`
7. Train/tune a task profile with feedback weights:
   - `PYTHONPATH=src python -m agent.main train --task trend_watch --novelty 1.2 --reliability 1.5 --speed 0.8`
8. Generate latest report:
   - `PYTHONPATH=src python -m agent.main report`
9. Run benchmark and record baseline metrics:
   - `PYTHONPATH=src python -m agent.main benchmark --task trend_watch --cycles 3`
10. Run domain-specific benchmark profile example:
   - `PYTHONPATH=src python -m agent.main benchmark --task software_solver --cycles 3 --mission-name enterprise_solution_builder --mission-statement "Find high-leverage software opportunities with measurable business impact."`
11. Run with policy/risk gates:
   - `PYTHONPATH=src python -m agent.main run --task software_solver --cycles 5 --min-accept-confidence 0.5 --max-policy-violations-per-cycle 2`
12. Run Day 8 regression check against forgetting:
   - `PYTHONPATH=src python -m agent.main regression-check --reference-task trend_watch --candidate-task software_solver --cycles 3 --max-pass-rate-drop 0.15`
13. Run Day 9 stability check for drift diagnostics:
   - `PYTHONPATH=src python -m agent.main stability-check --task software_solver --run-cycles 6 --recent-window 6 --baseline-window 6`
14. Run Day 10 release readiness check:
   - `PYTHONPATH=src python -m agent.main release-check --task software_solver --preset conservative`
15. Generate Day 10 operator runbook:
   - `PYTHONPATH=src python -m agent.main runbook --task software_solver --preset conservative`
16. Run persistent monetization loop (continuous lead export):
   - `PYTHONPATH=src python -m agent.main money-loop --task trend_watch --cycles-per-iteration 3 --interval 10 --sleep-between-iterations 300 --min-lead-confidence 0.6 --export-path logs/revenue_leads.csv`
17. Run generalized software-solver scope:
   - `PYTHONPATH=src python -m agent.main money-loop --task software_solver --cycles-per-iteration 3 --interval 10 --sleep-between-iterations 300 --min-lead-confidence 0.6 --export-path logs/revenue_leads.csv --usd-per-score-point 120`
18. Generate a generic software product specification:
   - `PYTHONPATH=src python -m agent.main generate-spec --product-name "Workflow Automation Suite" --output-dir generated_software --mission-statement "Build production software that automates a high-value workflow."`
19. Generate a generic software scaffold:
   - `PYTHONPATH=src python -m agent.main generate-code --product-name "Workflow Automation Suite" --output-dir generated_software`
20. Run tests for a generated software project:
   - `PYTHONPATH=src python -m agent.main run-tests --project-dir generated_software/workflow_automation_suite`
21. Package a generated software project:
   - `PYTHONPATH=src python -m agent.main package-release --project-dir generated_software/workflow_automation_suite --artifact-dir release_artifacts`
22. Auto-submit generated code changes:
   - `PYTHONPATH=src python -m agent.main auto-submit --repo-dir . --branch auto/submission --commit-message "Automated software submission" --push`
23. Export payout-ready ledger rows (masked destination fields):
   - `PYTHONPATH=src python -m agent.main export-payout --status open --limit 200 --output-path logs/payout_export.csv --mark-as-exported`
24. Draft client-ready proposals from monetization ledger:
   - `PYTHONPATH=src python -m agent.main draft-proposals --status open --limit 100 --output-dir logs/proposals --mark-as-proposed`
25. Enable auto-proposal drafting inside the persistent loop:
   - `PYTHONPATH=src python -m agent.main money-loop --task software_solver --cycles-per-iteration 3 --interval 10 --sleep-between-iterations 300 --min-lead-confidence 0.6 --export-path logs/revenue_leads.csv --usd-per-score-point 120 --auto-draft-proposals --proposal-dir logs/proposals`
26. Revalue existing ledger entries to high-ticket estimates:
   - `PYTHONPATH=src python -m agent.main revalue-ledger --status open --limit 1000 --base-project-value 40000 --max-project-value 750000`
27. Generate code and push for every proposal (one branch per proposal):
   - `PYTHONPATH=src python -m agent.main execute-proposals --proposal-dir logs/proposals --output-dir generated_software/proposal_projects --artifact-dir release_artifacts --branch-prefix proposal --run-tests --package --push`
28. Start the web app dashboard (results + retraining command UI):
   - `PYTHONPATH=src python -m agent.main web --host 0.0.0.0 --port 8080`
   - Open: `http://localhost:8080`

Payout configuration placeholders (set via environment variables, do not hardcode real account/routing numbers):
- `PAYOUT_DESTINATION_LABEL` (example: `primary_business_account`)
- `PAYOUT_ACCOUNT_HOLDER` (example: `PLACEHOLDER_NAME`)
- `PAYOUT_ROUTING_MASKED` (example: `***-PLACEHOLDER`)
- `PAYOUT_ACCOUNT_MASKED` (example: `***-PLACEHOLDER`)

## Software Production Mode
Use this mode when you want the system to produce software artifacts for a generic software problem.

1. Generate product specification:
   - `PYTHONPATH=src python -m agent.main generate-spec --product-name "Workflow Automation Suite" --output-dir generated_software --mission-statement "Build production software that automates a high-value workflow."`
2. Generate code scaffold:
   - `PYTHONPATH=src python -m agent.main generate-code --product-name "Workflow Automation Suite" --output-dir generated_software`
3. Run generated tests:
   - `PYTHONPATH=src python -m agent.main run-tests --project-dir generated_software/workflow_automation_suite`
4. Package release artifact:
   - `PYTHONPATH=src python -m agent.main package-release --project-dir generated_software/workflow_automation_suite --artifact-dir release_artifacts`

Generated outputs:
- Spec: `generated_software/workflow_automation_suite_spec.md`
- Code project: `generated_software/workflow_automation_suite/`
- Test log: `generated_software/workflow_automation_suite/test_output.txt`
- Release zip: `release_artifacts/workflow_automation_suite.zip`

## Vertical Plugin Example
Use this mode when you want the system to produce software artifacts for a specific business domain.

1. Run domain software intelligence cycle:
   - `PYTHONPATH=src python -m agent.main run --task software_solver --preset conservative --cycles 1`
2. Generate product specification:
   - `PYTHONPATH=src python -m agent.main generate-spec --product-name "Operations Workflow Suite" --output-dir generated_software --mission-statement "Build production software that automates high-value business workflows."`
3. Generate code scaffold:
   - `PYTHONPATH=src python -m agent.main generate-code --product-name "Operations Workflow Suite" --output-dir generated_software`
4. Run generated tests:
   - `PYTHONPATH=src python -m agent.main run-tests --project-dir generated_software/operations_workflow_suite`
5. Package release artifact:
   - `PYTHONPATH=src python -m agent.main package-release --project-dir generated_software/operations_workflow_suite --artifact-dir release_artifacts`

Generated outputs:
- Spec: `generated_software/operations_workflow_suite_spec.md`
- Code project: `generated_software/operations_workflow_suite/`
- Test log: `generated_software/operations_workflow_suite/test_output.txt`
- Release zip: `release_artifacts/operations_workflow_suite.zip`

## Day 1 outputs
- Weighted model profile: establish baseline feature set and initialize default scoring weights (novelty=1.0, reliability=1.0, speed=1.0).
- Mission contract is enforced per run using threshold flags.
- Each cycle records metrics in SQLite: findings, average confidence, error count, action count, and pass/fail.
- Report includes the latest mission scoring snapshot.

## Day 2 outputs
- Weighted model profile: apply deterministic caps and retry penalties so operational stability influences effective scoring weight.
- Deterministic action caps via max fetch budget per cycle.
- Retry/backoff per target fetch.
- Circuit-breaker stop when consecutive failures exceed threshold.
- Failure categorization logged per cycle (policy, timeout, network, parse, unknown).

## Day 3 outputs
- Weighted model profile: enforce deduplication and lifecycle weighting so repeated low-value signals are down-weighted.
- Finding deduplication by objective+source+title fingerprint.
- Objective lifecycle transitions enforced: pending -> in_progress -> done/deferred/failed.
- Audit summaries in report: event level counts and objective status counts.

## Day 4 outputs
- Weighted model profile: calibrate reliability weight using extraction quality and normalized URL provenance.
- URL normalization for policy checks and tracking (drops fragments and utm params).
- Extraction quality guards using text length and quality score thresholds.
- Reliability calibration uses source reliability plus extraction quality.
- Final source URLs are persisted from actual fetch results.

## Day 5 outputs
- Weighted model profile: benchmark-driven profile tuning sets task-specific weights from measurable pass-rate and confidence baselines.
- Benchmark command records baseline metrics: pass rate, avg findings, avg confidence, avg error rate.
- Benchmark history is persisted in SQLite and summarized in reports.

## Day 6 outputs
- Weighted model profile: explainability traces map every accept/reject decision back to the active weighted score components.
- Decision trace logging for each target attempt and acceptance/rejection outcome.
- Confidence band summaries (high/medium/low) in reports.
- Recommended next actions section based on benchmark and confidence/error trends.

## Day 7 outputs
- Weighted model profile: policy and risk gates become hard constraints, forcing low-trust or unsafe signals to zero effective weight.
- Policy block rules for URL/content keyword matches.
- Confidence risk gate rejects low-confidence findings before persistence.
- Explicit stop condition can halt run when policy violation threshold is reached.
- Halt events are persisted and summarized in reports.

## Day 8 outputs
- Weighted model profile: cross-task regression checks preserve shared core weights to reduce catastrophic forgetting.
- Second task plugin (`security_watch`) for multi-task readiness.
- Shared-skill overlap checks between reference and candidate tasks.
- Regression-check command compares pass-rate drop to anti-forgetting threshold.
- Regression results are persisted and summarized in reports.

## Day 9 outputs
- Weighted model profile: stability diagnostics track drift and auto-recommend rebalancing when recent windows diverge from baseline.
- Stability-check command for long-run drift detection using recent vs baseline windows.
- Automatic tuning recommendations based on confidence/error and pass-rate drift.
- Stability records persisted in SQLite and summarized in reports.

## Day 10 outputs
- Weighted model profile: complete weighted model system is production-ready with tuned presets, readiness scoring, and operator runbooks.
- Deployment-ready presets: balanced, conservative, aggressive.
- Release-check command computes readiness score using benchmark, regression, and stability signals.
- Operator runbook command generates a markdown runbook with preflight, commands, and escalation guidance.
- Release checks are persisted and summarized in reports.

## Safety controls
- Domain allowlist enforcement
- Max actions per cycle
- Robots and terms compliance is your responsibility before deployment
- No login/credential automation built in

## Notes
- This is an autonomy framework, not unrestricted self-direction.
- Keep objective proposals bounded by your policy rules.
