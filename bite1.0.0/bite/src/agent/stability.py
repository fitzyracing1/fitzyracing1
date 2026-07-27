from typing import Any


def _window_avg(items: list[dict[str, Any]], key: str) -> float:
    if not items:
        return 0.0
    return sum(float(it.get(key, 0.0)) for it in items) / len(items)


def _window_error_rate(items: list[dict[str, Any]]) -> float:
    if not items:
        return 0.0
    total = 0.0
    for it in items:
        actions = int(it.get("action_count", 0))
        errors = int(it.get("error_count", 0))
        total += (errors / actions) if actions > 0 else 0.0
    return total / len(items)


def analyze_stability(
    metrics_desc: list[dict[str, Any]],
    baseline_window: int,
    recent_window: int,
) -> dict[str, Any]:
    if baseline_window < 1 or recent_window < 1:
        raise ValueError("baseline_window and recent_window must be >= 1")

    recent = metrics_desc[:recent_window]
    baseline = metrics_desc[recent_window : recent_window + baseline_window]

    recent_pass = _window_avg(recent, "pass")
    baseline_pass = _window_avg(baseline, "pass") if baseline else recent_pass
    drift = baseline_pass - recent_pass
    recent_conf = _window_avg(recent, "avg_confidence")
    recent_err = _window_error_rate(recent)

    if drift <= 0.08 and recent_err <= 0.30:
        status = "stable"
    elif drift <= 0.18 and recent_err <= 0.45:
        status = "warning"
    else:
        status = "critical"

    recs: list[str] = []
    if drift > 0.08:
        recs.append("Reduce scope and rerun a short benchmark to isolate drifted objectives.")
    if recent_conf < 0.55:
        recs.append("Increase extraction quality threshold and tune keywords for precision.")
    if recent_err > 0.35:
        recs.append("Raise retries for high-value sources and lower per-cycle fetch budget.")
    if not recs:
        recs.append("Keep current profile and extend run length for confidence.")

    return {
        "status": status,
        "baseline_pass_rate": baseline_pass,
        "recent_pass_rate": recent_pass,
        "pass_rate_drift": drift,
        "recent_avg_confidence": recent_conf,
        "recent_avg_error_rate": recent_err,
        "recommendations": recs,
    }
