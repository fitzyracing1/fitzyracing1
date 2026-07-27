from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContributionTask:
    task_id: str
    task_type: str
    payload: dict[str, Any]
    status: str = "pending"  # pending, claimed, completed
    created_at: float = field(default_factory=time.time)
    claimed_by: str | None = None
    claimed_at: float | None = None
    completed_at: float | None = None


class ContributionManager:
    """In-memory contribution queue for hosted volunteer compute."""

    def __init__(self) -> None:
        self.tasks: list[ContributionTask] = []
        self.results: list[dict[str, Any]] = []
        self.worker_stats: dict[str, int] = {}

    def enqueue_tasks(self, task_type: str, payloads: list[dict[str, Any]]) -> list[str]:
        ids: list[str] = []
        for payload in payloads:
            task_id = str(uuid.uuid4())
            self.tasks.append(ContributionTask(task_id=task_id, task_type=task_type, payload=payload))
            ids.append(task_id)
        return ids

    def next_task(self, worker_id: str) -> ContributionTask | None:
        for task in self.tasks:
            if task.status == "pending":
                task.status = "claimed"
                task.claimed_by = worker_id
                task.claimed_at = time.time()
                return task
        return None

    def submit_result(self, worker_id: str, task_id: str, result: dict[str, Any]) -> bool:
        for task in self.tasks:
            if task.task_id == task_id and task.status in {"claimed", "pending"}:
                task.status = "completed"
                task.completed_at = time.time()
                if task.claimed_by is None:
                    task.claimed_by = worker_id
                self.results.append(
                    {
                        "task_id": task_id,
                        "task_type": task.task_type,
                        "worker_id": worker_id,
                        "result": result,
                        "timestamp": time.time(),
                    }
                )
                self.worker_stats[worker_id] = self.worker_stats.get(worker_id, 0) + 1
                return True
        return False

    def stats(self) -> dict[str, Any]:
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == "completed")
        claimed = sum(1 for t in self.tasks if t.status == "claimed")
        pending = sum(1 for t in self.tasks if t.status == "pending")
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "claimed_tasks": claimed,
            "pending_tasks": pending,
            "workers": self.worker_stats,
            "result_count": len(self.results),
        }


def compute_ready_player_one_score(payload: dict[str, Any]) -> float:
    """Reference worker-side scoring for RPO contribution tasks."""

    agility = float(payload.get("agility", 0.0))
    focus = float(payload.get("focus", 0.0))
    teamwork = float(payload.get("teamwork", 0.0))
    efficiency = float(payload.get("resource_efficiency", 0.0))
    risk_control = float(payload.get("risk_control", 0.0))
    latency_ms = float(payload.get("latency_ms", 120.0))
    ioi_risk_weight = float(payload.get("ioi_risk_weight", 0.0))
    team_raid_matchmaking = float(payload.get("team_raid_matchmaking", 0.0))
    quest_progression_score = float(payload.get("quest_progression_score", 0.0))

    score = (
        1.25 * agility
        + 1.2 * focus
        + 1.0 * teamwork
        + 1.0 * efficiency
        + 0.75 * risk_control
        + 1.05 * quest_progression_score
        + 0.85 * team_raid_matchmaking
        - 0.007 * latency_ms
        - 0.95 * ioi_risk_weight
    )
    return float(score)
