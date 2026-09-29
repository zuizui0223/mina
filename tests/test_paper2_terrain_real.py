import numpy as np
import pandas as pd

from scripts.run_paper2_terrain_real import (
    ordered_score,
    permute_r_within_blocks,
)


def test_ordered_score_positive_only_for_frozen_species_order():
    assert ordered_score({"ADPE":-0.6,"CHPE":-0.2,"GEPE":0.1}) > 0
    assert ordered_score({"ADPE":-0.2,"CHPE":-0.4,"GEPE":0.1}) < 0
    assert ordered_score({"ADPE":0.1,"CHPE":0.2,"GEPE":0.3}) < 0


def test_permutation_preserves_R_multiset_within_each_block():
    frame=pd.DataFrame({
        "trait_block":["a","a","a","b","b"],
        "R":[-2.0,-1.0,1.0,4.0,8.0],
    })
    out=permute_r_within_blocks(
        frame,global_index=7,species_index=1,seed=20260946
    )
    for block in ("a","b"):
        before=sorted(frame.loc[frame["trait_block"].eq(block),"R"].tolist())
        after=sorted(out.loc[out["trait_block"].eq(block),"R"].tolist())
        assert after == before


def test_permutation_is_deterministic_and_changes_nontrivial_block():
    frame=pd.DataFrame({
        "trait_block":["a"]*6,
        "R":np.arange(6,dtype=float),
    })
    a=permute_r_within_blocks(frame,global_index=3,species_index=0,seed=20260946)
    b=permute_r_within_blocks(frame,global_index=3,species_index=0,seed=20260946)
    assert a["R"].tolist() == b["R"].tolist()
    assert a["R"].tolist() != frame["R"].tolist()
