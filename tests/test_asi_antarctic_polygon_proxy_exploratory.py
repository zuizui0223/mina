import unittest
import numpy as np
import pandas as pd
from scripts.fit_asi_antarctic_polygon_proxy_exploratory import fit_one

class TestSingleExploratoryModel(unittest.TestCase):
    def test_estimand_has_source_geo_and_site_clustered_variance(self):
        rng=np.random.default_rng(20261119)
        rows=[]
        for block in range(6):
            for site in range(8):
                group=int(site>=4)
                for species in ("ADPE","CHPE","GEPE"):
                    for year in range(2002,2006):
                        p=1/(1+np.exp(-(-0.4 + 0.25*group + 0.1*block +
                                        0.2*(species=="GEPE"))))
                        rows.append({
                            "Code":f"B{block}S{site}",
                            "spatial_block_100km":f"B{block}",
                            "species":species,"year_decades":(year-2006)/10,
                            "separate_source_polygon":group,
                            "log2_visits":1.0,
                            "breeding_confirmed":int(rng.random()<p)
                        })
        a,b=fit_one(pd.DataFrame(rows))
        self.assertTrue(np.isfinite(a.params["separate_source_polygon"]))
        self.assertTrue(np.isfinite(b.bse["separate_source_polygon"]))
        self.assertIn("separate_source_polygon",b.conf_int().index)
        self.assertGreater(len(rows),100)

if __name__=="__main__":
    unittest.main()
