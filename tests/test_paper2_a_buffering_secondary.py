import unittest
try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("A-buffering secondary tests require numpy/pandas") from exc

from scripts.run_paper2_a_buffering_secondary import (
    mode_frame,permute_A_within_blocks
)

class ModeTests(unittest.TestCase):
    def test_A_only_zeroes_H_and_interaction(self):
        f=pd.DataFrame({"A":[1.,2.],"H":[3.,4.],"AH":[3.,8.],"trait_block":["X","X"]})
        x=mode_frame(f,"A_only")
        self.assertEqual(x["H"].tolist(),[0.,0.])
        self.assertEqual(x["AH"].tolist(),[0.,0.])
        self.assertEqual(x["A"].tolist(),[1.,2.])

    def test_H_only_zeroes_A_and_interaction(self):
        f=pd.DataFrame({"A":[1.,2.],"H":[3.,4.],"AH":[3.,8.],"trait_block":["X","X"]})
        x=mode_frame(f,"H_only")
        self.assertEqual(x["A"].tolist(),[0.,0.])
        self.assertEqual(x["AH"].tolist(),[0.,0.])
        self.assertEqual(x["H"].tolist(),[3.,4.])

class PermutationTests(unittest.TestCase):
    def test_A_permutation_stays_within_block(self):
        f=pd.DataFrame({
            "A":[1.,2.,10.,20.,99.],"H":[3.,4.,5.,6.,7.],
            "AH":[3.,8.,50.,120.,693.],"trait_block":["X","X","Y","Y","Z"]
        })
        x=permute_A_within_blocks(f,global_index=11,species_index=2)
        for b in ("X","Y"):
            self.assertEqual(
                sorted(f.loc[f.trait_block==b,"A"].tolist()),
                sorted(x.loc[x.trait_block==b,"A"].tolist()),
            )
        self.assertEqual(float(x.loc[x.trait_block=="Z","A"].iloc[0]),99.)

if __name__=="__main__":
    unittest.main()
