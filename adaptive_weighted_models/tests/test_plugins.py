from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from weighted_models.plugins import bootstrap_ready_player_one
from weighted_models.rag import load_index, search_index


class PluginBootstrapTests(unittest.TestCase):
    def test_ready_player_one_bootstrap_creates_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "rpo"
            result = bootstrap_ready_player_one(out)

            self.assertEqual(result.plugin, "ready_player_one")
            self.assertEqual(result.profile, "mechanics")
            self.assertTrue(result.index_path.exists())
            self.assertTrue(result.model_path.exists())
            self.assertTrue(result.train_csv.exists())
            self.assertTrue(result.predict_csv.exists())
            self.assertTrue(result.predictions_csv.exists())
            self.assertGreater(result.train_rows, 10)

            with result.train_csv.open("r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
            expected_cols = {
                "faction_gunters",
                "faction_sixers",
                "faction_rebels",
                "avatar_support",
                "quest_progression_score",
                "ioi_threat",
                "ioi_risk_weight",
                "team_raid_matchmaking",
            }
            self.assertTrue(expected_cols.issubset(set(header)))

            idx = load_index(result.index_path)
            matches = search_index(idx, "drift retraining", top_k=3)
            self.assertGreaterEqual(len(matches), 1)

    def test_ready_player_one_live_ops_bootstrap_creates_live_ops_columns(self) -> None:
        from weighted_models.plugins import bootstrap_ready_player_one_live_ops

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "rpo_live_ops"
            result = bootstrap_ready_player_one_live_ops(out)

            self.assertEqual(result.plugin, "ready_player_one")
            self.assertEqual(result.profile, "live_ops")
            self.assertTrue(result.train_csv.exists())
            self.assertTrue(result.predict_csv.exists())

            with result.train_csv.open("r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
            live_ops_cols = {
                "season",
                "seasonal_leaderboard_drift",
                "faction_meta_shift",
                "raid_role_balance",
            }
            self.assertTrue(live_ops_cols.issubset(set(header)))


if __name__ == "__main__":
    unittest.main()
