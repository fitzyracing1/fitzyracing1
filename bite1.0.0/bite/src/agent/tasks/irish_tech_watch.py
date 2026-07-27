from .base import SearchTarget, TaskPlugin


class IrishTechWatchTask(TaskPlugin):
    name = "irish_tech_watch"

    def get_targets(self) -> list[SearchTarget]:
        return [
            SearchTarget("eTenders", "https://www.etenders.gov.ie/", 0.95),
            SearchTarget("Enterprise Ireland", "https://www.enterprise-ireland.com/en/news/", 0.9),
            SearchTarget("IDA Ireland Newsroom", "https://www.idaireland.com/latest-news/newsroom", 0.88),
            SearchTarget("Gov.ie Enterprise News", "https://www.gov.ie/en/news/", 0.82),
            SearchTarget("Silicon Republic", "https://www.siliconrepublic.com/", 0.8),
            SearchTarget("EU TED", "https://ted.europa.eu/en/", 0.78),
        ]

    def keywords(self) -> list[str]:
        return [
            "ireland",
            "irish",
            "dublin",
            "cork",
            "galway",
            "limerick",
            "public sector",
            "procurement",
            "etenders",
            "digital transformation",
            "cybersecurity",
            "ai",
            "healthtech",
            "fintech",
            "govtech",
            "enterprise",
            "compliance",
            "gdpr",
            "european union",
            "eu",
            "innovation",
            "funding",
            "grant",
            "sme",
        ]

    def objective_boost(self) -> float:
        return 1.18

    def skill_tags(self) -> set[str]:
        return {
            "regional-market-analysis",
            "procurement-analysis",
            "compliance-scoping",
            "source-validation",
            "evidence-scoring",
        }
