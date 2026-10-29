"""Post-observation source-geography-conditioned nested-patch null unit tests."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyze_bas_hart_spatial_cell_label_controls_v22 import (
    recover_primary_point_neighbors,per_source_geo_null
)


def two_species_separated_within_one_100m_cell():
    # Both taxa share the same 100m patch but segregate on 20m subpatches.
    a=np.column_stack((np.linspace(0,30,750),np.full(750,20.)))
    b=np.column_stack((np.linspace(60,90,750),np.full(750,20.)))
    return np.vstack((a,b)),np.r_[np.zeros(750,np.uint8),np.ones(750,np.uint8)]


def test_same_patch_two_species_have_power_to_test_fine_grain_arrangement():
    xy,labels=two_species_separated_within_one_100m_cell()
    x,l,nn,ok=recover_primary_point_neighbors(xy,labels)
    out=per_source_geo_null(x,l,nn,ok,100.,(0.,0.),20261026,nsim=19)
    assert out["status"]=="CELL_CONDITIONAL_LABEL_NULL_REPORTABLE"
    assert out["mixed_species_source_grid_cell_n"]==1
    assert out["fraction_original_NN_eligible_source_nests_in_mixed_species_grid_cells"]==1.
    assert out["original_observed_heterospecific_NN_fraction"]==0.
    assert out["source_within_cell_local_segregation_delta_nullminusobserved"]>.35
    assert out["underpowered_source_cell_mixing_not_proof_no_competition"] is False
    assert out["within_cell_exchangeable_species_label_null"]["n_permutations"]==19


def test_different_monoculture_grids_mark_uninformative_no_microscale_mechanism():
    xy,labels=two_species_separated_within_one_100m_cell()
    xy[labels==1,0]+=150
    x,l,nn,ok=recover_primary_point_neighbors(xy,labels)
    out=per_source_geo_null(x,l,nn,ok,100.,(0.,0.),20261026,nsim=19)
    assert out["status"]=="GEOGRAPHIC_MIXED_PATCH_SUPPORT_HOLD"
    assert out["mixed_species_source_grid_cell_n"]==0
    assert out["fraction_original_NN_eligible_source_nests_in_mixed_species_grid_cells"]==0
    assert out["source_within_cell_local_segregation_delta_nullminusobserved"]==0
    assert out["underpowered_source_cell_mixing_not_proof_no_competition"] is True


def test_frozen_null_cannot_choose_favorable_posthoc_cell_size():
    xy,labels=two_species_separated_within_one_100m_cell()
    x,l,nn,ok=recover_primary_point_neighbors(xy,labels)
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        per_source_geo_null(x,l,nn,ok,30.,(0,0),20261026,nsim=19)


def test_duplicate_position_replay_keeps_original_utm_nest_uniqueness():
    xy,labels=two_species_separated_within_one_100m_cell()
    xy=np.concatenate((xy,xy[:3]))
    labels=np.concatenate((labels,labels[:3]))
    clean,lab,nn,eligible=recover_primary_point_neighbors(xy,labels)
    assert len(clean)==1497
    assert np.count_nonzero(eligible)>1450
