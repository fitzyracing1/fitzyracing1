from dataclasses import dataclass


@dataclass
class MissionContract:
    mission_name: str
    mission_statement: str
    min_confidence: float
    min_findings_per_cycle: int
    max_error_rate: float

    def validate(self) -> None:
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0.0, 1.0]")
        if self.min_findings_per_cycle < 0:
            raise ValueError("min_findings_per_cycle must be >= 0")
        if not 0.0 <= self.max_error_rate <= 1.0:
            raise ValueError("max_error_rate must be in [0.0, 1.0]")


def default_mission() -> MissionContract:
    return MissionContract(
        mission_name="daily_trend_intel",
        mission_statement="Track high-signal AI tooling changes daily with low false positives.",
        min_confidence=0.55,
        min_findings_per_cycle=2,
        max_error_rate=0.35,
    )
