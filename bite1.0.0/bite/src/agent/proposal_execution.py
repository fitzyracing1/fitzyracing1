import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return cleaned[:80] or "proposal_project"


def parse_proposal_metadata(path: Path) -> dict[str, str]:
    metadata = {"title": path.stem, "source_url": ""}
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("# Proposal:"):
            metadata["title"] = line.replace("# Proposal:", "", 1).strip()
        elif line.startswith("- Source:"):
            metadata["source_url"] = line.replace("- Source:", "", 1).strip()
    return metadata


def parse_proposal_title(path: Path) -> str:
    return parse_proposal_metadata(path)["title"]


def parse_proposal_source_repo_url(path: Path) -> str:
    source_url = parse_proposal_metadata(path)["source_url"]
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"}:
        return ""
    if parsed.netloc.lower() != "github.com":
        return ""

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return ""

    owner = parts[0]
    repo = parts[1].removesuffix(".git")
    return f"https://github.com/{owner}/{repo}.git"


def mark_proposal_execution(path: Path, status: str, branch: str, commit_hash: str) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## Execution Status"
    block = (
        "\n## Execution Status\n"
        f"- Status: {status}\n"
        f"- Branch: {branch}\n"
        f"- Commit: {commit_hash or 'n/a'}\n"
    )
    if marker in text:
        # Replace existing status block conservatively from marker to end.
        new_text = text.split(marker)[0].rstrip() + block + "\n"
        path.write_text(new_text, encoding="utf-8")
        return
    path.write_text(text.rstrip() + "\n" + block + "\n", encoding="utf-8")


@dataclass
class ProposalExecutionResult:
    proposal_path: Path
    product_name: str
    project_dir: Path
    spec_path: Path
    ok: bool
    message: str
    branch: str = ""
    commit_hash: str = ""
