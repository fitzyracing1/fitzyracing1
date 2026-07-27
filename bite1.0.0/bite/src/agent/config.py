from dataclasses import dataclass, field
from pathlib import Path

from .mission import default_mission


@dataclass
class AgentConfig:
    db_path: Path = Path("agent_memory.db")
    report_path: Path = Path("latest_report.md")
    mission_name: str = default_mission().mission_name
    mission_statement: str = default_mission().mission_statement
    min_confidence: float = default_mission().min_confidence
    min_findings_per_cycle: int = default_mission().min_findings_per_cycle
    max_error_rate: float = default_mission().max_error_rate
    allowed_domains: set[str] = field(
        default_factory=lambda: {
            "arxiv.org",
            "github.com",
            "huggingface.co",
            "news.ycombinator.com",
            "openai.com",
            "microsoft.com",
            "anthropic.com",
            "techcrunch.com",
            "etenders.gov.ie",
            "enterprise-ireland.com",
            "idaireland.com",
            "siliconrepublic.com",
            "irishtimes.com",
            "ted.europa.eu",
            "gov.ie",
            "nasa.gov",
            "esa.int",
            "faa.gov",
            "sec.gov",
            "sam.gov",
        }
    )
    request_timeout_s: float = 10.0
    max_actions_per_cycle: int = 5
    max_fetches_per_cycle: int = 12
    max_retries_per_target: int = 2
    retry_backoff_s: float = 0.7
    max_consecutive_failures: int = 6
    min_extracted_chars: int = 160
    min_extraction_quality: float = 0.45
    min_accept_confidence: float = 0.45
    blocked_url_keywords: set[str] = field(
        default_factory=lambda: {
            "exploit",
            "malware",
            "weapon",
        }
    )
    blocked_content_keywords: set[str] = field(
        default_factory=lambda: {
            "build weapon",
            "bypass law",
            "steal credentials",
        }
    )
    max_policy_violations_per_cycle: int = 3
    halt_on_policy_violation_limit: bool = True
    user_agent: str = "AutonomousWebAgent/0.1"
