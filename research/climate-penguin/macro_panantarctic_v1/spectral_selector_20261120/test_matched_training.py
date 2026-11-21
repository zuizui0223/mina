import unittest
import numpy as np
import pandas as pd
from fit_matched_training import fit_weights,evaluation_weights,threshold_table

class WeightTests(unittest.TestCase):
    def data(self):
        return pd.DataFrame(dict(site_id=['a']*6+['b']*2,scene_id=['s']*6+['t']*2,
          label=[1,1,0,0,0,0,1,0],score=[.8,.9,.1,.2,.3,.4,.95,.05]))

    def test_fit_equal_group_class_totals(self):
        d=self.data();d['w']=fit_weights(d)
        sums=d.groupby(['site_id','scene_id','label']).w.sum()
        self.assertTrue(np.allclose(sums,sums.iloc[0]));self.assertAlmostEqual(d.w.mean(),1)

    def test_evaluation_equal_sites_per_class(self):
        d=self.data();d['w']=evaluation_weights(d)
        self.assertTrue(np.allclose(d.groupby(['site_id','label']).w.sum(),.5))
        self.assertTrue(np.allclose(d.groupby('label').w.sum(),1))

    def test_thresholds_agree_with_direct_weighted_counts(self):
        d=self.data();w=evaluation_weights(d);t=threshold_table(d)
        for r in t.itertuples():
            self.assertAlmostEqual(r.positive_recovery,float(w[(d.label==1)&(d.score>=r.threshold)].sum()))
            self.assertAlmostEqual(r.candidate_background_rejection,float(w[(d.label==0)&(d.score<r.threshold)].sum()))

if __name__=='__main__':unittest.main()
