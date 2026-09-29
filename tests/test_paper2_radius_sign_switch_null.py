import unittest
try:
    import numpy as np
    import pandas as pd
    import pyreadr  # noqa: F401
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("Paper 2 radius-null tests require numpy/pandas/pyreadr") from exc

from scripts.run_paper2_radius_sign_switch_null import (
    permute_multiradius_within_blocks,
    radius_frame,
)

class RadiusPermutationTests(unittest.TestCase):
    def test_one_site_permutation_moves_complete_multiradius_tuple(self):
        rows=[]
        for i in range(4):
            rows.append({
                "unit_id":f"u{i}",
                "trait_block":"X",
                "A_1000":float(i),
                "H_1000":float(10+i),
                "AH_1000":float(20+i),
                "A_2000":float(30+i),
                "H_2000":float(40+i),
                "AH_2000":float(50+i),
                "A_5000":float(60+i),
                "H_5000":float(70+i),
                "AH_5000":float(80+i),
            })
        frame=pd.DataFrame(rows)
        out=permute_multiradius_within_blocks(
            frame,global_index=17,species_index=1,seed=20260929
        )
        cols=[
            "A_1000","H_1000","AH_1000",
            "A_2000","H_2000","AH_2000",
            "A_5000","H_5000","AH_5000",
        ]
        before=sorted(map(tuple,frame[cols].to_numpy()))
        after=sorted(map(tuple,out[cols].to_numpy()))
        self.assertEqual(before,after)

    def test_singleton_block_fixed(self):
        frame=pd.DataFrame({
            "unit_id":["a","b","c"],
            "trait_block":["X","X","Z"],
            "A_1000":[1.,2.,99.],"H_1000":[3.,4.,88.],"AH_1000":[3.,8.,8712.],
            "A_2000":[5.,6.,77.],"H_2000":[7.,8.,66.],"AH_2000":[35.,48.,5082.],
            "A_5000":[9.,10.,55.],"H_5000":[11.,12.,44.],"AH_5000":[99.,120.,2420.],
        })
        out=permute_multiradius_within_blocks(
            frame,global_index=4,species_index=0,seed=20260929
        )
        row=out.loc[out.trait_block=="Z"].iloc[0]
        self.assertEqual(float(row.A_1000),99.)
        self.assertEqual(float(row.A_2000),77.)
        self.assertEqual(float(row.A_5000),55.)

    def test_radius_frame_selects_matching_columns(self):
        frame=pd.DataFrame({
            "A_1000":[1.],"H_1000":[2.],"AH_1000":[2.],
            "A_2000":[3.],"H_2000":[4.],"AH_2000":[12.],
            "A_5000":[5.],"H_5000":[6.],"AH_5000":[30.],
        })
        out=radius_frame(frame,2000)
        self.assertEqual(float(out.A.iloc[0]),3.)
        self.assertEqual(float(out.H.iloc[0]),4.)
        self.assertEqual(float(out.AH.iloc[0]),12.)

if __name__=="__main__":
    unittest.main()
