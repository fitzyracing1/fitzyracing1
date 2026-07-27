from datetime import datetime, timezone
from time import sleep

from .config import AgentConfig
from .extract import calibrate_reliability, confidence_score, extraction_quality_score, keyword_density, summarize
from .fetchers import DomainPolicyError, WebNavigator
from .mission import MissionContract
from .models import Finding
from .objectives import default_objectives_for_task, reprioritize
from .store import MemoryStore
from .tasks.aerospace_software import AerospaceSoftwareTask
from .tasks.irish_tech_watch import IrishTechWatchTask
from .tasks.security_watch import SecurityWatchTask
from .tasks.software_solver import SoftwareSolverTask
from .tasks.trend_watch import TrendWatchTask
from .tasks.compete_watch import CompeteWatchTask


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_task(task_name: str):
    if task_name == "trend_watch":
        return TrendWatchTask()
    if task_name == "irish_tech_watch":
        return IrishTechWatchTask()
    if task_name == "security_watch":
        return SecurityWatchTask()
    if task_name == "aerospace_software":
        return AerospaceSoftwareTask()
    if task_name == "software_solver":
        return SoftwareSolverTask()
    if task_name == "compete_watch":
        return CompeteWatchTask()
    raise ValueError(f"Unknown task: {task_name}")


def task_skill_overlap(reference_task: str, candidate_task: str) -> dict[str, int | str]:
    ref = _load_task(reference_task)
    cand = _load_task(candidate_task)
    shared = ref.skill_tags().intersection(cand.skill_tags())
    return {
        "reference_task": reference_task,
        "candidate_task": candidate_task,
        "reference_skills": len(ref.skill_tags()),
        "candidate_skills": len(cand.skill_tags()),
        "shared_skills": len(shared),
        "shared_skill_list": ",".join(sorted(shared)),
    }


def _categorize_error(err: Exception) -> str:
    name = err.__class__.__name__.lower()
    msg = str(err).lower()
    if isinstance(err, DomainPolicyError):
        return "policy"
    if "timeout" in name or "timed out" in msg:
        return "timeout"
    if "connect" in name or "network" in msg or "protocol" in name:
        return "network"
    if "parse" in name or "decode" in name:
        return "parse"
    return "unknown"


def _confidence_band(conf: float) -> str:
    if conf >= 0.75:
        return "high"
    if conf >= 0.5:
        return "medium"
    return "low"


def _matches_policy_block(text: str, blocked_terms: set[str]) -> str | None:
    lowered = text.lower()
    for term in blocked_terms:
        if term in lowered:
            return term
    return None


def _fetch_with_retry(
    navigator: WebNavigator,
    url: str,
    retries: int,
    backoff_s: float,
) -> tuple[tuple[str, str] | None, Exception | None, int]:
    attempts = 0
    last_err: Exception | None = None
    max_attempts = max(1, retries + 1)
    for i in range(max_attempts):
        attempts += 1
        try:
            return navigator.fetch(url), None, attempts
        except Exception as err:
            last_err = err
            if i < max_attempts - 1:
                sleep(backoff_s)
    return None, last_err, attempts


def seed_objectives(store: MemoryStore, task_name: str, novelty_boost: float = 1.0) -> None:
    objs = default_objectives_for_task(task_name)
    objs = reprioritize(objs, novelty_boost=novelty_boost)
    for o in objs:
        store.save_objective(o)


def run_agent(task_name: str, cycles: int, interval_s: int, cfg: AgentConfig) -> None:
    store = MemoryStore(cfg.db_path)
    mission = MissionContract(
        mission_name=cfg.mission_name,
        mission_statement=cfg.mission_statement,
        min_confidence=cfg.min_confidence,
        min_findings_per_cycle=cfg.min_findings_per_cycle,
        max_error_rate=cfg.max_error_rate,
    )
    mission.validate()
    profile = store.get_task_profile(task_name)
    task = _load_task(task_name)

    seed_objectives(store, task_name, novelty_boost=task.objective_boost())
    navigator = WebNavigator(cfg.allowed_domains, cfg.request_timeout_s, cfg.user_agent)

    try:
        run_halted = False
        halt_reason = ""
        for i in range(cycles):
            store.log_event(_ts(), "INFO", f"Cycle {i + 1}/{cycles} started for task={task_name}")
            cycle_findings = 0
            cycle_conf_sum = 0.0
            cycle_errors = 0
            cycle_actions = 0
            cycle_attempts = 0
            policy_violations = 0
            category_counts: dict[str, int] = {
                "policy": 0,
                "timeout": 0,
                "network": 0,
                "parse": 0,
                "unknown": 0,
            }
            consecutive_failures = 0
            fetch_budget = max(1, cfg.max_fetches_per_cycle)

            objectives = store.list_active_objectives(limit=cfg.max_actions_per_cycle)
            targets = task.get_targets()
            keys = task.keywords()

            for obj in objectives[: cfg.max_actions_per_cycle]:
                if fetch_budget <= 0:
                    store.log_event(_ts(), "WARN", "Fetch budget exhausted; deferring remaining objectives")
                    break
                if consecutive_failures >= cfg.max_consecutive_failures:
                    store.log_event(_ts(), "WARN", "Circuit breaker opened due to consecutive failures")
                    break

                moved = store.transition_objective_status(obj.id, "in_progress", _ts())
                if not moved:
                    store.log_event(_ts(), "WARN", f"Skipped objective with invalid transition id={obj.id} from={obj.status}")
                    continue

                objective_complete = True
                objective_errors = 0
                objective_findings = 0

                for tgt in targets:
                    if fetch_budget <= 0:
                        objective_complete = False
                        break
                    if consecutive_failures >= cfg.max_consecutive_failures:
                        objective_complete = False
                        break

                    cycle_actions += 1
                    fetch_budget -= 1
                    try:
                        blocked_url_term = _matches_policy_block(tgt.url, cfg.blocked_url_keywords)
                        if blocked_url_term:
                            policy_violations += 1
                            category_counts["policy"] += 1
                            store.save_decision_trace(
                                ts=_ts(),
                                task_name=task_name,
                                objective_id=obj.id,
                                target_name=tgt.name,
                                action="policy_block_url",
                                rationale=f"blocked url keyword matched: {blocked_url_term}",
                                confidence=0.0,
                                confidence_band="low",
                                outcome="blocked",
                            )
                            raise DomainPolicyError(f"blocked url keyword: {blocked_url_term}")

                        store.save_decision_trace(
                            ts=_ts(),
                            task_name=task_name,
                            objective_id=obj.id,
                            target_name=tgt.name,
                            action="fetch_target",
                            rationale="target selected by task profile and cycle budget",
                            confidence=0.0,
                            confidence_band="low",
                            outcome="attempt",
                        )

                        fetched, err, attempts = _fetch_with_retry(
                            navigator=navigator,
                            url=tgt.url,
                            retries=cfg.max_retries_per_target,
                            backoff_s=cfg.retry_backoff_s,
                        )
                        cycle_attempts += attempts
                        if err is not None or fetched is None:
                            raise err if err is not None else RuntimeError("fetch returned no content")

                        payload, final_url = fetched

                        title, text, finding_url = navigator.extract_finding(payload, final_url)
                        blocked_content_term = _matches_policy_block(
                            f"{title} {text}", cfg.blocked_content_keywords
                        )
                        if blocked_content_term:
                            policy_violations += 1
                            category_counts["policy"] += 1
                            store.save_decision_trace(
                                ts=_ts(),
                                task_name=task_name,
                                objective_id=obj.id,
                                target_name=tgt.name,
                                action="policy_block_content",
                                rationale=f"blocked content keyword matched: {blocked_content_term}",
                                confidence=0.0,
                                confidence_band="low",
                                outcome="blocked",
                            )
                            raise DomainPolicyError(f"blocked content keyword: {blocked_content_term}")

                        quality = extraction_quality_score(title=title, text=text, min_chars=cfg.min_extracted_chars)
                        if len(text) < cfg.min_extracted_chars or quality < cfg.min_extraction_quality:
                            store.save_decision_trace(
                                ts=_ts(),
                                task_name=task_name,
                                objective_id=obj.id,
                                target_name=tgt.name,
                                action="reject_extraction",
                                rationale=(
                                    f"quality gate failed chars={len(text)} quality={quality:.2f} "
                                    f"thresholds(chars>={cfg.min_extracted_chars}, quality>={cfg.min_extraction_quality})"
                                ),
                                confidence=quality,
                                confidence_band=_confidence_band(quality),
                                outcome="rejected",
                            )
                            raise ValueError(
                                f"low extraction quality chars={len(text)} quality={quality:.2f}"
                            )

                        rel = keyword_density(text, keys)
                        novelty = min(1.0, 0.3 + rel * 5)
                        calibrated = calibrate_reliability(tgt.reliability * profile.reliability_weight, quality)
                        conf = confidence_score(
                            reliability=calibrated,
                            relevance=rel,
                            novelty=novelty * profile.novelty_weight,
                            weights=(1.0, 1.5, 1.0),
                        )

                        if conf < cfg.min_accept_confidence:
                            store.save_decision_trace(
                                ts=_ts(),
                                task_name=task_name,
                                objective_id=obj.id,
                                target_name=tgt.name,
                                action="reject_low_confidence",
                                rationale=(
                                    f"confidence {conf:.2f} below threshold {cfg.min_accept_confidence:.2f}"
                                ),
                                confidence=conf,
                                confidence_band=_confidence_band(conf),
                                outcome="rejected",
                            )
                            continue

                        finding = Finding(
                            objective_id=obj.id,
                            source_url=finding_url,
                            title=title,
                            snippet=summarize(text),
                            confidence=conf,
                            novelty=novelty,
                        )
                        inserted = store.save_finding(finding)
                        if inserted:
                            objective_findings += 1
                            cycle_findings += 1
                            cycle_conf_sum += conf
                            consecutive_failures = 0
                            store.save_decision_trace(
                                ts=_ts(),
                                task_name=task_name,
                                objective_id=obj.id,
                                target_name=tgt.name,
                                action="accept_finding",
                                rationale=(
                                    f"accepted by relevance and calibrated reliability "
                                    f"rel={rel:.3f} quality={quality:.2f}"
                                ),
                                confidence=conf,
                                confidence_band=_confidence_band(conf),
                                outcome="saved",
                            )
                            store.log_event(_ts(), "INFO", f"Saved finding for objective={obj.id} source={tgt.name} conf={conf:.2f}")
                        else:
                            store.save_decision_trace(
                                ts=_ts(),
                                task_name=task_name,
                                objective_id=obj.id,
                                target_name=tgt.name,
                                action="deduplicate_finding",
                                rationale="existing fingerprint matched objective+source+title",
                                confidence=conf,
                                confidence_band=_confidence_band(conf),
                                outcome="skipped",
                            )
                            store.log_event(_ts(), "INFO", f"Deduplicated finding objective={obj.id} source={tgt.name}")
                    except Exception as e:
                        objective_errors += 1
                        cycle_errors += 1
                        consecutive_failures += 1
                        cat = _categorize_error(e)
                        category_counts[cat] = category_counts.get(cat, 0) + 1
                        level = "WARN" if cat in {"policy", "timeout", "network"} else "ERROR"
                        store.save_decision_trace(
                            ts=_ts(),
                            task_name=task_name,
                            objective_id=obj.id,
                            target_name=tgt.name,
                            action="target_failure",
                            rationale=f"failure category={cat}",
                            confidence=0.0,
                            confidence_band="low",
                            outcome="failed",
                        )
                        store.log_event(
                            _ts(),
                            level,
                            f"Target fetch failed category={cat} objective={obj.id} url={tgt.url} err={e}",
                        )

                    if (
                        cfg.halt_on_policy_violation_limit
                        and policy_violations >= cfg.max_policy_violations_per_cycle
                    ):
                        run_halted = True
                        halt_reason = (
                            f"policy violation limit reached: {policy_violations}/"
                            f"{cfg.max_policy_violations_per_cycle}"
                        )
                        objective_complete = False
                        break

                if objective_complete and objective_findings > 0:
                    store.transition_objective_status(obj.id, "done", _ts())
                elif objective_errors >= len(targets):
                    store.transition_objective_status(obj.id, "failed", _ts())
                else:
                    store.transition_objective_status(obj.id, "deferred", _ts())

                if run_halted:
                    store.log_event(_ts(), "WARN", f"Run halt requested during objective={obj.id}: {halt_reason}")
                    break

            if i < cycles - 1 and interval_s > 0:
                sleep(interval_s)

            avg_conf = cycle_conf_sum / cycle_findings if cycle_findings > 0 else 0.0
            error_rate = cycle_errors / cycle_actions if cycle_actions > 0 else 0.0
            cycle_pass = (
                cycle_findings >= mission.min_findings_per_cycle
                and avg_conf >= mission.min_confidence
                and error_rate <= mission.max_error_rate
            )
            cycle_notes = (
                f"mission={mission.mission_name}; statement={mission.mission_statement}; "
                f"targets(min_findings={mission.min_findings_per_cycle}, min_conf={mission.min_confidence:.2f}, "
                f"max_error_rate={mission.max_error_rate:.2f}); "
                f"actual(findings={cycle_findings}, avg_conf={avg_conf:.2f}, error_rate={error_rate:.2f}); "
                f"day2(attempts={cycle_attempts}, categories={category_counts}, budget_remaining={fetch_budget}); "
                f"day7(policy_violations={policy_violations}, min_accept_conf={cfg.min_accept_confidence:.2f})"
            )
            store.save_cycle_metric(
                ts=_ts(),
                task_name=task_name,
                mission_name=mission.mission_name,
                cycle_index=i + 1,
                findings_count=cycle_findings,
                avg_confidence=avg_conf,
                error_count=cycle_errors,
                action_count=cycle_actions,
                passed=cycle_pass,
                notes=cycle_notes,
            )
            store.log_event(
                _ts(),
                "INFO" if cycle_pass else "WARN",
                f"Cycle {i + 1} score pass={cycle_pass} findings={cycle_findings} avg_conf={avg_conf:.2f} error_rate={error_rate:.2f}",
            )

            store.log_event(_ts(), "INFO", f"Cycle {i + 1}/{cycles} complete")

            if run_halted:
                store.save_run_halt(_ts(), task_name, halt_reason, i + 1)
                store.log_event(_ts(), "WARN", f"Execution halted: {halt_reason}")
                break

        if run_halted:
            store.log_event(_ts(), "WARN", "Run terminated early by Day 7 stop condition")
    finally:
        navigator.close()
