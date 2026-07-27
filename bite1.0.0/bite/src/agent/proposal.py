import re
from pathlib import Path


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    return cleaned.strip("-")[:80] or "proposal"


def build_proposal_markdown(entry: dict[str, str | int | float]) -> str:
    title = str(entry["title"])
    task_name = str(entry["task_name"])
    source_url = str(entry["source_url"])
    est_value = float(entry["estimated_value_usd"])
    lead_score = float(entry["lead_score"])

    if task_name == "irish_tech_watch":
        return "\n".join(
            [
                f"# Proposal: {title}",
                "",
                "## Opportunity Summary",
                f"- Task Scope: {task_name}",
                f"- Source: {source_url}",
                f"- Lead Score: {lead_score:.2f}",
                f"- Estimated Value (USD): {est_value:.2f}",
                "",
                "## Ireland Market Fit",
                "- Target Region: Ireland (with EU-aligned delivery model)",
                "- Typical Buyers: public sector agencies, regulated enterprises, and scaling SMEs",
                "- Delivery Priority: measurable workflow automation and compliance-safe deployment",
                "",
                "## Proposed Solution",
                "1. Discovery and requirements validation with Irish stakeholder constraints",
                "2. Milestone delivery plan with procurement-ready outputs",
                "3. Build, integration, and verification with security-by-default controls",
                "4. Operator handoff with KPI tracking and change-management notes",
                "",
                "## Delivery Scope",
                "- Working software increment",
                "- Validation checklist",
                "- Deployment and rollback notes",
                "- Data residency plan aligned to EU/EEA hosting expectations",
                "",
                "## Commercial Terms (Draft)",
                f"- Target package anchor: ${est_value:.2f}",
                "- Pricing note: VAT treatment and procurement terms finalized at contracting stage",
                "- Payment terms: net-15 after milestone acceptance",
                "",
                "## Next Action",
                "Schedule a 20-minute qualification call and confirm implementation constraints.",
                "",
            ]
        )

    return "\n".join(
        [
            f"# Proposal: {title}",
            "",
            "## Opportunity Summary",
            f"- Task Scope: {task_name}",
            f"- Source: {source_url}",
            f"- Lead Score: {lead_score:.2f}",
            f"- Estimated Value (USD): {est_value:.2f}",
            "",
            "## Problem Hypothesis",
            "This signal suggests a software workflow bottleneck or capability gap with business impact.",
            "",
            "## Proposed Solution",
            "1. Discovery and requirements validation",
            "2. Implementation plan with milestone-based delivery",
            "3. Build, integration, and verification",
            "4. Operator handoff and success metrics",
            "",
            "## Delivery Scope",
            "- Working software increment",
            "- Validation checklist",
            "- Deployment and rollback notes",
            "",
            "## Commercial Terms (Draft)",
            f"- Target package anchor: ${est_value:.2f}",
            "- Payment terms: net-15 after milestone acceptance",
            "",
            "## Next Action",
            "Schedule a 20-minute qualification call and confirm implementation constraints.",
            "",
        ]
    )


def write_proposal_file(output_dir: Path, entry: dict[str, str | int | float], overwrite: bool = False) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    lead_id = int(entry["id"])
    slug = _slugify(str(entry["title"]))
    path = output_dir / f"proposal_{lead_id}_{slug}.md"

    if path.exists() and not overwrite:
        return path

    path.write_text(build_proposal_markdown(entry), encoding="utf-8")
    return path


def build_competition_proposal_markdown(entry: dict[str, str | int | float]) -> str:
    title = str(entry["title"])
    source_url = str(entry["source_url"])
    est_value = float(entry["estimated_value_usd"])
    lead_score = float(entry["lead_score"])

    return "\n".join(
        [
            f"# Competition Proposal: Build Alternative to {title}",
            "",
            "## Target",
            f"- Competing Against: [{title}]({source_url})",
            f"- Lead Score: {lead_score:.2f}",
            f"- Estimated Market Value (USD): {est_value:.2f}",
            "",
            "## Competitive Opportunity",
            f"**{title}** has demonstrated market traction and user demand. This is an opportunity to build a",
            "competing alternative with a differentiated feature set, better pricing, or improved UX.",
            "",
            "## Differentiation Strategy",
            "1. Identify the top 3 complaints/limitations in the target's issue tracker and community",
            "2. Design around those pain points as first-class features",
            "3. Offer open-source core + paid enterprise tier (vs. target's model)",
            "4. Ship a working v1 within 2 weeks to capture early adopter interest",
            "",
            "## Implementation Plan",
            "1. Reverse-engineer the target's public API/interface and replicate core feature surface",
            "2. Add differentiating capabilities not present in target",
            "3. Build docs, CLI, and SDK to lower the switching cost",
            "4. Publish to GitHub with permissive license to attract contributors",
            "",
            "## Delivery Scope",
            "- Working competing software with feature parity on core workflows",
            "- Benchmark comparison report (our implementation vs. target)",
            "- Migration guide for users switching from the target",
            "- Deployment-ready package with CI/CD",
            "",
            "## Commercial Terms (Draft)",
            f"- Target market size anchor: ${est_value:.2f}",
            "- Revenue model: open-core (free OSS + paid hosted/enterprise)",
            "- Payment terms: net-15 after milestone acceptance",
            "",
            "## Next Action",
            f"1. Clone and audit {source_url}",
            "2. File competitive feature matrix",
            "3. Begin implementation sprint",
            "",
        ]
    )


def write_competition_proposal_file(
    output_dir: Path, entry: dict[str, str | int | float], overwrite: bool = False
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    lead_id = int(entry["id"])
    slug = _slugify(str(entry["title"]))
    path = output_dir / f"compete_{lead_id}_{slug}.md"

    if path.exists() and not overwrite:
        return path

    path.write_text(build_competition_proposal_markdown(entry), encoding="utf-8")
    return path
