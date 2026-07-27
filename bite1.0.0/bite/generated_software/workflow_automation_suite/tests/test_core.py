import unittest

from solution_app.core import SolutionInput, build_output, score_risk

class CoreTests(unittest.TestCase):
    def test_score_risk_low(self):
        inp = SolutionInput(workflow_steps=8, integration_points=2, automation_window_hours=12)
        self.assertLess(score_risk(inp), 0.35)

    def test_build_output_has_keys(self):
        inp = SolutionInput(workflow_steps=30, integration_points=10, automation_window_hours=2)
        output = build_output(inp)
        self.assertIn('risk_score', output)
        self.assertIn('risk_band', output)

if __name__ == '__main__':
    unittest.main()
