import hashlib
from datetime import datetime, timezone

from .models import Objective


def _obj_id(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]


def default_objectives_for_task(task_name: str) -> list[Objective]:
    now = datetime.now(timezone.utc).isoformat()

    if task_name == "trend_watch":
        seeds = [
            ("Track notable new AI repos this week", "site:github.com ai agent framework released", 0.95),
            ("Find practical browser automation updates", "browser automation release notes", 0.85),
            ("Compare major model provider announcements", "model provider new feature release", 0.8),
        ]
    elif task_name == "irish_tech_watch":
        seeds = [
            (
                "Track Irish public-sector digital transformation tenders",
                "ireland public sector digital transformation tender etenders",
                0.99,
            ),
            (
                "Identify Irish SME modernization opportunities",
                "ireland sme modernization cloud migration workflow automation",
                0.96,
            ),
            (
                "Monitor Irish and EU funding for applied AI and cybersecurity",
                "enterprise ireland ida eu funding ai cybersecurity",
                0.94,
            ),
            (
                "Find compliance-heavy software delivery opportunities",
                "ireland gdpr nist iso27001 software compliance project",
                0.92,
            ),
        ]
    elif task_name == "security_watch":
        seeds = [
            ("Find new vulnerability advisories", "security advisory CVE browser automation", 0.95),
            ("Track dependency exploit reports", "dependency exploit report python package", 0.9),
            ("Monitor incident response postmortems", "incident postmortem outage analysis", 0.8),
            ("Track zero-day mitigation guidance", "zero day mitigation guidance cisa", 0.88),
        ]
    elif task_name == "aerospace_software":
        seeds = [
            (
                "Generate aerospace mission planning software requirements",
                "mission planning software requirements telemetry guidance",
                0.99,
            ),
            (
                "Design flight software architecture for high-reliability operations",
                "flight software architecture fault tolerance avionics",
                0.95,
            ),
            (
                "Build verification and simulation test strategy",
                "simulation verification test strategy software",
                0.92,
            ),
            (
                "Package release artifacts for mission planning product",
                "software release packaging aerospace mission planner",
                0.88,
            ),
        ]
    elif task_name == "software_solver":
        seeds = [
            (
                "Find enterprise platform modernization opportunities",
                "enterprise platform modernization migration legacy stack",
                0.995,
            ),
            (
                "Identify compliance-driven software transformation projects",
                "soc2 hipaa pci compliance software program transformation",
                0.985,
            ),
            (
                "Detect high-value integration and data pipeline bottlenecks",
                "enterprise api integration data pipeline reliability bottleneck",
                0.97,
            ),
            (
                "Track large-scope reliability and observability initiatives",
                "sre observability reliability initiative platform engineering",
                0.96,
            ),
        ]
    else:
        seeds = [
            ("General tech landscape scan", "software release notes this week", 0.7),
            ("Identify high-signal sources", "engineering blog launch update", 0.65),
        ]

    out: list[Objective] = []
    for title, query, priority in seeds:
        seed = f"{task_name}|{title}|{query}"
        out.append(
            Objective(
                id=_obj_id(seed),
                title=title,
                query=query,
                priority=priority,
                status="pending",
                created_at=now,
                updated_at=now,
                metadata={"task": task_name},
            )
        )
    return out


def reprioritize(objectives: list[Objective], novelty_boost: float = 1.0) -> list[Objective]:
    for obj in objectives:
        obj.priority = round(obj.priority * novelty_boost, 4)
    return sorted(objectives, key=lambda x: x.priority, reverse=True)
