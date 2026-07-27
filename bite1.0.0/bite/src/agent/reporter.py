from pathlib import Path

from .store import MemoryStore


def _recommended_actions(task_name: str, avg_error_rate: float, avg_confidence: float, pass_rate: float) -> list[str]:
    actions: list[str] = []
    if avg_error_rate > 0.35:
        actions.append("Reduce target set to highest-reliability sources and increase retries for key domains.")
    if avg_confidence < 0.55:
        actions.append("Raise extraction quality threshold and tune task keywords for higher topical precision.")
    if pass_rate < 0.6:
        actions.append("Run benchmark for 5 cycles and adjust profile weights toward reliability before scaling.")

    if task_name == "aerospace_software":
        actions.append("Generate specification and scaffold first, then verify unit tests before packaging releases.")
        actions.append("Favor deterministic interfaces and traceable risk scoring for mission-planning modules.")

    if not actions:
        actions.append("Maintain current profile and expand cycle count to validate stability over longer runs.")
    return actions


def generate_markdown_report(store: MemoryStore, output_path: Path) -> str:
    objectives = store.list_active_objectives(limit=20)
    events = store.recent_events(limit=40)
    metrics = store.recent_cycle_metrics(limit=20)
    benchmarks = store.recent_task_benchmarks(limit=10)
    traces = store.recent_decision_traces(limit=15)
    halts = store.recent_run_halts(limit=5)
    regressions = store.recent_regression_checks(limit=5)
    stability = store.recent_stability_checks(limit=5)
    release_checks = store.recent_release_checks(limit=5)
    event_levels = store.event_level_summary(limit=200)
    status_counts = store.objective_status_summary()
    latest_task = metrics[0]["task_name"] if metrics else None
    band_counts = store.confidence_band_summary(task_name=latest_task, limit=200)

    lines: list[str] = []
    lines.append("# Autonomous Web Agent Report")
    lines.append("")
    lines.append("## Mission Scoring")
    if not metrics:
        lines.append("- No cycle metrics available yet.")
    else:
        latest = metrics[0]
        lines.append(f"- Mission: **{latest['mission_name']}**")
        lines.append(
            f"- Latest Cycle: #{latest['cycle_index']} pass={bool(latest['pass'])} findings={latest['findings_count']} "
            f"avg_conf={latest['avg_confidence']:.2f} errors={latest['error_count']}/{latest['action_count']}"
        )
        lines.append(f"- Notes: {latest['notes']}")

    lines.append("")
    lines.append("## Day 5 Benchmarks")
    if not benchmarks:
        lines.append("- No benchmark records yet.")
    else:
        latest = benchmarks[0]
        lines.append(
            f"- Latest: task={latest['task_name']} profile={latest['profile_name']} cycles={latest['cycles']} "
            f"pass_rate={latest['pass_rate']:.2f} avg_findings={latest['avg_findings']:.2f} "
            f"avg_conf={latest['avg_confidence']:.2f} avg_error_rate={latest['avg_error_rate']:.2f}"
        )
        lines.append(f"- Notes: {latest['notes']}")

    lines.append("")
    lines.append("## Day 8 Multi-Task Readiness")
    if not regressions:
        lines.append("- No regression checks recorded yet.")
    else:
        latest_reg = regressions[0]
        lines.append(
            f"- Latest Regression: passed={bool(latest_reg['passed'])} "
            f"reference={latest_reg['reference_task']} candidate={latest_reg['candidate_task']} "
            f"pass_rate_drop={latest_reg['pass_rate_drop']:.2f} shared_skills={latest_reg['shared_skills']}"
        )
        lines.append(f"- Notes: {latest_reg['notes']}")

    lines.append("")
    lines.append("## Day 9 Stability")
    if not stability:
        lines.append("- No stability checks recorded yet.")
    else:
        latest_stability = stability[0]
        lines.append(
            f"- Latest Stability: task={latest_stability['task_name']} status={latest_stability['status']} "
            f"drift={latest_stability['pass_rate_drift']:.2f} "
            f"baseline_pass={latest_stability['baseline_pass_rate']:.2f} "
            f"recent_pass={latest_stability['recent_pass_rate']:.2f}"
        )
        lines.append(
            f"- Recent Quality: avg_conf={latest_stability['recent_avg_confidence']:.2f} "
            f"avg_error_rate={latest_stability['recent_avg_error_rate']:.2f}"
        )
        lines.append(f"- Recommendations: {latest_stability['recommendations']}")
        lines.append(f"- Notes: {latest_stability['notes']}")

    lines.append("")
    lines.append("## Day 10 Release Hardening")
    if not release_checks:
        lines.append("- No release checks recorded yet.")
    else:
        latest_release = release_checks[0]
        lines.append(
            f"- Latest Release Check: passed={bool(latest_release['passed'])} "
            f"task={latest_release['task_name']} preset={latest_release['preset']} "
            f"readiness_score={latest_release['readiness_score']:.2f}"
        )
        lines.append(
            f"- Inputs: benchmark_pass_rate={latest_release['benchmark_pass_rate']:.2f} "
            f"regression_passed={bool(latest_release['regression_passed'])} "
            f"stability_status={latest_release['stability_status']}"
        )
        lines.append(f"- Notes: {latest_release['notes']}")

    lines.append("")
    lines.append("## Day 7 Policy & Stop Conditions")
    policy_blocks = [t for t in traces if str(t["action"]).startswith("policy_block")]
    lines.append(f"- Policy Block Events (recent): {len(policy_blocks)}")
    if halts:
        last_halt = halts[0]
        lines.append(
            f"- Last Halt: cycle={last_halt['cycle_index']} task={last_halt['task_name']} reason={last_halt['reason']}"
        )
    else:
        lines.append("- Last Halt: none")

    lines.append("")
    lines.append("## Day 6 Explainability")
    lines.append(
        "- Confidence Bands: "
        f"high={band_counts.get('high', 0)} medium={band_counts.get('medium', 0)} low={band_counts.get('low', 0)}"
    )
    if traces:
        lines.append("- Recent Decision Traces:")
        for trace in traces[:8]:
            lines.append(
                f"  - [{trace['ts']}] task={trace['task_name']} objective={trace['objective_id']} "
                f"target={trace['target_name']} action={trace['action']} band={trace['confidence_band']} "
                f"outcome={trace['outcome']}"
            )
            lines.append(f"    - rationale: {trace['rationale']}")
    else:
        lines.append("- Recent Decision Traces: none")

    lines.append("")
    lines.append("## Recommended Next Actions")
    if benchmarks:
        b = benchmarks[0]
        recommendations = _recommended_actions(
            task_name=str(b["task_name"]),
            avg_error_rate=float(b["avg_error_rate"]),
            avg_confidence=float(b["avg_confidence"]),
            pass_rate=float(b["pass_rate"]),
        )
    else:
        recommendations = [
            "Run a baseline benchmark for the active task before changing profile weights.",
            "After baseline, adjust one weight at a time and compare pass rate and confidence deltas.",
        ]
    for item in recommendations:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Day 3 Audit Summary")
    lines.append(
        "- Event Levels: "
        f"INFO={event_levels.get('INFO', 0)} WARN={event_levels.get('WARN', 0)} ERROR={event_levels.get('ERROR', 0)}"
    )
    lines.append(
        "- Objective Status Counts: "
        f"pending={status_counts.get('pending', 0)} in_progress={status_counts.get('in_progress', 0)} "
        f"deferred={status_counts.get('deferred', 0)} done={status_counts.get('done', 0)} failed={status_counts.get('failed', 0)}"
    )

    lines.append("")
    lines.append("## Active Objectives")
    if not objectives:
        lines.append("- None")
    for obj in objectives:
        lines.append(f"- **{obj.title}** (`{obj.id}`) priority={obj.priority} status={obj.status}")
        findings = store.get_findings_for_objective(obj.id, limit=3)
        for f in findings:
            lines.append(f"  - [{f.title}]({f.source_url}) conf={f.confidence:.2f} novelty={f.novelty:.2f}")
            lines.append(f"    - {f.snippet}")

    lines.append("")
    lines.append("## Recent Events")
    if not events:
        lines.append("- None")
    else:
        for evt in events:
            lines.append(f"- {evt['ts']} [{evt['level']}] {evt['message']}")

    content = "\n".join(lines) + "\n"
    output_path.write_text(content, encoding="utf-8")
    return content
