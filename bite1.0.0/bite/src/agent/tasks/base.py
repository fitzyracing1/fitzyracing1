from dataclasses import dataclass


@dataclass
class SearchTarget:
    name: str
    url: str
    reliability: float


class TaskPlugin:
    name: str = "base"

    def get_targets(self) -> list[SearchTarget]:
        raise NotImplementedError

    def keywords(self) -> list[str]:
        raise NotImplementedError

    def objective_boost(self) -> float:
        return 1.0

    def skill_tags(self) -> set[str]:
        return {"source-validation", "evidence-scoring"}
