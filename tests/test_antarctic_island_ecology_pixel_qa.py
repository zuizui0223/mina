import unittest
from datetime import datetime

import numpy as np
import pandas as pd

from scripts.audit_antarctic_island_ecology_pixel_qa import (
    BIT_CLOUD,
    BIT_CLOUD_SHADOW,
    BIT_DILATED_CLOUD,
    BIT_FILL,
    BIT_SNOW,
    BIT_WATER,
    qa_flag,
    select_scenes,
    program_pass,
)


def feature(item_id, dt, cloud):
    return {
        "id": item_id,
        "properties": {"datetime": dt, "eo:cloud_cover": cloud},
        "assets": {"qa_pixel": {"href": "https://example.invalid/a.tif"}},
    }


class PixelQAPilotTests(unittest.TestCase):
    def test_qa_bits_decode_independently(self):
        values = np.array([
            0,
            1 << BIT_FILL,
            1 << BIT_DILATED_CLOUD,
            1 << BIT_CLOUD,
            1 << BIT_CLOUD_SHADOW,
            1 << BIT_SNOW,
            1 << BIT_WATER,
            (1 << BIT_CLOUD) | (1 << BIT_SNOW),
        ], dtype=np.uint16)
        self.assertEqual(int(qa_flag(values, BIT_CLOUD).sum()), 2)
        self.assertEqual(int(qa_flag(values, BIT_SNOW).sum()), 2)
        self.assertEqual(int(qa_flag(values, BIT_WATER).sum()), 1)

    def test_scene_selection_one_per_year_and_spans_epoch(self):
        features = [
            feature("a1984bad", "1984-12-01T00:00:00Z", 60),
            feature("a1984good", "1984-12-15T00:00:00Z", 20),
            feature("a1985", "1985-01-01T00:00:00Z", 30),
            feature("a1986", "1986-02-01T00:00:00Z", 30),
            feature("a1987", "1987-12-01T00:00:00Z", 30),
            feature("a1988", "1988-01-01T00:00:00Z", 30),
            feature("a1989", "1989-02-01T00:00:00Z", 30),
            feature("a1990", "1990-12-01T00:00:00Z", 30),
            feature("winter", "1991-07-01T00:00:00Z", 1),
            feature("cloudy", "1992-12-01T00:00:00Z", 90),
        ]
        picked = select_scenes(features, max_scenes=5)
        years = [datetime.fromisoformat(x["properties"]["datetime"].replace("Z","+00:00")).year for x in picked]
        self.assertEqual(len(years), 5)
        self.assertEqual(years[0], 1984)
        self.assertEqual(years[-1], 1990)
        self.assertEqual(picked[0]["id"], "a1984good")
        self.assertEqual(len(set(years)), 5)

    def test_program_gate_requires_beaufort_and_major_region_replication(self):
        rows = []
        for region in [
            "Central-west Antarctic Peninsula",
            "South Shetland Islands",
            "Victoria Land",
        ]:
            for i in range(3):
                rows.append({
                    "site_id": f"{region[:2]}{i}",
                    "region": region,
                    "site_pass": True,
                })
        rows.append({"site_id": "BEAU", "region": "Victoria Land", "site_pass": True})
        for i in range(4):
            rows.append({"site_id": f"M{i}", "region": f"Minor{i}", "site_pass": True})
        frame = pd.DataFrame(rows)
        ok, detail = program_pass(frame)
        self.assertTrue(ok)
        self.assertTrue(detail["beaufort_pass"])
        self.assertGreaterEqual(detail["passing_sites"], 11)

        frame.loc[frame["site_id"] == "BEAU", "site_pass"] = False
        ok, _ = program_pass(frame)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
