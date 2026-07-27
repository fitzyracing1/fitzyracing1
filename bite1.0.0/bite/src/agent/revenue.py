import csv
from pathlib import Path
from typing import Iterable


def lead_score(confidence: float, novelty: float) -> float:
    return round((0.7 * confidence) + (0.3 * novelty), 4)


def revenue_angle(title: str, snippet: str) -> str:
    text = f"{title} {snippet}".lower()
    if any(k in text for k in ["migration", "platform", "erp", "crm", "data warehouse"]):
        return "Enterprise modernization and platform migration engagement"
    if any(k in text for k in ["soc2", "iso 27001", "hipaa", "pci", "governance"]):
        return "Compliance and governance transformation program"
    if "security" in text or "compliance" in text:
        return "Security/compliance advisory outreach"
    if "api" in text or "sdk" in text or "framework" in text:
        return "Implementation services and integration retainers"
    if "benchmark" in text or "performance" in text:
        return "Optimization consulting package"
    if "launch" in text or "product" in text or "release" in text:
        return "Early-adopter enablement and training"
    return "General AI automation consulting outreach"


def estimate_project_value_usd(
    title: str,
    snippet: str,
    source_url: str,
    confidence: float,
    novelty: float,
    base_project_value: float = 25000.0,
    max_project_value: float = 500000.0,
) -> float:
    text = f"{title} {snippet}".lower()
    score = lead_score(confidence, novelty)

    multiplier = 1.0
    if any(k in text for k in ["enterprise", "platform", "migration", "multi-tenant", "architecture"]):
        multiplier += 0.55
    if any(k in text for k in ["security", "compliance", "soc2", "hipaa", "pci", "governance"]):
        multiplier += 0.45
    if any(k in text for k in ["integration", "api", "data pipeline", "observability", "sre"]):
        multiplier += 0.35
    if "github.com" in source_url or "arxiv.org" in source_url:
        multiplier += 0.15

    # Scale score into project-size bands while keeping a realistic floor.
    raw_value = base_project_value * (0.7 + (2.4 * score)) * multiplier
    clamped = max(base_project_value * 0.6, min(raw_value, max_project_value))
    return round(clamped, 2)


def append_leads_csv(path: Path, leads: Iterable[dict[str, str | int | float]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(leads)
    headers = [
        "finding_id",
        "discovered_at",
        "objective_id",
        "objective_title",
        "title",
        "source_url",
        "confidence",
        "novelty",
        "lead_score",
        "revenue_angle",
    ]
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not exists:
            writer.writeheader()
        if not rows:
            return 0
        for row in rows:
            writer.writerow(
                {
                    "finding_id": row["id"],
                    "discovered_at": row["discovered_at"],
                    "objective_id": row["objective_id"],
                    "objective_title": row["objective_title"],
                    "title": row["title"],
                    "source_url": row["source_url"],
                    "confidence": row["confidence"],
                    "novelty": row["novelty"],
                    "lead_score": lead_score(float(row["confidence"]), float(row["novelty"])),
                    "revenue_angle": revenue_angle(str(row["title"]), str(row["snippet"])),
                }
            )
    return len(rows)
