import unittest
import numpy as np
from scripts.audit_aadc_landsat_local_qa_pilot import qa_flags
class TestSourceQABits(unittest.TestCase):
    def test_cloud_and_snow_not_equivalent_to_new_rock(self):
        a=np.array([0,8,32,128,16,1],dtype=np.uint16)
        x=qa_flags(a)
        self.assertEqual(x["pixel_count"],6)
        self.assertEqual(x["usable_qa_pixels"],3)
        self.assertEqual(x["snow_flagged_valid_pixels"],1)
        self.assertEqual(x["water_flagged_valid_pixels"],1)
        self.assertFalse(x["clear_QA_proves_bare_rock"])
if __name__=="__main__":
    unittest.main()
