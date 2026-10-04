import unittest
import pandas as pd
from scripts.diagnose_published_guano_unmatched_scenes import parse_source, select_points

class UnmatchedSceneDiagnosticTests(unittest.TestCase):
    def test_parse_source(self):
        x=parse_source("LE71241082001018SGS00")
        self.assertEqual(x["published_path"],124)
        self.assertEqual(x["published_row"],108)
        self.assertEqual(x["date"],"2001-01-18")
    def test_point_selection(self):
        d=pd.DataFrame({"latitude":range(20),"longitude":range(20)})
        x=select_points(d,7)
        self.assertEqual(len(x),7)
        self.assertEqual(x.latitude.min(),0)
        self.assertEqual(x.latitude.max(),19)

if __name__=="__main__":
    unittest.main()
