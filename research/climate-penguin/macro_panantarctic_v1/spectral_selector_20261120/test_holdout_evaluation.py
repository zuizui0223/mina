import unittest
import pandas as pd
from evaluate_matched_holdout import site_rates,region_intervals,shared_scene_blocks

class HoldoutTests(unittest.TestCase):
    def test_equal_sites_not_equal_regions(self):
        rows=[]
        for site,region,correct in [('a','r1',1),('b','r2',0),('c','r2',0),('d','r2',0)]:
            for label in [0,1]:rows.append(dict(site_id=site,region=region,label=label,correct=correct))
        estimates=region_intervals(pd.DataFrame(rows),n=100)
        self.assertEqual(estimates['positive_recovery']['estimate'],.25)
        self.assertEqual(estimates['candidate_background_rejection']['estimate'],.25)

    def test_scenes_then_sites_not_pooled_pixels(self):
        d=pd.DataFrame([dict(region='r',site_id='a',scene_id='s1',label=1,correct=1)]*100+
                       [dict(region='r',site_id='a',scene_id='s2',label=1,correct=0)])
        self.assertEqual(site_rates(d).correct.iloc[0],.5)

    def test_shared_scene_transitive_components(self):
        d=pd.DataFrame({'region':['a','b','b','c','d'],'Landsat.Product.Identifier.L1':['s1','s1','s2','s2','s3']})
        m=shared_scene_blocks(d)
        self.assertEqual(m['a'],m['c']);self.assertNotEqual(m['a'],m['d'])

if __name__=='__main__':unittest.main()
