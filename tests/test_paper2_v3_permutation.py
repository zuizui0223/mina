import unittest
import numpy as np
import pandas as pd

from scripts.run_paper2_v3_permutation import (
    permutation_bounds,
    permute_traits_within_blocks,
    holm_adjust,
)

class ShardTests(unittest.TestCase):
    def test_bounds_cover_9999_exactly(self):
        seen=[]
        for shard in range(20):
            a,b=permutation_bounds(9999,20,shard)
            seen.extend(range(a,b))
        self.assertEqual(seen,list(range(9999)))

class PermutationTests(unittest.TestCase):
    def test_tuple_permutation_stays_within_block_and_singleton_fixed(self):
        frame=pd.DataFrame({
            "unit_id":["a","b","c","d","e"],
            "trait_block":["X","X","Y","Y","Z"],
            "A":[1.,2.,10.,20.,99.],
            "H":[3.,4.,30.,40.,88.],
            "AH":[3.,8.,300.,800.,8712.],
        })
        out=permute_traits_within_blocks(frame,global_index=17,species_index=1,seed=20260929)
        for block in ("X","Y"):
            before=sorted(map(tuple,frame.loc[frame.trait_block==block,["A","H","AH"]].to_numpy()))
            after=sorted(map(tuple,out.loc[out.trait_block==block,["A","H","AH"]].to_numpy()))
            self.assertEqual(before,after)
        row=out.loc[out.trait_block=="Z"].iloc[0]
        self.assertEqual((row.A,row.H,row.AH),(99.,88.,8712.))

    def test_global_index_is_deterministic(self):
        frame=pd.DataFrame({
            "unit_id":[f"u{i}" for i in range(8)],
            "trait_block":["X"]*8,
            "A":np.arange(8,dtype=float),
            "H":np.arange(8,dtype=float)+10,
            "AH":np.arange(8,dtype=float)+20,
        })
        a=permute_traits_within_blocks(frame,global_index=123,species_index=0,seed=20260929)
        b=permute_traits_within_blocks(frame,global_index=123,species_index=0,seed=20260929)
        self.assertEqual(a[["A","H","AH"]].to_dict("records"),b[["A","H","AH"]].to_dict("records"))

class HolmTests(unittest.TestCase):
    def test_holm_adjustment(self):
        out=holm_adjust({"A":0.01,"B":0.04,"C":0.20})
        self.assertAlmostEqual(out["A"],0.03)
        self.assertAlmostEqual(out["B"],0.08)
        self.assertAlmostEqual(out["C"],0.20)

if __name__=="__main__":
    unittest.main()
