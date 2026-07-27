import csv
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def utc_ts() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PayoutConfig:
    destination_label: str
    account_holder: str
    routing_number_masked: str
    account_number_masked: str


def load_payout_config_from_env() -> PayoutConfig:
    # Keep sensitive details out of code and source control.
    return PayoutConfig(
        destination_label=os.getenv("PAYOUT_DESTINATION_LABEL", "primary_business_account"),
        account_holder=os.getenv("PAYOUT_ACCOUNT_HOLDER", "PLACEHOLDER_NAME"),
        routing_number_masked=os.getenv("PAYOUT_ROUTING_MASKED", "***-PLACEHOLDER"),
        account_number_masked=os.getenv("PAYOUT_ACCOUNT_MASKED", "***-PLACEHOLDER"),
    )


def payout_ready_rows(entries: list[dict[str, str | int | float]], cfg: PayoutConfig) -> list[dict[str, str | int | float]]:
    out: list[dict[str, str | int | float]] = []
    for e in entries:
        out.append(
            {
                "ledger_id": e["id"],
                "ts": e["ts"],
                "task_name": e["task_name"],
                "title": e["title"],
                "source_url": e["source_url"],
                "estimated_value_usd": e["estimated_value_usd"],
                "destination_label": cfg.destination_label,
                "account_holder": cfg.account_holder,
                "routing_number_masked": cfg.routing_number_masked,
                "account_number_masked": cfg.account_number_masked,
                "transfer_status": "requires_manual_approval",
            }
        )
    return out


def write_payout_export(path: Path, rows: list[dict[str, str | int | float]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        if not path.exists():
            path.write_text("", encoding="utf-8")
        return 0

    headers = [
        "ledger_id",
        "ts",
        "task_name",
        "title",
        "source_url",
        "estimated_value_usd",
        "destination_label",
        "account_holder",
        "routing_number_masked",
        "account_number_masked",
        "transfer_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return len(rows)
