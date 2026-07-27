from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Objective:
    id: str
    title: str
    query: str
    priority: float
    status: str = "pending"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Finding:
    objective_id: str
    source_url: str
    title: str
    snippet: str
    confidence: float
    novelty: float
    discovered_at: str = field(default_factory=utc_now_iso)


@dataclass
class TaskProfile:
    name: str
    novelty_weight: float = 1.0
    reliability_weight: float = 1.0
    speed_weight: float = 1.0
    notes: str = ""
