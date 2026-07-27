from .base import SearchTarget, TaskPlugin


class TrendWatchTask(TaskPlugin):
    name = "trend_watch"

    def get_targets(self) -> list[SearchTarget]:
        return [
            SearchTarget("Hacker News", "https://news.ycombinator.com/", 0.85),
            SearchTarget("GitHub Trending", "https://github.com/trending", 0.9),
            SearchTarget("TechCrunch", "https://techcrunch.com/", 0.7),
        ]

    def keywords(self) -> list[str]:
        return ["agent", "release", "model", "automation", "open-source", "benchmark"]

    def objective_boost(self) -> float:
        return 1.1

    def skill_tags(self) -> set[str]:
        return {"trend-scanning", "source-validation", "evidence-scoring", "release-tracking"}
