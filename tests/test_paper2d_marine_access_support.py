import unittest

import pandas as pd

from scripts.audit_paper2d_marine_access_support import file_url, required_year_months


class MarineAccessSupportTests(unittest.TestCase):
    def test_file_url_is_frozen_v4_south_monthly(self):
        url = file_url(1984, 11)
        self.assertIn("/south/monthly/geotiff/11_Nov/", url)
        self.assertTrue(url.endswith("S_198411_concentration_v4.0.tif"))

    def test_required_months_follow_frozen_site_epochs(self):
        frame = pd.DataFrame([{
            "early_window_start": 1984,
            "early_window_end": 1985,
            "late_window_start": 2016,
            "late_window_end": 2017,
        }])
        got = required_year_months(frame)
        self.assertEqual(len(got), 12)
        self.assertIn((1984, 1), got)
        self.assertIn((1985, 12), got)
        self.assertIn((2017, 11), got)


if __name__ == "__main__":
    unittest.main()
