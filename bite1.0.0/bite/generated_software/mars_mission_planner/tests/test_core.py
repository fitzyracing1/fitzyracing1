import unittest

from mission_planner.core import MissionInput, build_plan, score_risk

class CoreTests(unittest.TestCase):
    def test_score_risk_low(self):
        inp = MissionInput(payload_mass_kg=1200, orbit_altitude_km=450, launch_window_hours=6)
        self.assertLess(score_risk(inp), 0.35)

    def test_build_plan_has_keys(self):
        inp = MissionInput(payload_mass_kg=6000, orbit_altitude_km=900, launch_window_hours=1.5)
        plan = build_plan(inp)
        self.assertIn('risk_score', plan)
        self.assertIn('risk_band', plan)

if __name__ == '__main__':
    unittest.main()
