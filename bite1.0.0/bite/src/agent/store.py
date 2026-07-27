import json
import sqlite3
from hashlib import sha1
from pathlib import Path

from .models import Finding, Objective, TaskProfile


class MemoryStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS objectives (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                query TEXT NOT NULL,
                priority REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                objective_id TEXT NOT NULL,
                source_url TEXT NOT NULL,
                title TEXT NOT NULL,
                snippet TEXT NOT NULL,
                confidence REAL NOT NULL,
                novelty REAL NOT NULL,
                discovered_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS task_profiles (
                name TEXT PRIMARY KEY,
                novelty_weight REAL NOT NULL,
                reliability_weight REAL NOT NULL,
                speed_weight REAL NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS run_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cycle_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                task_name TEXT NOT NULL,
                mission_name TEXT NOT NULL,
                cycle_index INTEGER NOT NULL,
                findings_count INTEGER NOT NULL,
                avg_confidence REAL NOT NULL,
                error_count INTEGER NOT NULL,
                action_count INTEGER NOT NULL,
                pass INTEGER NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS task_benchmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                task_name TEXT NOT NULL,
                profile_name TEXT NOT NULL,
                cycles INTEGER NOT NULL,
                pass_rate REAL NOT NULL,
                avg_findings REAL NOT NULL,
                avg_confidence REAL NOT NULL,
                avg_error_rate REAL NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decision_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                task_name TEXT NOT NULL,
                objective_id TEXT NOT NULL,
                target_name TEXT NOT NULL,
                action TEXT NOT NULL,
                rationale TEXT NOT NULL,
                confidence REAL NOT NULL,
                confidence_band TEXT NOT NULL,
                outcome TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS run_halts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                task_name TEXT NOT NULL,
                reason TEXT NOT NULL,
                cycle_index INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS regression_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                reference_task TEXT NOT NULL,
                candidate_task TEXT NOT NULL,
                baseline_pass_rate REAL NOT NULL,
                candidate_pass_rate REAL NOT NULL,
                pass_rate_drop REAL NOT NULL,
                shared_skills INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS stability_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                task_name TEXT NOT NULL,
                baseline_window INTEGER NOT NULL,
                recent_window INTEGER NOT NULL,
                baseline_pass_rate REAL NOT NULL,
                recent_pass_rate REAL NOT NULL,
                pass_rate_drift REAL NOT NULL,
                recent_avg_confidence REAL NOT NULL,
                recent_avg_error_rate REAL NOT NULL,
                status TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS release_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                task_name TEXT NOT NULL,
                preset TEXT NOT NULL,
                benchmark_pass_rate REAL NOT NULL,
                regression_passed INTEGER NOT NULL,
                stability_status TEXT NOT NULL,
                readiness_score REAL NOT NULL,
                passed INTEGER NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS revenue_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                task_name TEXT NOT NULL,
                finding_id INTEGER NOT NULL,
                source_url TEXT NOT NULL,
                title TEXT NOT NULL,
                confidence REAL NOT NULL,
                novelty REAL NOT NULL,
                lead_score REAL NOT NULL,
                estimated_value_usd REAL NOT NULL,
                status TEXT NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS payout_exports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                destination_label TEXT NOT NULL,
                total_amount_usd REAL NOT NULL,
                item_count INTEGER NOT NULL,
                export_path TEXT NOT NULL,
                notes TEXT NOT NULL
            );
            """
        )
        self._ensure_schema_upgrades()
        self.conn.commit()

    def _ensure_schema_upgrades(self) -> None:
        cols = self.conn.execute("PRAGMA table_info(findings)").fetchall()
        col_names = {c[1] for c in cols}
        if "fingerprint" not in col_names:
            self.conn.execute("ALTER TABLE findings ADD COLUMN fingerprint TEXT DEFAULT ''")

    @staticmethod
    def _finding_fingerprint(finding: Finding) -> str:
        raw = f"{finding.objective_id}|{finding.source_url}|{finding.title.strip().lower()}"
        return sha1(raw.encode("utf-8")).hexdigest()

    def save_objective(self, obj: Objective) -> None:
        self.conn.execute(
            """
            INSERT INTO objectives (id, title, query, priority, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                query=excluded.query,
                priority=excluded.priority,
                status=excluded.status,
                updated_at=excluded.updated_at,
                metadata=excluded.metadata
            """,
            (
                obj.id,
                obj.title,
                obj.query,
                obj.priority,
                obj.status,
                obj.created_at,
                obj.updated_at,
                json.dumps(obj.metadata),
            ),
        )
        self.conn.commit()

    def list_active_objectives(self, limit: int = 10) -> list[Objective]:
        rows = self.conn.execute(
            """
            SELECT * FROM objectives
            WHERE status IN ('pending', 'in_progress', 'deferred')
            ORDER BY priority DESC, updated_at ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        out: list[Objective] = []
        for row in rows:
            out.append(
                Objective(
                    id=row["id"],
                    title=row["title"],
                    query=row["query"],
                    priority=row["priority"],
                    status=row["status"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    metadata=json.loads(row["metadata"]),
                )
            )
        return out

    def save_finding(self, finding: Finding) -> bool:
        fp = self._finding_fingerprint(finding)
        existing = self.conn.execute(
            """
            SELECT 1 FROM findings
            WHERE fingerprint = ?
            LIMIT 1
            """,
            (fp,),
        ).fetchone()
        if existing:
            return False

        self.conn.execute(
            """
            INSERT INTO findings (objective_id, source_url, title, snippet, confidence, novelty, discovered_at, fingerprint)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                finding.objective_id,
                finding.source_url,
                finding.title,
                finding.snippet,
                finding.confidence,
                finding.novelty,
                finding.discovered_at,
                fp,
            ),
        )
        self.conn.commit()
        return True

    def transition_objective_status(self, objective_id: str, new_status: str, ts: str) -> bool:
        row = self.conn.execute(
            "SELECT status FROM objectives WHERE id = ?",
            (objective_id,),
        ).fetchone()
        if not row:
            return False

        current = row["status"]
        allowed: dict[str, set[str]] = {
            "pending": {"in_progress", "failed"},
            "in_progress": {"done", "deferred", "failed"},
            "deferred": {"in_progress", "failed"},
            "done": set(),
            "failed": set(),
        }

        if current == new_status:
            return True
        if new_status not in allowed.get(current, set()):
            return False

        self.conn.execute(
            "UPDATE objectives SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, ts, objective_id),
        )
        self.conn.commit()
        return True

    def get_findings_for_objective(self, objective_id: str, limit: int = 20) -> list[Finding]:
        rows = self.conn.execute(
            """
            SELECT objective_id, source_url, title, snippet, confidence, novelty, discovered_at
            FROM findings
            WHERE objective_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (objective_id, limit),
        ).fetchall()
        return [
            Finding(
                objective_id=row["objective_id"],
                source_url=row["source_url"],
                title=row["title"],
                snippet=row["snippet"],
                confidence=row["confidence"],
                novelty=row["novelty"],
                discovered_at=row["discovered_at"],
            )
            for row in rows
        ]

    def findings_since_id(
        self,
        since_id: int = 0,
        task_name: str | None = None,
        min_confidence: float = 0.0,
        limit: int = 200,
    ) -> list[dict[str, str | int | float]]:
        if task_name:
            rows = self.conn.execute(
                """
                SELECT f.id, f.objective_id, o.title AS objective_title, f.source_url, f.title,
                       f.snippet, f.confidence, f.novelty, f.discovered_at
                FROM findings f
                JOIN objectives o ON o.id = f.objective_id
                WHERE f.id > ?
                  AND f.confidence >= ?
                  AND EXISTS (
                      SELECT 1
                      FROM cycle_metrics cm
                      WHERE cm.task_name = ?
                        AND instr(cm.notes, f.objective_id) > 0
                  )
                ORDER BY f.id ASC
                LIMIT ?
                """,
                (since_id, min_confidence, task_name, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT f.id, f.objective_id, o.title AS objective_title, f.source_url, f.title,
                       f.snippet, f.confidence, f.novelty, f.discovered_at
                FROM findings f
                JOIN objectives o ON o.id = f.objective_id
                WHERE f.id > ?
                  AND f.confidence >= ?
                ORDER BY f.id ASC
                LIMIT ?
                """,
                (since_id, min_confidence, limit),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "objective_id": row["objective_id"],
                "objective_title": row["objective_title"],
                "source_url": row["source_url"],
                "title": row["title"],
                "snippet": row["snippet"],
                "confidence": row["confidence"],
                "novelty": row["novelty"],
                "discovered_at": row["discovered_at"],
            }
            for row in rows
        ]

    def upsert_task_profile(self, profile: TaskProfile) -> None:
        self.conn.execute(
            """
            INSERT INTO task_profiles (name, novelty_weight, reliability_weight, speed_weight, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                novelty_weight=excluded.novelty_weight,
                reliability_weight=excluded.reliability_weight,
                speed_weight=excluded.speed_weight,
                notes=excluded.notes
            """,
            (
                profile.name,
                profile.novelty_weight,
                profile.reliability_weight,
                profile.speed_weight,
                profile.notes,
            ),
        )
        self.conn.commit()

    def get_task_profile(self, name: str) -> TaskProfile:
        row = self.conn.execute(
            """
            SELECT * FROM task_profiles WHERE name = ?
            """,
            (name,),
        ).fetchone()
        if not row:
            profile = TaskProfile(name=name)
            self.upsert_task_profile(profile)
            return profile
        return TaskProfile(
            name=row["name"],
            novelty_weight=row["novelty_weight"],
            reliability_weight=row["reliability_weight"],
            speed_weight=row["speed_weight"],
            notes=row["notes"],
        )

    def log_event(self, ts: str, level: str, message: str) -> None:
        self.conn.execute(
            "INSERT INTO run_events (ts, level, message) VALUES (?, ?, ?)",
            (ts, level, message),
        )
        self.conn.commit()

    def recent_events(self, limit: int = 50) -> list[dict[str, str]]:
        rows = self.conn.execute(
            "SELECT ts, level, message FROM run_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [{"ts": r["ts"], "level": r["level"], "message": r["message"]} for r in rows]

    def event_level_summary(self, limit: int = 200) -> dict[str, int]:
        rows = self.conn.execute(
            """
            SELECT level, COUNT(*) AS cnt
            FROM (
                SELECT level FROM run_events ORDER BY id DESC LIMIT ?
            )
            GROUP BY level
            """,
            (limit,),
        ).fetchall()
        return {row["level"]: row["cnt"] for row in rows}

    def objective_status_summary(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT status, COUNT(*) AS cnt FROM objectives GROUP BY status"
        ).fetchall()
        return {row["status"]: row["cnt"] for row in rows}

    def save_cycle_metric(
        self,
        ts: str,
        task_name: str,
        mission_name: str,
        cycle_index: int,
        findings_count: int,
        avg_confidence: float,
        error_count: int,
        action_count: int,
        passed: bool,
        notes: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO cycle_metrics (
                ts, task_name, mission_name, cycle_index, findings_count,
                avg_confidence, error_count, action_count, pass, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                task_name,
                mission_name,
                cycle_index,
                findings_count,
                avg_confidence,
                error_count,
                action_count,
                1 if passed else 0,
                notes,
            ),
        )
        self.conn.commit()

    def recent_cycle_metrics(self, limit: int = 20) -> list[dict[str, str | int | float]]:
        rows = self.conn.execute(
            """
            SELECT ts, task_name, mission_name, cycle_index, findings_count,
                   avg_confidence, error_count, action_count, pass, notes
            FROM cycle_metrics
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "ts": row["ts"],
                "task_name": row["task_name"],
                "mission_name": row["mission_name"],
                "cycle_index": row["cycle_index"],
                "findings_count": row["findings_count"],
                "avg_confidence": row["avg_confidence"],
                "error_count": row["error_count"],
                "action_count": row["action_count"],
                "pass": row["pass"],
                "notes": row["notes"],
            }
            for row in rows
        ]

    def recent_cycle_metrics_for_task(self, task_name: str, limit: int = 40) -> list[dict[str, str | int | float]]:
        rows = self.conn.execute(
            """
            SELECT ts, task_name, mission_name, cycle_index, findings_count,
                   avg_confidence, error_count, action_count, pass, notes
            FROM cycle_metrics
            WHERE task_name = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (task_name, limit),
        ).fetchall()
        return [
            {
                "ts": row["ts"],
                "task_name": row["task_name"],
                "mission_name": row["mission_name"],
                "cycle_index": row["cycle_index"],
                "findings_count": row["findings_count"],
                "avg_confidence": row["avg_confidence"],
                "error_count": row["error_count"],
                "action_count": row["action_count"],
                "pass": row["pass"],
                "notes": row["notes"],
            }
            for row in rows
        ]

    def summarize_recent_cycle_metrics(self, task_name: str, cycles: int) -> dict[str, float]:
        rows = self.conn.execute(
            """
            SELECT pass, findings_count, avg_confidence, error_count, action_count
            FROM cycle_metrics
            WHERE task_name = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (task_name, cycles),
        ).fetchall()
        if not rows:
            return {
                "samples": 0.0,
                "pass_rate": 0.0,
                "avg_findings": 0.0,
                "avg_confidence": 0.0,
                "avg_error_rate": 0.0,
            }

        samples = len(rows)
        pass_rate = sum(row["pass"] for row in rows) / samples
        avg_findings = sum(row["findings_count"] for row in rows) / samples
        avg_confidence = sum(row["avg_confidence"] for row in rows) / samples
        avg_error_rate = sum(
            (row["error_count"] / row["action_count"]) if row["action_count"] > 0 else 0.0
            for row in rows
        ) / samples
        return {
            "samples": float(samples),
            "pass_rate": pass_rate,
            "avg_findings": avg_findings,
            "avg_confidence": avg_confidence,
            "avg_error_rate": avg_error_rate,
        }

    def save_task_benchmark(
        self,
        ts: str,
        task_name: str,
        profile_name: str,
        cycles: int,
        pass_rate: float,
        avg_findings: float,
        avg_confidence: float,
        avg_error_rate: float,
        notes: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO task_benchmarks (
                ts, task_name, profile_name, cycles, pass_rate,
                avg_findings, avg_confidence, avg_error_rate, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                task_name,
                profile_name,
                cycles,
                pass_rate,
                avg_findings,
                avg_confidence,
                avg_error_rate,
                notes,
            ),
        )
        self.conn.commit()

    def recent_task_benchmarks(self, task_name: str | None = None, limit: int = 10) -> list[dict[str, str | float | int]]:
        if task_name:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, profile_name, cycles, pass_rate, avg_findings,
                       avg_confidence, avg_error_rate, notes
                FROM task_benchmarks
                WHERE task_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (task_name, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, profile_name, cycles, pass_rate, avg_findings,
                       avg_confidence, avg_error_rate, notes
                FROM task_benchmarks
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "ts": row["ts"],
                "task_name": row["task_name"],
                "profile_name": row["profile_name"],
                "cycles": row["cycles"],
                "pass_rate": row["pass_rate"],
                "avg_findings": row["avg_findings"],
                "avg_confidence": row["avg_confidence"],
                "avg_error_rate": row["avg_error_rate"],
                "notes": row["notes"],
            }
            for row in rows
        ]

    def save_decision_trace(
        self,
        ts: str,
        task_name: str,
        objective_id: str,
        target_name: str,
        action: str,
        rationale: str,
        confidence: float,
        confidence_band: str,
        outcome: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO decision_traces (
                ts, task_name, objective_id, target_name, action,
                rationale, confidence, confidence_band, outcome
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                task_name,
                objective_id,
                target_name,
                action,
                rationale,
                confidence,
                confidence_band,
                outcome,
            ),
        )
        self.conn.commit()

    def recent_decision_traces(self, task_name: str | None = None, limit: int = 20) -> list[dict[str, str | float]]:
        if task_name:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, objective_id, target_name, action,
                       rationale, confidence, confidence_band, outcome
                FROM decision_traces
                WHERE task_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (task_name, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, objective_id, target_name, action,
                       rationale, confidence, confidence_band, outcome
                FROM decision_traces
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "ts": row["ts"],
                "task_name": row["task_name"],
                "objective_id": row["objective_id"],
                "target_name": row["target_name"],
                "action": row["action"],
                "rationale": row["rationale"],
                "confidence": row["confidence"],
                "confidence_band": row["confidence_band"],
                "outcome": row["outcome"],
            }
            for row in rows
        ]

    def confidence_band_summary(self, task_name: str | None = None, limit: int = 200) -> dict[str, int]:
        if task_name:
            rows = self.conn.execute(
                """
                SELECT confidence_band, COUNT(*) AS cnt
                FROM (
                    SELECT confidence_band FROM decision_traces
                    WHERE task_name = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                GROUP BY confidence_band
                """,
                (task_name, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT confidence_band, COUNT(*) AS cnt
                FROM (
                    SELECT confidence_band FROM decision_traces
                    ORDER BY id DESC
                    LIMIT ?
                )
                GROUP BY confidence_band
                """,
                (limit,),
            ).fetchall()
        return {row["confidence_band"]: row["cnt"] for row in rows}

    def save_run_halt(self, ts: str, task_name: str, reason: str, cycle_index: int) -> None:
        self.conn.execute(
            """
            INSERT INTO run_halts (ts, task_name, reason, cycle_index)
            VALUES (?, ?, ?, ?)
            """,
            (ts, task_name, reason, cycle_index),
        )
        self.conn.commit()

    def recent_run_halts(self, task_name: str | None = None, limit: int = 10) -> list[dict[str, str | int]]:
        if task_name:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, reason, cycle_index
                FROM run_halts
                WHERE task_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (task_name, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, reason, cycle_index
                FROM run_halts
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "ts": row["ts"],
                "task_name": row["task_name"],
                "reason": row["reason"],
                "cycle_index": row["cycle_index"],
            }
            for row in rows
        ]

    def save_regression_check(
        self,
        ts: str,
        reference_task: str,
        candidate_task: str,
        baseline_pass_rate: float,
        candidate_pass_rate: float,
        pass_rate_drop: float,
        shared_skills: int,
        passed: bool,
        notes: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO regression_checks (
                ts, reference_task, candidate_task, baseline_pass_rate,
                candidate_pass_rate, pass_rate_drop, shared_skills, passed, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                reference_task,
                candidate_task,
                baseline_pass_rate,
                candidate_pass_rate,
                pass_rate_drop,
                shared_skills,
                1 if passed else 0,
                notes,
            ),
        )
        self.conn.commit()

    def recent_regression_checks(self, limit: int = 10) -> list[dict[str, str | float | int]]:
        rows = self.conn.execute(
            """
            SELECT ts, reference_task, candidate_task, baseline_pass_rate,
                   candidate_pass_rate, pass_rate_drop, shared_skills, passed, notes
            FROM regression_checks
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "ts": row["ts"],
                "reference_task": row["reference_task"],
                "candidate_task": row["candidate_task"],
                "baseline_pass_rate": row["baseline_pass_rate"],
                "candidate_pass_rate": row["candidate_pass_rate"],
                "pass_rate_drop": row["pass_rate_drop"],
                "shared_skills": row["shared_skills"],
                "passed": row["passed"],
                "notes": row["notes"],
            }
            for row in rows
        ]

    def save_stability_check(
        self,
        ts: str,
        task_name: str,
        baseline_window: int,
        recent_window: int,
        baseline_pass_rate: float,
        recent_pass_rate: float,
        pass_rate_drift: float,
        recent_avg_confidence: float,
        recent_avg_error_rate: float,
        status: str,
        recommendations: str,
        notes: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO stability_checks (
                ts, task_name, baseline_window, recent_window,
                baseline_pass_rate, recent_pass_rate, pass_rate_drift,
                recent_avg_confidence, recent_avg_error_rate, status,
                recommendations, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                task_name,
                baseline_window,
                recent_window,
                baseline_pass_rate,
                recent_pass_rate,
                pass_rate_drift,
                recent_avg_confidence,
                recent_avg_error_rate,
                status,
                recommendations,
                notes,
            ),
        )
        self.conn.commit()

    def recent_stability_checks(self, task_name: str | None = None, limit: int = 10) -> list[dict[str, str | int | float]]:
        if task_name:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, baseline_window, recent_window,
                       baseline_pass_rate, recent_pass_rate, pass_rate_drift,
                       recent_avg_confidence, recent_avg_error_rate, status,
                       recommendations, notes
                FROM stability_checks
                WHERE task_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (task_name, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, baseline_window, recent_window,
                       baseline_pass_rate, recent_pass_rate, pass_rate_drift,
                       recent_avg_confidence, recent_avg_error_rate, status,
                       recommendations, notes
                FROM stability_checks
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "ts": row["ts"],
                "task_name": row["task_name"],
                "baseline_window": row["baseline_window"],
                "recent_window": row["recent_window"],
                "baseline_pass_rate": row["baseline_pass_rate"],
                "recent_pass_rate": row["recent_pass_rate"],
                "pass_rate_drift": row["pass_rate_drift"],
                "recent_avg_confidence": row["recent_avg_confidence"],
                "recent_avg_error_rate": row["recent_avg_error_rate"],
                "status": row["status"],
                "recommendations": row["recommendations"],
                "notes": row["notes"],
            }
            for row in rows
        ]

    def save_release_check(
        self,
        ts: str,
        task_name: str,
        preset: str,
        benchmark_pass_rate: float,
        regression_passed: bool,
        stability_status: str,
        readiness_score: float,
        passed: bool,
        notes: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO release_checks (
                ts, task_name, preset, benchmark_pass_rate, regression_passed,
                stability_status, readiness_score, passed, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                task_name,
                preset,
                benchmark_pass_rate,
                1 if regression_passed else 0,
                stability_status,
                readiness_score,
                1 if passed else 0,
                notes,
            ),
        )
        self.conn.commit()

    def recent_release_checks(self, task_name: str | None = None, limit: int = 10) -> list[dict[str, str | float | int]]:
        if task_name:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, preset, benchmark_pass_rate, regression_passed,
                       stability_status, readiness_score, passed, notes
                FROM release_checks
                WHERE task_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (task_name, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT ts, task_name, preset, benchmark_pass_rate, regression_passed,
                       stability_status, readiness_score, passed, notes
                FROM release_checks
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "ts": row["ts"],
                "task_name": row["task_name"],
                "preset": row["preset"],
                "benchmark_pass_rate": row["benchmark_pass_rate"],
                "regression_passed": row["regression_passed"],
                "stability_status": row["stability_status"],
                "readiness_score": row["readiness_score"],
                "passed": row["passed"],
                "notes": row["notes"],
            }
            for row in rows
        ]

    def record_revenue_entry(
        self,
        ts: str,
        task_name: str,
        finding_id: int,
        source_url: str,
        title: str,
        confidence: float,
        novelty: float,
        lead_score: float,
        estimated_value_usd: float,
        status: str,
        notes: str,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO revenue_ledger (
                ts, task_name, finding_id, source_url, title,
                confidence, novelty, lead_score, estimated_value_usd,
                status, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                task_name,
                finding_id,
                source_url,
                title,
                confidence,
                novelty,
                lead_score,
                estimated_value_usd,
                status,
                notes,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def revenue_entry_exists_for_finding(self, finding_id: int) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM revenue_ledger WHERE finding_id = ? LIMIT 1",
            (finding_id,),
        ).fetchone()
        return bool(row)

    def recent_revenue_entries(self, limit: int = 100, status: str | None = None) -> list[dict[str, str | int | float]]:
        if status:
            rows = self.conn.execute(
                """
                SELECT id, ts, task_name, finding_id, source_url, title,
                       confidence, novelty, lead_score, estimated_value_usd,
                       status, notes
                FROM revenue_ledger
                WHERE status = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (status, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT id, ts, task_name, finding_id, source_url, title,
                       confidence, novelty, lead_score, estimated_value_usd,
                       status, notes
                FROM revenue_ledger
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def revenue_summary(self, status: str | None = None) -> dict[str, float]:
        if status:
            row = self.conn.execute(
                """
                SELECT COUNT(*) AS item_count,
                       COALESCE(SUM(estimated_value_usd), 0.0) AS total_estimated_usd
                FROM revenue_ledger
                WHERE status = ?
                """,
                (status,),
            ).fetchone()
        else:
            row = self.conn.execute(
                """
                SELECT COUNT(*) AS item_count,
                       COALESCE(SUM(estimated_value_usd), 0.0) AS total_estimated_usd
                FROM revenue_ledger
                """
            ).fetchone()
        return {
            "item_count": float(row["item_count"]),
            "total_estimated_usd": float(row["total_estimated_usd"]),
        }

    def mark_revenue_entries_status(self, entry_ids: list[int], status: str) -> int:
        if not entry_ids:
            return 0
        qmarks = ",".join(["?"] * len(entry_ids))
        cur = self.conn.execute(
            f"UPDATE revenue_ledger SET status = ? WHERE id IN ({qmarks})",
            (status, *entry_ids),
        )
        self.conn.commit()
        return int(cur.rowcount)

    def record_payout_export(
        self,
        ts: str,
        destination_label: str,
        total_amount_usd: float,
        item_count: int,
        export_path: str,
        notes: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO payout_exports (
                ts, destination_label, total_amount_usd, item_count, export_path, notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (ts, destination_label, total_amount_usd, item_count, export_path, notes),
        )
        self.conn.commit()

    def update_revenue_estimated_value(self, entry_id: int, estimated_value_usd: float, notes_suffix: str = "") -> None:
        if notes_suffix:
            self.conn.execute(
                """
                UPDATE revenue_ledger
                SET estimated_value_usd = ?, notes = notes || ?
                WHERE id = ?
                """,
                (estimated_value_usd, notes_suffix, entry_id),
            )
        else:
            self.conn.execute(
                """
                UPDATE revenue_ledger
                SET estimated_value_usd = ?
                WHERE id = ?
                """,
                (estimated_value_usd, entry_id),
            )
        self.conn.commit()
