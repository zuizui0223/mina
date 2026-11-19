import unittest
import pandas as pd
from shapely.geometry import box
from scripts.audit_glims_scar_rocktime_source_support import support_fragments, site_rows

def raw_rock(year,idx):
    return {"source_rock_row_index":idx,"source_rock_year":year,
            "source_date_precision":"year"}

class TestRockTimeOriginalSource(unittest.TestCase):
    def test_rock_source_must_follow_later_glims_source(self):
        diffs=[{"glims_id":"g1","early_year":1957,"late_year":2005,
                "geometry":box(0,0,3,3)}]
        rock=[box(1,1,2,2),box(0,0,1,1)]
        info=[raw_rock(2000,0),raw_rock(2024,1)]
        parts,qa=support_fragments(diffs,rock,info,[box(-1,-1,4,4)],["land_A"])
        self.assertEqual(qa["glims_id_with_later_dated_rock_on_scar_land"],1)
        self.assertEqual(qa["source_frags"],1)
        self.assertEqual(parts["land_A"][0]["rock_source_year"],2024)

    def test_offshore_rock_source_does_not_create_land_support(self):
        diffs=[{"glims_id":"g1","early_year":1957,"late_year":2005,
                "geometry":box(10,10,11,11)}]
        parts,qa=support_fragments(diffs,[box(10,10,11,11)],
                                   [raw_rock(2024,0)],[box(0,0,2,2)],["land_A"])
        self.assertEqual(len(parts),0)

    def test_site_on_other_land_not_counted_as_near_glacier(self):
        fragments={"land_B":[{"glims_id":"g1","glims_early_year":1957,
                               "glims_late_year":2005,
                               "rock_row":1,"rock_source_year":2024,
                               "rock_source_precision":"year",
                               "geometry":box(2.1,0,2.2,1),
                               "source_overlap_m2":0.1}]}
        sites=pd.DataFrame([
             {"site_id":"A","site_name":"A","longitude":1.5,"latitude":0.5},
             {"site_id":"B","site_name":"B","longitude":2.15,"latitude":0.5},
        ])
        r=site_rows(sites,[box(0,0,2,1),box(2.1,0,4,1)],
                    ["land_A","land_B"],fragments,lambda a,b:(a,b))
        self.assertFalse(r[0]["near_1km_source_only"])
        self.assertTrue(r[1]["near_1km_source_only"])
        self.assertFalse(r[1]["source_overlap_is_confirmed_new_rock"])
        self.assertFalse(r[1]["verified_surveyed_absence"])

if __name__=="__main__":
    unittest.main()
