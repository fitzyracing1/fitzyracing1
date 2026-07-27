from __future__ import annotations

import unittest

from weighted_models.distributed import ContributionManager, compute_ready_player_one_score


class DistributedTests(unittest.TestCase):
    def test_contribution_queue_lifecycle(self) -> None:
        mgr = ContributionManager()
        ids = mgr.enqueue_tasks("rpo_match_score", [{"agility": 0.8}, {"agility": 0.2}])
        self.assertEqual(len(ids), 2)

        t1 = mgr.next_task("worker-a")
        self.assertIsNotNone(t1)
        assert t1 is not None

        ok = mgr.submit_result("worker-a", t1.task_id, {"score": 1.2})
        self.assertTrue(ok)

        stats = mgr.stats()
        self.assertEqual(stats["completed_tasks"], 1)
        self.assertEqual(stats["workers"].get("worker-a"), 1)

    def test_rpo_scoring_function_runs(self) -> None:
        payload = {
            "agility": 0.8,
            "focus": 0.7,
            "teamwork": 0.6,
            "resource_efficiency": 0.7,
            "risk_control": 0.8,
            "latency_ms": 55,
            "ioi_risk_weight": 0.2,
            "team_raid_matchmaking": 0.75,
            "quest_progression_score": 0.68,
        }
        score = compute_ready_player_one_score(payload)
        self.assertIsInstance(score, float)


if __name__ == "__main__":
    unittest.main()
