from dataclasses import dataclass

@dataclass
class MissionInput:
    payload_mass_kg: float
    orbit_altitude_km: float
    launch_window_hours: float

def score_risk(inp: MissionInput) -> float:
    score = 0.0
    if inp.payload_mass_kg > 5000:
        score += 0.35
    if inp.orbit_altitude_km > 800:
        score += 0.25
    if inp.launch_window_hours < 2:
        score += 0.30
    return min(1.0, score)

def build_plan(inp: MissionInput) -> dict:
    risk = score_risk(inp)
    return {
        'payload_mass_kg': inp.payload_mass_kg,
        'orbit_altitude_km': inp.orbit_altitude_km,
        'launch_window_hours': inp.launch_window_hours,
        'risk_score': risk,
        'risk_band': 'high' if risk >= 0.7 else 'medium' if risk >= 0.35 else 'low',
    }
