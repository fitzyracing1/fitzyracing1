from dataclasses import dataclass

@dataclass
class SolutionInput:
    workflow_steps: float
    integration_points: float
    automation_window_hours: float

def score_risk(inp: SolutionInput) -> float:
    score = 0.0
    if inp.workflow_steps > 25:
        score += 0.35
    if inp.integration_points > 8:
        score += 0.25
    if inp.automation_window_hours < 4:
        score += 0.30
    return min(1.0, score)

def build_output(inp: SolutionInput) -> dict:
    risk = score_risk(inp)
    return {
        'workflow_steps': inp.workflow_steps,
        'integration_points': inp.integration_points,
        'automation_window_hours': inp.automation_window_hours,
        'risk_score': risk,
        'risk_band': 'high' if risk >= 0.7 else 'medium' if risk >= 0.35 else 'low',
    }
