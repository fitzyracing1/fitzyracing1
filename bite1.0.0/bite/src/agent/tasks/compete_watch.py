from .base import SearchTarget, TaskPlugin


class CompeteWatchTask(TaskPlugin):
    """Scans all major sources to identify popular projects worth competing against."""

    name = "compete_watch"

    def get_targets(self) -> list[SearchTarget]:
        return [
            SearchTarget("GitHub Trending", "https://github.com/trending", 0.95),
            SearchTarget("Hacker News", "https://news.ycombinator.com/", 0.9),
            SearchTarget("Hugging Face", "https://huggingface.co/models", 0.88),
            SearchTarget("ArXiv CS", "https://arxiv.org/list/cs/new", 0.85),
            SearchTarget("TechCrunch", "https://techcrunch.com/", 0.75),
            SearchTarget("GitHub Trending Python", "https://github.com/trending/python", 0.92),
            SearchTarget("GitHub Trending JavaScript", "https://github.com/trending/javascript", 0.88),
            SearchTarget("GitHub Trending Rust", "https://github.com/trending/rust", 0.85),
        ]

    def keywords(self) -> list[str]:
        return [
            # Established tools ripe for competition
            "agent",
            "framework",
            "platform",
            "sdk",
            "api",
            "cli",
            "dashboard",
            "automation",
            "workflow",
            "orchestration",
            "pipeline",
            "tool",
            "library",
            "open-source",
            "saas",
            "self-hosted",
            "llm",
            "model",
            "inference",
            "deploy",
            "monitor",
            "observability",
            "devops",
            "productivity",
            "integration",
            "connector",
            "plugin",
            "extension",
            "server",
            "client",
            "backend",
            "frontend",
            "fullstack",
            "search",
            "vector",
            "embedding",
            "database",
            "cache",
            "queue",
            "scheduler",
            "scraper",
            "crawler",
            "parser",
            "compiler",
            "runtime",
            "interpreter",
            "benchmark",
            "testing",
            "linter",
            "formatter",
            "bundler",
            "builder",
            "generator",
            "template",
            "boilerplate",
            "starter",
            "kit",
            "suite",
        ]

    def objective_boost(self) -> float:
        return 1.25

    def skill_tags(self) -> set[str]:
        return {
            "competitive-analysis",
            "trend-scanning",
            "source-validation",
            "evidence-scoring",
            "problem-discovery",
            "solution-design",
            "release-tracking",
        }
