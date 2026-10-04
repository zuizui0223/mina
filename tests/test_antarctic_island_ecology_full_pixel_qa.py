import json
import unittest
from pathlib import Path

import pandas as pd

from scripts.run_antarctic_island_ecology_full_pixel_qa import shard_sites


class FullPixelQATests(unittest.TestCase):
    def test_six_shards_partition_84_sites_once(self):
        frame = pd.DataFrame({"site_id": [f"S{i:03d}" for i in range(84)]})
        shards = [shard_sites(frame, i, 6) for i in range(6)]
        self.assertEqual([len(x) for x in shards], [14] * 6)
        joined = pd.concat(shards, ignore_index=True)
        self.assertEqual(len(joined), 84)
        self.assertEqual(joined["site_id"].nunique(), 84)

    def test_contract_keeps_pilot_rule(self):
        root = Path(__file__).resolve().parents[1]
        full = json.loads(
            (root / "contracts" / "ANTARCTIC_ISLAND_ECOLOGY_PAPER2D_FULL_PIXEL_QA_V1.json")
            .read_text(encoding="utf-8")
        )
        pilot = json.loads(
            (root / "contracts" / "ANTARCTIC_ISLAND_ECOLOGY_PAPER2D_PIXEL_QA_V1.json")
            .read_text(encoding="utf-8")
        )
        p = pilot["pixel_support_metrics"]
        rule = full["per_site_rule"]
        self.assertEqual(rule["local_valid_fraction_threshold"], 0.50)
        self.assertEqual(rule["minimum_selected_distinct_year_scenes_per_epoch"], 3)
        self.assertEqual(rule["minimum_good_scenes_per_epoch"], 2)
        self.assertEqual(full["source_roster"]["full_pixel_candidate_physical_sites"], 84)
        self.assertEqual(full["source_roster"]["full_pixel_candidate_units"], 103)
        self.assertIn("fraction", " ".join(p["per_epoch"]).lower())

    def test_demographic_outcomes_remain_locked(self):
        root = Path(__file__).resolve().parents[1]
        full = json.loads(
            (root / "contracts" / "ANTARCTIC_ISLAND_ECOLOGY_PAPER2D_FULL_PIXEL_QA_V1.json")
            .read_text(encoding="utf-8")
        )
        self.assertTrue(full["continuation_gate_after_full_qa"]["demographic_magnitudes_remain_locked"])
        forbidden = " ".join(full["prohibited_changes"]).lower()
        self.assertIn("population outcomes", forbidden)
        self.assertIn("abundance trend", forbidden)


if __name__ == "__main__":
    unittest.main()
