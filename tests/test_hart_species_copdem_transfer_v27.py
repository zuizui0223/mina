"""Synthetic species-vs-original CopDEM terrain, geographical LOIO CV.

Simulated data only. The actual first-party nest point outcomes are accessed
by a separate GitHub Action after the prospective-relative-to-terrain contract.
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from evaluate_hart_species_copdem_transfer_v27 import (
    site_original_terrain,leave_one_island_terrain_transfer,ORIGINAL_LOCALITY_ORDER
)


def toy_terrain(flip=None):
    rng=np.random.default_rng(12345)
    arrays={}
    for i,site in enumerate(ORIGINAL_LOCALITY_ORDER):
        n=160
        # All x/y original nest centres are unique within site by construction.
        xy=np.column_stack((np.arange(2*n,dtype=float)*1.1+20000*i,
                            np.arange(2*n,dtype=float)*.3+8000*i))
        label=np.r_[np.zeros(n,dtype=np.uint8),np.ones(n,dtype=np.uint8)]
        direction=-1 if flip==site else +1
        elev=np.r_[rng.normal(30+i*10,3,n),
                   rng.normal(30+i*10+direction*20,3,n)]
        slope=np.r_[rng.normal(6,1.0,n),
                    rng.normal(6+direction*5,1.0,n)]
        arrays[site+"_xy"]=xy
        arrays[site+"_label"]=label
        arrays[site+"_DEM_elevation_m"]=elev
        arrays[site+"_DEM_slope_degrees"]=slope
    return arrays


def test_source_species_terrain_summary_respects_original_taxa():
    arrays=toy_terrain()
    X,y,meta=site_original_terrain(arrays,"Ashen_Hills")
    assert X.shape==(320,2)
    assert np.all(np.isfinite(X))
    assert list(sorted(np.unique(y)))==[0,1]
    assert meta["original_A_C_source_nest_counts"]=={"ADELIE":160,"CHINSTRAP":160}
    assert 15<meta["median_DSM_elevation_diff_Chinstrap_minus_Adelie_m"]<25
    assert 3<meta["median_DSM_slope_diff_Chinstrap_minus_Adelie_deg"]<7
    assert meta["source_orthomosaic_full_survey_footprint_verified"] is False


def test_exact_3_candidate_island_holdout_never_4_fake_islands():
    arrays=toy_terrain()
    siteX,siteY={},{}
    for site in ORIGINAL_LOCALITY_ORDER:
        siteX[site],siteY[site],_meta=site_original_terrain(arrays,site)
    out=leave_one_island_terrain_transfer(siteX,siteY)
    assert out["original_source_parent_named_island_count"]==3
    assert len(out["source_parent_island_heldout_cv_results"])==3
    assert out["original_localities_nested_within_heldout_islands"]=={
        "Ashen_Hills":"Saunders_Island",
        "Bellingshausen":"Bellingshausen_Island",
        "Beach_Point":"Thule_Island",
        "Hewison_Point":"Thule_Island",
    }
    assert out["source_parent_island_heldout_cv_results"]["Thule_Island"]["original_source_heldout_locality_list"]==["Beach_Point","Hewison_Point"]
    assert out["source_island_groups_with_positive_terrain_Brier_gain"]==3
    assert out["source_island_equal_weighted_mean_Brier_gain"]>0.12
    assert out["source_three_island_exploratory_terrain_transfer_gate"] is True
    assert out["raw_individual_nests_as_independent_island_replicates"] is False


def test_source_nan_and_colliding_points_do_not_enter_model():
    data=toy_terrain()
    data["Ashen_Hills_DEM_elevation_m"][0:100]=np.nan
    with pytest.raises(ValueError,match="GEOGRAPHY_STOP"):
        site_original_terrain(data,"Ashen_Hills")
    data=toy_terrain()
    data["Ashen_Hills_xy"][:150]=data["Ashen_Hills_xy"][0]
    with pytest.raises(ValueError,match="GEOGRAPHY_STOP"):
        site_original_terrain(data,"Ashen_Hills")
