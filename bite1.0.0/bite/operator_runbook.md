# Operator Runbook: software_solver

- Preset: conservative
- Objective: Execute bounded autonomous scans with policy gates and measurable release checks

## Preflight
- Verify Python environment and dependencies are installed
- Confirm policy blocklists and allowlist are aligned to current mission
- Confirm mission thresholds match deployment risk tolerance

## Commands
- Run: PYTHONPATH=src python -m agent.main run --task software_solver --preset conservative --cycles 3
- Benchmark: PYTHONPATH=src python -m agent.main benchmark --task software_solver --preset conservative --cycles 3
- Stability: PYTHONPATH=src python -m agent.main stability-check --task software_solver --preset conservative --run-cycles 6
- Release: PYTHONPATH=src python -m agent.main release-check --task software_solver --preset conservative

## Latest Signals
- Benchmark: pass_rate=0.00 avg_conf=0.00 avg_error_rate=0.17
- Regression: passed=True pass_rate_drop=0.00
- Stability: status=stable drift=0.00 recommendations=Increase extraction quality threshold and tune keywords for precision.
- Release Check: passed=False readiness_score=0.50 status=stable

## Escalation
- If stability is critical: reduce fetch budget and tighten extraction quality thresholds
- If regression fails: retrain profile or rollback recent tuning
- If policy halts increase: audit target list and blocked keyword sets
