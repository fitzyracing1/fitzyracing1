from pathlib import Path

from .store import MemoryStore


def evaluate_release_readiness(
    benchmark_pass_rate: float,
    regression_passed: bool,
    stability_status: str,
) -> tuple[float, bool, str]:
    stability_score = {
        "stable": 1.0,
        "warning": 0.6,
        "critical": 0.2,
    }.get(stability_status, 0.2)
    regression_score = 1.0 if regression_passed else 0.0
    score = 0.5 * benchmark_pass_rate + 0.3 * regression_score + 0.2 * stability_score
    passed = score >= 0.7 and benchmark_pass_rate >= 0.6 and regression_passed and stability_status != "critical"
    status = "ready" if passed else "not_ready"
    return score, passed, status


def generate_operator_runbook(store: MemoryStore, output_path: Path, task_name: str, preset: str) -> str:
    benchmarks = store.recent_task_benchmarks(task_name=task_name, limit=1)
    regressions = store.recent_regression_checks(limit=1)
    stability = store.recent_stability_checks(task_name=task_name, limit=1)
    release = store.recent_release_checks(task_name=task_name, limit=1)

    lines: list[str] = []
    lines.append(f"# Operator Runbook: {task_name}")
    lines.append("")
    lines.append(f"- Preset: {preset}")
    lines.append("- Objective: Execute bounded autonomous scans with policy gates and measurable release checks")
    lines.append("")
    lines.append("## Preflight")
    lines.append("- Verify Python environment and dependencies are installed")
    lines.append("- Confirm policy blocklists and allowlist are aligned to current mission")
    lines.append("- Confirm mission thresholds match deployment risk tolerance")
    lines.append("")
    lines.append("## Commands")
    lines.append(f"- Run: PYTHONPATH=src python -m agent.main run --task {task_name} --preset {preset} --cycles 3")
    lines.append(f"- Benchmark: PYTHONPATH=src python -m agent.main benchmark --task {task_name} --preset {preset} --cycles 3")
    lines.append(f"- Stability: PYTHONPATH=src python -m agent.main stability-check --task {task_name} --preset {preset} --run-cycles 6")
    lines.append(f"- Release: PYTHONPATH=src python -m agent.main release-check --task {task_name} --preset {preset}")
    lines.append("")
    lines.append("## Latest Signals")
    if benchmarks:
        b = benchmarks[0]
        lines.append(
            f"- Benchmark: pass_rate={b['pass_rate']:.2f} avg_conf={b['avg_confidence']:.2f} avg_error_rate={b['avg_error_rate']:.2f}"
        )
    else:
        lines.append("- Benchmark: missing")

    if regressions:
        r = regressions[0]
        lines.append(
            f"- Regression: passed={bool(r['passed'])} pass_rate_drop={r['pass_rate_drop']:.2f}"
        )
    else:
        lines.append("- Regression: missing")

    if stability:
        s = stability[0]
        lines.append(
            f"- Stability: status={s['status']} drift={s['pass_rate_drift']:.2f} recommendations={s['recommendations']}"
        )
    else:
        lines.append("- Stability: missing")

    if release:
        rel = release[0]
        lines.append(
            f"- Release Check: passed={bool(rel['passed'])} readiness_score={rel['readiness_score']:.2f} status={rel['stability_status']}"
        )
    else:
        lines.append("- Release Check: missing")

    lines.append("")
    lines.append("## Escalation")
    lines.append("- If stability is critical: reduce fetch budget and tighten extraction quality thresholds")
    lines.append("- If regression fails: retrain profile or rollback recent tuning")
    lines.append("- If policy halts increase: audit target list and blocked keyword sets")

    content = "\n".join(lines) + "\n"
    output_path.write_text(content, encoding="utf-8")
    return content
