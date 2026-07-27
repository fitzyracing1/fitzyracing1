import argparse
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

from .config import AgentConfig
from .finance import load_payout_config_from_env, payout_ready_rows, write_payout_export
from .models import TaskProfile
from .proposal_execution import mark_proposal_execution, parse_proposal_source_repo_url, parse_proposal_title
from .proposal import write_competition_proposal_file, write_proposal_file
from .presets import apply_preset
from .revenue import append_leads_csv, estimate_project_value_usd, lead_score
from .release import evaluate_release_readiness, generate_operator_runbook
from .reporter import generate_markdown_report
from .runner import run_agent, task_skill_overlap
from .software_factory import generate_code, generate_spec, package_release, run_tests
from .stability import analyze_stability
from .store import MemoryStore
from .submitter import auto_submit_changes, auto_submit_paths
from .web import run_web_server


TASK_CHOICES = ["trend_watch", "irish_tech_watch", "security_watch", "aerospace_software", "software_solver", "compete_watch"]


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def cmd_run(args: argparse.Namespace) -> None:
    cfg = _build_cfg_from_args(args)
    run_agent(task_name=args.task, cycles=args.cycles, interval_s=args.interval, cfg=cfg)
    print("Run complete.")


def cmd_train(args: argparse.Namespace) -> None:
    cfg = AgentConfig()
    store = MemoryStore(cfg.db_path)
    profile = store.get_task_profile(args.task)
    profile = TaskProfile(
        name=profile.name,
        novelty_weight=args.novelty if args.novelty is not None else profile.novelty_weight,
        reliability_weight=args.reliability if args.reliability is not None else profile.reliability_weight,
        speed_weight=args.speed if args.speed is not None else profile.speed_weight,
        notes=args.notes if args.notes is not None else profile.notes,
    )
    store.upsert_task_profile(profile)
    print(f"Updated profile for task={args.task}: {profile}")


def cmd_report(args: argparse.Namespace) -> None:
    cfg = AgentConfig()
    store = MemoryStore(cfg.db_path)
    content = generate_markdown_report(store, cfg.report_path)
    print(content)


def cmd_benchmark(args: argparse.Namespace) -> None:
    cfg = _build_cfg_from_args(args)

    run_agent(task_name=args.task, cycles=args.cycles, interval_s=args.interval, cfg=cfg)
    store = MemoryStore(cfg.db_path)
    summary = store.summarize_recent_cycle_metrics(task_name=args.task, cycles=args.cycles)
    profile = store.get_task_profile(args.task)
    notes = (
        f"benchmark task={args.task} mission={args.mission_name} samples={int(summary['samples'])}; "
        f"weights(novelty={profile.novelty_weight}, reliability={profile.reliability_weight}, speed={profile.speed_weight})"
    )
    store.save_task_benchmark(
        ts=_ts(),
        task_name=args.task,
        profile_name=profile.name,
        cycles=args.cycles,
        pass_rate=summary["pass_rate"],
        avg_findings=summary["avg_findings"],
        avg_confidence=summary["avg_confidence"],
        avg_error_rate=summary["avg_error_rate"],
        notes=notes,
    )
    print(
        "Benchmark complete "
        f"task={args.task} pass_rate={summary['pass_rate']:.2f} avg_findings={summary['avg_findings']:.2f} "
        f"avg_conf={summary['avg_confidence']:.2f} avg_error_rate={summary['avg_error_rate']:.2f}"
    )


def _build_cfg_from_args(args: argparse.Namespace) -> AgentConfig:
    cfg = AgentConfig(
        mission_name=args.mission_name,
        mission_statement=args.mission_statement,
        min_confidence=args.min_confidence,
        min_findings_per_cycle=args.min_findings,
        max_error_rate=args.max_error_rate,
        max_fetches_per_cycle=args.max_fetches_per_cycle,
        max_retries_per_target=args.max_retries_per_target,
        retry_backoff_s=args.retry_backoff_s,
        max_consecutive_failures=args.max_consecutive_failures,
        min_extracted_chars=args.min_extracted_chars,
        min_extraction_quality=args.min_extraction_quality,
        min_accept_confidence=args.min_accept_confidence,
        max_policy_violations_per_cycle=args.max_policy_violations_per_cycle,
        halt_on_policy_violation_limit=not args.disable_policy_halt,
    )
    return apply_preset(cfg, args.preset)


def cmd_regression_check(args: argparse.Namespace) -> None:
    cfg = _build_cfg_from_args(args)
    store = MemoryStore(cfg.db_path)

    run_agent(task_name=args.reference_task, cycles=args.cycles, interval_s=args.interval, cfg=cfg)
    baseline = store.summarize_recent_cycle_metrics(task_name=args.reference_task, cycles=args.cycles)

    run_agent(task_name=args.candidate_task, cycles=args.cycles, interval_s=args.interval, cfg=cfg)
    candidate = store.summarize_recent_cycle_metrics(task_name=args.candidate_task, cycles=args.cycles)

    overlap = task_skill_overlap(args.reference_task, args.candidate_task)
    drop = baseline["pass_rate"] - candidate["pass_rate"]
    passed = drop <= args.max_pass_rate_drop
    notes = (
        f"shared_skills={overlap['shared_skills']} list={overlap['shared_skill_list']} "
        f"baseline={baseline['pass_rate']:.2f} candidate={candidate['pass_rate']:.2f}"
    )
    store.save_regression_check(
        ts=_ts(),
        reference_task=args.reference_task,
        candidate_task=args.candidate_task,
        baseline_pass_rate=baseline["pass_rate"],
        candidate_pass_rate=candidate["pass_rate"],
        pass_rate_drop=drop,
        shared_skills=int(overlap["shared_skills"]),
        passed=passed,
        notes=notes,
    )
    print(
        f"Regression check passed={passed} reference={args.reference_task} candidate={args.candidate_task} "
        f"drop={drop:.2f} shared_skills={overlap['shared_skills']}"
    )


def cmd_stability_check(args: argparse.Namespace) -> None:
    cfg = _build_cfg_from_args(args)
    store = MemoryStore(cfg.db_path)
    if args.run_cycles > 0:
        run_agent(task_name=args.task, cycles=args.run_cycles, interval_s=args.interval, cfg=cfg)

    metrics = store.recent_cycle_metrics_for_task(
        task_name=args.task,
        limit=args.recent_window + args.baseline_window,
    )
    result = analyze_stability(
        metrics_desc=metrics,
        baseline_window=args.baseline_window,
        recent_window=args.recent_window,
    )
    rec_text = " | ".join(result["recommendations"])
    notes = (
        f"samples={len(metrics)}; windows(baseline={args.baseline_window}, recent={args.recent_window}); "
        f"status={result['status']}"
    )
    store.save_stability_check(
        ts=_ts(),
        task_name=args.task,
        baseline_window=args.baseline_window,
        recent_window=args.recent_window,
        baseline_pass_rate=result["baseline_pass_rate"],
        recent_pass_rate=result["recent_pass_rate"],
        pass_rate_drift=result["pass_rate_drift"],
        recent_avg_confidence=result["recent_avg_confidence"],
        recent_avg_error_rate=result["recent_avg_error_rate"],
        status=result["status"],
        recommendations=rec_text,
        notes=notes,
    )
    print(
        f"Stability check status={result['status']} drift={result['pass_rate_drift']:.2f} "
        f"recent_conf={result['recent_avg_confidence']:.2f} recent_err={result['recent_avg_error_rate']:.2f}"
    )


def cmd_release_check(args: argparse.Namespace) -> None:
    cfg = _build_cfg_from_args(args)
    store = MemoryStore(cfg.db_path)

    bench = store.recent_task_benchmarks(task_name=args.task, limit=1)
    reg = store.recent_regression_checks(limit=1)
    stab = store.recent_stability_checks(task_name=args.task, limit=1)

    benchmark_pass_rate = float(bench[0]["pass_rate"]) if bench else 0.0
    regression_passed = bool(reg[0]["passed"]) if reg else False
    stability_status = str(stab[0]["status"]) if stab else "critical"

    score, passed, status = evaluate_release_readiness(
        benchmark_pass_rate=benchmark_pass_rate,
        regression_passed=regression_passed,
        stability_status=stability_status,
    )
    notes = (
        f"status={status}; benchmark={benchmark_pass_rate:.2f}; regression={regression_passed}; "
        f"stability={stability_status}"
    )
    store.save_release_check(
        ts=_ts(),
        task_name=args.task,
        preset=args.preset,
        benchmark_pass_rate=benchmark_pass_rate,
        regression_passed=regression_passed,
        stability_status=stability_status,
        readiness_score=score,
        passed=passed,
        notes=notes,
    )
    print(
        f"Release check passed={passed} task={args.task} preset={args.preset} "
        f"readiness_score={score:.2f} status={status}"
    )


def cmd_runbook(args: argparse.Namespace) -> None:
    cfg = _build_cfg_from_args(args)
    store = MemoryStore(cfg.db_path)
    content = generate_operator_runbook(
        store=store,
        output_path=cfg.report_path.parent / "operator_runbook.md",
        task_name=args.task,
        preset=args.preset,
    )
    print(content)


def cmd_generate_spec(args: argparse.Namespace) -> None:
    result = generate_spec(
        product_name=args.product_name,
        output_dir=Path(args.output_dir),
        mission_statement=args.mission_statement,
    )
    print(f"{result.message} path={result.path}")


def cmd_generate_code(args: argparse.Namespace) -> None:
    result = generate_code(
        product_name=args.product_name,
        output_dir=Path(args.output_dir),
    )
    print(f"{result.message} path={result.path}")


def cmd_run_tests(args: argparse.Namespace) -> None:
    result = run_tests(Path(args.project_dir))
    print(f"{result.message} path={result.path}")


def cmd_package_release(args: argparse.Namespace) -> None:
    result = package_release(
        project_dir=Path(args.project_dir),
        artifact_dir=Path(args.artifact_dir),
    )
    print(f"{result.message} path={result.path}")


def cmd_money_loop(args: argparse.Namespace) -> None:
    cfg = _build_cfg_from_args(args)
    store = MemoryStore(cfg.db_path)

    export_path = Path(args.export_path)
    last_seen_id = max(0, args.start_after_id)
    iteration = 0

    while True:
        iteration += 1
        run_agent(
            task_name=args.task,
            cycles=args.cycles_per_iteration,
            interval_s=args.interval,
            cfg=cfg,
        )

        leads = store.findings_since_id(
            since_id=last_seen_id,
            min_confidence=args.min_lead_confidence,
            limit=args.max_export_per_iteration,
        )
        qualified_leads: list[tuple[dict[str, str | int | float], float, float]] = []
        for lead in leads:
            lscore = lead_score(float(lead["confidence"]), float(lead["novelty"]))
            est_value = estimate_project_value_usd(
                title=str(lead["title"]),
                snippet=str(lead["snippet"]),
                source_url=str(lead["source_url"]),
                confidence=float(lead["confidence"]),
                novelty=float(lead["novelty"]),
                base_project_value=args.base_project_value,
                max_project_value=args.max_project_value,
            )
            if est_value < args.min_estimated_value_usd:
                continue
            qualified_leads.append((lead, lscore, est_value))

        exported = append_leads_csv(export_path, [lead for lead, _, _ in qualified_leads])
        newly_ledgered = 0
        drafted = 0
        for lead, lscore, est_value in qualified_leads:
            finding_id = int(lead["id"])
            if store.revenue_entry_exists_for_finding(finding_id):
                continue
            ledger_id = store.record_revenue_entry(
                ts=_ts(),
                task_name=args.task,
                finding_id=finding_id,
                source_url=str(lead["source_url"]),
                title=str(lead["title"]),
                confidence=float(lead["confidence"]),
                novelty=float(lead["novelty"]),
                lead_score=lscore,
                estimated_value_usd=est_value,
                status="open",
                notes=f"auto-scored from money-loop iteration={iteration}",
            )
            newly_ledgered += 1

            if args.auto_draft_proposals:
                proposal_entry = {
                    "id": ledger_id,
                    "ts": _ts(),
                    "task_name": args.task,
                    "title": str(lead["title"]),
                    "source_url": str(lead["source_url"]),
                    "lead_score": lscore,
                    "estimated_value_usd": est_value,
                }
                write_proposal_file(Path(args.proposal_dir), proposal_entry, overwrite=args.overwrite_proposals)
                drafted += 1

        if leads:
            last_seen_id = int(leads[-1]["id"])

        if args.generate_report_each_iteration:
            generate_markdown_report(store, cfg.report_path)

        print(
            f"money-loop iteration={iteration} task={args.task} "
            f"new_leads={exported} min_lead_conf={args.min_lead_confidence:.2f} "
            f"min_value_usd={args.min_estimated_value_usd:.2f} ledgered={newly_ledgered} "
            f"drafted={drafted} filtered_low_value={len(leads) - len(qualified_leads)} export={export_path}"
        )

        if args.max_iterations > 0 and iteration >= args.max_iterations:
            break

        if args.sleep_between_iterations > 0:
            sleep(args.sleep_between_iterations)


def cmd_auto_submit(args: argparse.Namespace) -> None:
    result = auto_submit_changes(
        repo_dir=Path(args.repo_dir),
        branch=args.branch,
        commit_message=args.commit_message,
        push=args.push,
        push_remote_name=args.push_remote,
        push_remote_url=args.push_remote_url,
    )
    print(
        f"auto-submit ok={result.ok} branch={result.branch} "
        f"commit={result.commit_hash or 'n/a'} message={result.message}"
    )


def cmd_export_payout(args: argparse.Namespace) -> None:
    cfg = load_payout_config_from_env()
    store = MemoryStore(AgentConfig().db_path)
    entries = store.recent_revenue_entries(limit=args.limit, status=args.status)
    if not entries:
        print("payout-export rows=0 total_usd=0.00 path=n/a")
        return

    grouped: dict[int, dict[str, str | int | float]] = defaultdict(dict)
    for e in entries:
        grouped[int(e["id"])] = e
    unique_entries = list(grouped.values())

    rows = payout_ready_rows(unique_entries, cfg)
    path = Path(args.output_path)
    count = write_payout_export(path, rows)
    total = round(sum(float(x["estimated_value_usd"]) for x in unique_entries), 2)

    if args.mark_as_exported and count > 0:
        ids = [int(x["ledger_id"]) for x in rows]
        store.mark_revenue_entries_status(ids, "exported")

    store.record_payout_export(
        ts=_ts(),
        destination_label=cfg.destination_label,
        total_amount_usd=total,
        item_count=count,
        export_path=str(path),
        notes=(
            f"masked_destination={cfg.destination_label}; status_filter={args.status}; "
            f"mark_exported={args.mark_as_exported}"
        ),
    )
    print(f"payout-export rows={count} total_usd={total:.2f} path={path}")


def cmd_revalue_ledger(args: argparse.Namespace) -> None:
    store = MemoryStore(AgentConfig().db_path)
    entries = store.recent_revenue_entries(limit=args.limit, status=args.status)
    if not entries:
        print("revalue-ledger updated=0 total_before=0.00 total_after=0.00")
        return

    total_before = 0.0
    total_after = 0.0
    updated = 0
    for e in entries:
        total_before += float(e["estimated_value_usd"])
        new_val = estimate_project_value_usd(
            title=str(e["title"]),
            snippet=str(e.get("notes", "")),
            source_url=str(e["source_url"]),
            confidence=float(e["confidence"]),
            novelty=float(e["novelty"]),
            base_project_value=args.base_project_value,
            max_project_value=args.max_project_value,
        )
        total_after += new_val
        store.update_revenue_estimated_value(
            entry_id=int(e["id"]),
            estimated_value_usd=new_val,
            notes_suffix=" | revalued_high_ticket",
        )
        updated += 1
    print(
        f"revalue-ledger updated={updated} total_before={total_before:.2f} "
        f"total_after={total_after:.2f}"
    )


def cmd_draft_proposals(args: argparse.Namespace) -> None:
    store = MemoryStore(AgentConfig().db_path)
    entries = store.recent_revenue_entries(limit=args.limit, status=args.status)
    if not entries:
        print("draft-proposals created=0 path=n/a")
        return

    out_dir = Path(args.output_dir)
    created = 0
    for entry in entries:
        path = write_proposal_file(out_dir, entry, overwrite=args.overwrite)
        if path.exists():
            created += 1

    if args.mark_as_proposed and entries:
        ids = [int(e["id"]) for e in entries]
        store.mark_revenue_entries_status(ids, "proposed")
    print(f"draft-proposals created={created} path={out_dir}")


def cmd_execute_proposals(args: argparse.Namespace) -> None:
    if args.push_source_repo and args.push_remote_url:
        print("execute-proposals processed=0 success=0 failed=0 reason=conflicting_push_targets")
        return

    proposal_dir = Path(args.proposal_dir)
    if not proposal_dir.exists():
        print(f"execute-proposals processed=0 success=0 failed=0 reason=missing_dir:{proposal_dir}")
        return

    proposal_files = sorted(proposal_dir.glob("proposal_*.md"))
    if args.limit > 0:
        proposal_files = proposal_files[: args.limit]
    if not proposal_files:
        print("execute-proposals processed=0 success=0 failed=0 reason=no_proposals")
        return

    repo_dir = Path(args.repo_dir).resolve()
    output_dir = Path(args.output_dir)
    artifact_dir = Path(args.artifact_dir)

    ok_count = 0
    fail_count = 0
    for prop in proposal_files:
        title = parse_proposal_title(prop)
        product_name = f"{title} Implementation"

        spec_result = generate_spec(
            product_name=product_name,
            output_dir=output_dir,
            mission_statement="Deliver production-ready software implementation based on proposal scope.",
        )
        code_result = generate_code(
            product_name=product_name,
            output_dir=output_dir,
        )
        if not spec_result.ok or not code_result.ok or code_result.path is None or spec_result.path is None:
            fail_count += 1
            mark_proposal_execution(prop, "failed_generation", "", "")
            continue

        project_dir = code_result.path
        paths_to_submit: list[Path] = [prop, spec_result.path, project_dir]

        if args.run_tests:
            test_result = run_tests(project_dir)
            if test_result.path is not None:
                paths_to_submit.append(test_result.path)

        if args.package:
            pkg_result = package_release(project_dir=project_dir, artifact_dir=artifact_dir)
            if pkg_result.path is not None:
                paths_to_submit.append(pkg_result.path)
                manifest = artifact_dir / f"{project_dir.name}_manifest.json"
                if manifest.exists():
                    paths_to_submit.append(manifest)

        branch = f"{args.branch_prefix}/{prop.stem}"
        push_remote_url = args.push_remote_url
        if args.push and args.push_source_repo:
            push_remote_url = parse_proposal_source_repo_url(prop)
            if not push_remote_url:
                fail_count += 1
                mark_proposal_execution(prop, "submit_failed: proposal source is not a GitHub repository URL", branch, "")
                continue

        submit_result = auto_submit_paths(
            repo_dir=repo_dir,
            branch=branch,
            commit_message=f"Implement {prop.stem}",
            paths=paths_to_submit,
            push=args.push,
            push_remote_name=args.push_remote,
            push_remote_url=push_remote_url,
        )
        if submit_result.ok:
            ok_count += 1
            mark_proposal_execution(prop, "submitted", submit_result.branch, submit_result.commit_hash)
        else:
            fail_count += 1
            mark_proposal_execution(prop, f"submit_failed: {submit_result.message}", submit_result.branch, submit_result.commit_hash)

    print(
        f"execute-proposals processed={len(proposal_files)} success={ok_count} failed={fail_count} "
        f"push={args.push}"
    )


def cmd_web(args: argparse.Namespace) -> None:
    run_web_server(task_choices=TASK_CHOICES, host=args.host, port=args.port)


def cmd_compete(args: argparse.Namespace) -> None:
    """Scan all sources and generate competitive proposals + optional code for every finding."""
    cfg = _build_cfg_from_args(args)
    store = MemoryStore(cfg.db_path)
    out_dir = Path(args.proposal_dir)
    last_id = args.start_after_id
    iteration = 0

    while True:
        iteration += 1
        run_agent(task_name="compete_watch", cycles=args.cycles_per_iteration, interval_s=args.interval, cfg=cfg)

        entries = store.recent_revenue_entries(limit=args.max_export_per_iteration, status="open")
        new_entries = [e for e in entries if int(e["id"]) > last_id]
        new_entries = [
            e for e in new_entries if float(e["lead_score"]) >= args.min_lead_confidence
        ]
        if args.min_estimated_value_usd > 0:
            new_entries = [e for e in new_entries if float(e["estimated_value_usd"]) >= args.min_estimated_value_usd]

        drafted = 0
        generated = 0
        for entry in new_entries:
            path = write_competition_proposal_file(out_dir, entry, overwrite=args.overwrite_proposals)
            if path.exists():
                drafted += 1

            if args.generate_code:
                title = str(entry["title"])
                product_name = f"Competitor to {title}"
                spec_result = generate_spec(
                    product_name=product_name,
                    output_dir=Path(args.output_dir),
                    mission_statement=f"Build a competing alternative to {title} with differentiated features.",
                )
                code_result = generate_code(
                    product_name=product_name,
                    output_dir=Path(args.output_dir),
                )
                if spec_result.ok and code_result.ok:
                    generated += 1

        if new_entries:
            ids = [int(e["id"]) for e in new_entries]
            store.mark_revenue_entries_status(ids, "proposed")
            last_id = max(ids)

        print(
            f"compete iteration={iteration} findings={len(new_entries)} "
            f"drafted={drafted} generated={generated}"
        )

        if args.max_iterations > 0 and iteration >= args.max_iterations:
            break

        if args.sleep_between_iterations > 0:
            sleep(args.sleep_between_iterations)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Autonomous Web Agent")
    sub = parser.add_subparsers(required=True)

    p_run = sub.add_parser("run", help="Run autonomous cycles")
    p_run.add_argument("--task", default="trend_watch", choices=TASK_CHOICES)
    p_run.add_argument("--preset", default="balanced", choices=["balanced", "conservative", "aggressive"])
    p_run.add_argument("--cycles", type=int, default=1)
    p_run.add_argument("--interval", type=int, default=0)
    p_run.add_argument("--mission-name", default="daily_trend_intel")
    p_run.add_argument(
        "--mission-statement",
        default="Track high-signal AI tooling changes daily with low false positives.",
    )
    p_run.add_argument("--min-confidence", type=float, default=0.55)
    p_run.add_argument("--min-findings", type=int, default=2)
    p_run.add_argument("--max-error-rate", type=float, default=0.35)
    p_run.add_argument("--max-fetches-per-cycle", type=int, default=12)
    p_run.add_argument("--max-retries-per-target", type=int, default=2)
    p_run.add_argument("--retry-backoff-s", type=float, default=0.7)
    p_run.add_argument("--max-consecutive-failures", type=int, default=6)
    p_run.add_argument("--min-extracted-chars", type=int, default=160)
    p_run.add_argument("--min-extraction-quality", type=float, default=0.45)
    p_run.add_argument("--min-accept-confidence", type=float, default=0.45)
    p_run.add_argument("--max-policy-violations-per-cycle", type=int, default=3)
    p_run.add_argument("--disable-policy-halt", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_train = sub.add_parser("train", help="Tune task profile weights")
    p_train.add_argument("--task", default="trend_watch", choices=TASK_CHOICES)
    p_train.add_argument("--novelty", type=float)
    p_train.add_argument("--reliability", type=float)
    p_train.add_argument("--speed", type=float)
    p_train.add_argument("--notes", type=str)
    p_train.set_defaults(func=cmd_train)

    p_report = sub.add_parser("report", help="Generate report")
    p_report.set_defaults(func=cmd_report)

    p_bench = sub.add_parser("benchmark", help="Run and record benchmark metrics")
    p_bench.add_argument("--task", default="trend_watch", choices=TASK_CHOICES)
    p_bench.add_argument("--preset", default="balanced", choices=["balanced", "conservative", "aggressive"])
    p_bench.add_argument("--cycles", type=int, default=3)
    p_bench.add_argument("--interval", type=int, default=0)
    p_bench.add_argument("--mission-name", default="task_benchmark")
    p_bench.add_argument("--mission-statement", default="Evaluate task profile quality on fixed targets.")
    p_bench.add_argument("--min-confidence", type=float, default=0.55)
    p_bench.add_argument("--min-findings", type=int, default=2)
    p_bench.add_argument("--max-error-rate", type=float, default=0.35)
    p_bench.add_argument("--max-fetches-per-cycle", type=int, default=12)
    p_bench.add_argument("--max-retries-per-target", type=int, default=2)
    p_bench.add_argument("--retry-backoff-s", type=float, default=0.7)
    p_bench.add_argument("--max-consecutive-failures", type=int, default=6)
    p_bench.add_argument("--min-extracted-chars", type=int, default=160)
    p_bench.add_argument("--min-extraction-quality", type=float, default=0.45)
    p_bench.add_argument("--min-accept-confidence", type=float, default=0.45)
    p_bench.add_argument("--max-policy-violations-per-cycle", type=int, default=3)
    p_bench.add_argument("--disable-policy-halt", action="store_true")
    p_bench.set_defaults(func=cmd_benchmark)

    p_reg = sub.add_parser("regression-check", help="Compare candidate task against reference task")
    p_reg.add_argument("--reference-task", default="trend_watch", choices=TASK_CHOICES)
    p_reg.add_argument("--candidate-task", default="software_solver", choices=TASK_CHOICES)
    p_reg.add_argument("--preset", default="balanced", choices=["balanced", "conservative", "aggressive"])
    p_reg.add_argument("--cycles", type=int, default=3)
    p_reg.add_argument("--interval", type=int, default=0)
    p_reg.add_argument("--max-pass-rate-drop", type=float, default=0.15)
    p_reg.add_argument("--mission-name", default="regression_check")
    p_reg.add_argument("--mission-statement", default="Validate multi-task transfer without major forgetting.")
    p_reg.add_argument("--min-confidence", type=float, default=0.55)
    p_reg.add_argument("--min-findings", type=int, default=2)
    p_reg.add_argument("--max-error-rate", type=float, default=0.35)
    p_reg.add_argument("--max-fetches-per-cycle", type=int, default=12)
    p_reg.add_argument("--max-retries-per-target", type=int, default=2)
    p_reg.add_argument("--retry-backoff-s", type=float, default=0.7)
    p_reg.add_argument("--max-consecutive-failures", type=int, default=6)
    p_reg.add_argument("--min-extracted-chars", type=int, default=160)
    p_reg.add_argument("--min-extraction-quality", type=float, default=0.45)
    p_reg.add_argument("--min-accept-confidence", type=float, default=0.45)
    p_reg.add_argument("--max-policy-violations-per-cycle", type=int, default=3)
    p_reg.add_argument("--disable-policy-halt", action="store_true")
    p_reg.set_defaults(func=cmd_regression_check)

    p_stab = sub.add_parser("stability-check", help="Analyze drift and long-run stability")
    p_stab.add_argument("--task", default="trend_watch", choices=TASK_CHOICES)
    p_stab.add_argument("--preset", default="balanced", choices=["balanced", "conservative", "aggressive"])
    p_stab.add_argument("--run-cycles", type=int, default=0)
    p_stab.add_argument("--recent-window", type=int, default=8)
    p_stab.add_argument("--baseline-window", type=int, default=8)
    p_stab.add_argument("--interval", type=int, default=0)
    p_stab.add_argument("--mission-name", default="stability_check")
    p_stab.add_argument("--mission-statement", default="Detect drift and recommend runtime tuning.")
    p_stab.add_argument("--min-confidence", type=float, default=0.55)
    p_stab.add_argument("--min-findings", type=int, default=2)
    p_stab.add_argument("--max-error-rate", type=float, default=0.35)
    p_stab.add_argument("--max-fetches-per-cycle", type=int, default=12)
    p_stab.add_argument("--max-retries-per-target", type=int, default=2)
    p_stab.add_argument("--retry-backoff-s", type=float, default=0.7)
    p_stab.add_argument("--max-consecutive-failures", type=int, default=6)
    p_stab.add_argument("--min-extracted-chars", type=int, default=160)
    p_stab.add_argument("--min-extraction-quality", type=float, default=0.45)
    p_stab.add_argument("--min-accept-confidence", type=float, default=0.45)
    p_stab.add_argument("--max-policy-violations-per-cycle", type=int, default=3)
    p_stab.add_argument("--disable-policy-halt", action="store_true")
    p_stab.set_defaults(func=cmd_stability_check)

    p_rel = sub.add_parser("release-check", help="Run final release readiness checklist")
    p_rel.add_argument("--task", default="trend_watch", choices=TASK_CHOICES)
    p_rel.add_argument("--preset", default="balanced", choices=["balanced", "conservative", "aggressive"])
    p_rel.add_argument("--mission-name", default="release_check")
    p_rel.add_argument("--mission-statement", default="Evaluate deployment readiness signals.")
    p_rel.add_argument("--min-confidence", type=float, default=0.55)
    p_rel.add_argument("--min-findings", type=int, default=2)
    p_rel.add_argument("--max-error-rate", type=float, default=0.35)
    p_rel.add_argument("--max-fetches-per-cycle", type=int, default=12)
    p_rel.add_argument("--max-retries-per-target", type=int, default=2)
    p_rel.add_argument("--retry-backoff-s", type=float, default=0.7)
    p_rel.add_argument("--max-consecutive-failures", type=int, default=6)
    p_rel.add_argument("--min-extracted-chars", type=int, default=160)
    p_rel.add_argument("--min-extraction-quality", type=float, default=0.45)
    p_rel.add_argument("--min-accept-confidence", type=float, default=0.45)
    p_rel.add_argument("--max-policy-violations-per-cycle", type=int, default=3)
    p_rel.add_argument("--disable-policy-halt", action="store_true")
    p_rel.set_defaults(func=cmd_release_check)

    p_runbook = sub.add_parser("runbook", help="Generate operator runbook markdown")
    p_runbook.add_argument("--task", default="trend_watch", choices=TASK_CHOICES)
    p_runbook.add_argument("--preset", default="balanced", choices=["balanced", "conservative", "aggressive"])
    p_runbook.add_argument("--mission-name", default="runbook")
    p_runbook.add_argument("--mission-statement", default="Generate operator actions and escalation guidance.")
    p_runbook.add_argument("--min-confidence", type=float, default=0.55)
    p_runbook.add_argument("--min-findings", type=int, default=2)
    p_runbook.add_argument("--max-error-rate", type=float, default=0.35)
    p_runbook.add_argument("--max-fetches-per-cycle", type=int, default=12)
    p_runbook.add_argument("--max-retries-per-target", type=int, default=2)
    p_runbook.add_argument("--retry-backoff-s", type=float, default=0.7)
    p_runbook.add_argument("--max-consecutive-failures", type=int, default=6)
    p_runbook.add_argument("--min-extracted-chars", type=int, default=160)
    p_runbook.add_argument("--min-extraction-quality", type=float, default=0.45)
    p_runbook.add_argument("--min-accept-confidence", type=float, default=0.45)
    p_runbook.add_argument("--max-policy-violations-per-cycle", type=int, default=3)
    p_runbook.add_argument("--disable-policy-halt", action="store_true")
    p_runbook.set_defaults(func=cmd_runbook)

    p_spec = sub.add_parser("generate-spec", help="Generate a software product specification")
    p_spec.add_argument("--product-name", default="Workflow Automation Suite")
    p_spec.add_argument("--mission-statement", default="Build production software that automates a high-value workflow.")
    p_spec.add_argument("--output-dir", default="generated_software")
    p_spec.set_defaults(func=cmd_generate_spec)

    p_codegen = sub.add_parser("generate-code", help="Generate software scaffold code")
    p_codegen.add_argument("--product-name", default="Workflow Automation Suite")
    p_codegen.add_argument("--output-dir", default="generated_software")
    p_codegen.set_defaults(func=cmd_generate_code)

    p_tests = sub.add_parser("run-tests", help="Run tests for a generated software project")
    p_tests.add_argument("--project-dir", required=True)
    p_tests.set_defaults(func=cmd_run_tests)

    p_pkg = sub.add_parser("package-release", help="Package a generated software project as a release artifact")
    p_pkg.add_argument("--project-dir", required=True)
    p_pkg.add_argument("--artifact-dir", default="release_artifacts")
    p_pkg.set_defaults(func=cmd_package_release)

    p_money = sub.add_parser(
        "money-loop",
        help="Run persistently and export high-confidence findings as monetization leads",
    )
    p_money.add_argument("--task", default="trend_watch", choices=TASK_CHOICES)
    p_money.add_argument("--preset", default="balanced", choices=["balanced", "conservative", "aggressive"])
    p_money.add_argument("--cycles-per-iteration", type=int, default=3)
    p_money.add_argument("--interval", type=int, default=10)
    p_money.add_argument("--sleep-between-iterations", type=int, default=300)
    p_money.add_argument("--max-iterations", type=int, default=0)
    p_money.add_argument("--start-after-id", type=int, default=0)
    p_money.add_argument("--min-lead-confidence", type=float, default=0.6)
    p_money.add_argument("--max-export-per-iteration", type=int, default=250)
    p_money.add_argument("--export-path", default="logs/revenue_leads.csv")
    p_money.add_argument("--usd-per-score-point", type=float, default=100.0)
    p_money.add_argument("--base-project-value", type=float, default=25000.0)
    p_money.add_argument("--max-project-value", type=float, default=500000.0)
    p_money.add_argument("--min-estimated-value-usd", type=float, default=0.0)
    p_money.add_argument("--auto-draft-proposals", action="store_true")
    p_money.add_argument("--proposal-dir", default="logs/proposals")
    p_money.add_argument("--overwrite-proposals", action="store_true")
    p_money.add_argument("--generate-report-each-iteration", action="store_true")

    p_money.add_argument("--mission-name", default="revenue_intel_loop")
    p_money.add_argument(
        "--mission-statement",
        default="Continuously identify high-confidence AI opportunities for monetizable services.",
    )
    p_money.add_argument("--min-confidence", type=float, default=0.55)
    p_money.add_argument("--min-findings", type=int, default=1)
    p_money.add_argument("--max-error-rate", type=float, default=0.35)
    p_money.add_argument("--max-fetches-per-cycle", type=int, default=12)
    p_money.add_argument("--max-retries-per-target", type=int, default=2)
    p_money.add_argument("--retry-backoff-s", type=float, default=0.7)
    p_money.add_argument("--max-consecutive-failures", type=int, default=6)
    p_money.add_argument("--min-extracted-chars", type=int, default=160)
    p_money.add_argument("--min-extraction-quality", type=float, default=0.45)
    p_money.add_argument("--min-accept-confidence", type=float, default=0.45)
    p_money.add_argument("--max-policy-violations-per-cycle", type=int, default=3)
    p_money.add_argument("--disable-policy-halt", action="store_true")
    p_money.set_defaults(func=cmd_money_loop)

    p_submit = sub.add_parser("auto-submit", help="Commit and optionally push generated code changes")
    p_submit.add_argument("--repo-dir", default=".")
    p_submit.add_argument("--branch", default="auto/submission")
    p_submit.add_argument("--commit-message", default="Automated software submission")
    p_submit.add_argument("--push", action="store_true")
    p_submit.add_argument("--push-remote", default="origin")
    p_submit.add_argument("--push-remote-url", default="")
    p_submit.set_defaults(func=cmd_auto_submit)

    p_payout = sub.add_parser("export-payout", help="Export payout-ready ledger rows with masked destination config")
    p_payout.add_argument("--status", default="open")
    p_payout.add_argument("--limit", type=int, default=200)
    p_payout.add_argument("--output-path", default="logs/payout_export.csv")
    p_payout.add_argument("--mark-as-exported", action="store_true")
    p_payout.set_defaults(func=cmd_export_payout)

    p_revalue = sub.add_parser("revalue-ledger", help="Recalculate ledger entries for higher-ticket project valuation")
    p_revalue.add_argument("--status", default="open")
    p_revalue.add_argument("--limit", type=int, default=500)
    p_revalue.add_argument("--base-project-value", type=float, default=40000.0)
    p_revalue.add_argument("--max-project-value", type=float, default=750000.0)
    p_revalue.set_defaults(func=cmd_revalue_ledger)

    p_prop = sub.add_parser("draft-proposals", help="Draft client-ready proposals from revenue ledger entries")
    p_prop.add_argument("--status", default="open")
    p_prop.add_argument("--limit", type=int, default=100)
    p_prop.add_argument("--output-dir", default="logs/proposals")
    p_prop.add_argument("--overwrite", action="store_true")
    p_prop.add_argument("--mark-as-proposed", action="store_true")
    p_prop.set_defaults(func=cmd_draft_proposals)

    p_exec = sub.add_parser("execute-proposals", help="Generate code and submit each proposal on its own branch")
    p_exec.add_argument("--proposal-dir", default="logs/proposals")
    p_exec.add_argument("--output-dir", default="generated_software/proposal_projects")
    p_exec.add_argument("--artifact-dir", default="release_artifacts")
    p_exec.add_argument("--repo-dir", default=".")
    p_exec.add_argument("--branch-prefix", default="proposal")
    p_exec.add_argument("--limit", type=int, default=0)
    p_exec.add_argument("--run-tests", action="store_true")
    p_exec.add_argument("--package", action="store_true")
    p_exec.add_argument("--push", action="store_true")
    p_exec.add_argument("--push-remote", default="origin")
    p_exec.add_argument("--push-remote-url", default="")
    p_exec.add_argument("--push-source-repo", action="store_true")
    p_exec.set_defaults(func=cmd_execute_proposals)

    p_compete = sub.add_parser(
        "compete",
        help="Scan all sources and auto-generate competing implementations for every finding",
    )
    p_compete.add_argument("--preset", default="aggressive", choices=["balanced", "conservative", "aggressive"])
    p_compete.add_argument("--cycles-per-iteration", type=int, default=3)
    p_compete.add_argument("--interval", type=int, default=5)
    p_compete.add_argument("--sleep-between-iterations", type=int, default=120)
    p_compete.add_argument("--max-iterations", type=int, default=0)
    p_compete.add_argument("--start-after-id", type=int, default=0)
    p_compete.add_argument("--min-lead-confidence", type=float, default=0.5)
    p_compete.add_argument("--max-export-per-iteration", type=int, default=50)
    p_compete.add_argument("--min-estimated-value-usd", type=float, default=0.0)
    p_compete.add_argument("--proposal-dir", default="logs/proposals")
    p_compete.add_argument("--output-dir", default="generated_software/competitors")
    p_compete.add_argument("--overwrite-proposals", action="store_true")
    p_compete.add_argument("--generate-code", action="store_true")
    p_compete.add_argument("--mission-name", default="compete_intel_loop")
    p_compete.add_argument(
        "--mission-statement",
        default="Identify trending projects and generate competing alternative implementations.",
    )
    p_compete.add_argument("--min-confidence", type=float, default=0.5)
    p_compete.add_argument("--min-findings", type=int, default=1)
    p_compete.add_argument("--max-error-rate", type=float, default=0.4)
    p_compete.add_argument("--max-fetches-per-cycle", type=int, default=16)
    p_compete.add_argument("--max-retries-per-target", type=int, default=2)
    p_compete.add_argument("--retry-backoff-s", type=float, default=0.5)
    p_compete.add_argument("--max-consecutive-failures", type=int, default=8)
    p_compete.add_argument("--min-extracted-chars", type=int, default=120)
    p_compete.add_argument("--min-extraction-quality", type=float, default=0.4)
    p_compete.add_argument("--min-accept-confidence", type=float, default=0.4)
    p_compete.add_argument("--max-policy-violations-per-cycle", type=int, default=5)
    p_compete.add_argument("--disable-policy-halt", action="store_true")
    p_compete.set_defaults(func=cmd_compete)

    p_web = sub.add_parser("web", help="Start website dashboard for results and retraining")
    p_web.add_argument("--host", default="0.0.0.0")
    p_web.add_argument("--port", type=int, default=8080)
    p_web.set_defaults(func=cmd_web)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
