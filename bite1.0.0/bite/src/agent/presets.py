from dataclasses import replace

from .config import AgentConfig


def available_presets() -> list[str]:
    return ["balanced", "conservative", "aggressive"]


def apply_preset(cfg: AgentConfig, preset: str) -> AgentConfig:
    p = preset.lower()
    if p == "balanced":
        return cfg
    if p == "conservative":
        return replace(
            cfg,
            max_fetches_per_cycle=8,
            max_retries_per_target=3,
            max_consecutive_failures=4,
            min_extraction_quality=0.55,
            min_accept_confidence=0.55,
            max_policy_violations_per_cycle=2,
        )
    if p == "aggressive":
        return replace(
            cfg,
            max_fetches_per_cycle=20,
            max_retries_per_target=1,
            max_consecutive_failures=10,
            min_extraction_quality=0.25,
            min_accept_confidence=0.20,
            max_policy_violations_per_cycle=4,
        )
    raise ValueError(f"Unknown preset: {preset}")
