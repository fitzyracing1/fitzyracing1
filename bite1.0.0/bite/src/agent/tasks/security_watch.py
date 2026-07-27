from .base import SearchTarget, TaskPlugin


class SecurityWatchTask(TaskPlugin):
    name = "security_watch"

    def get_targets(self) -> list[SearchTarget]:
        return [
            SearchTarget("CISA Alerts", "https://www.cisa.gov/news-events/cybersecurity-advisories", 0.95),
            SearchTarget("NVD", "https://nvd.nist.gov/vuln", 0.93),
            SearchTarget("CERT", "https://www.us-cert.gov/ncas/alerts", 0.9),
        ]

    def keywords(self) -> list[str]:
        return ["cve", "advisory", "vulnerability", "exploit", "patch", "mitigation", "incident"]

    def objective_boost(self) -> float:
        return 1.05

    def skill_tags(self) -> set[str]:
        return {"policy-monitoring", "alert-triage", "evidence-scoring", "source-validation"}
