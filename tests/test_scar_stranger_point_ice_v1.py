import importlib.util,unittest
from pathlib import Path
f=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/scar_stranger_point_ice_v1/analyze.py"
s=importlib.util.spec_from_file_location("stranger",f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Spec(unittest.TestCase):
 def test_association(self):
  self.assertAlmostEqual(m.pearson([1,2,3],[3,2,1]),-1)
  self.assertEqual(m.rank([5,5,8]),[1.5,1.5,3])
  self.assertEqual(m.summary_corr([1,2,3,4,5],[4,4,4,4,4])["pearson"],None)
if __name__=="__main__":unittest.main()
