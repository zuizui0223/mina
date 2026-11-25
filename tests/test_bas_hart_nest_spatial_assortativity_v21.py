"""Synthetic genuine nest coordinate spatial-label tests; no ecological causality."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyze_bas_hart_nest_spatial_assortativity_v21 import (
    locality_nearest_species_assortativity,analyze_all_point_sources
)


def sites():
    # Spatially separated species groups; label randomization preserves
    # original point process but breaks existing original label placement.
    xs=np.concatenate((np.arange(750)*0.2,np.arange(750)*0.2+300))
    yy=np.linspace(0,1,1500)
    xy=np.column_stack((xs,yy))
    labels=np.asarray([0]*750+[1]*750,dtype=np.uint8)
    return xy,labels


def test_local_original_source_conspecific_enrichment_vs_exchangeable_labels():
    xy,labels=sites()
    x=locality_nearest_species_assortativity(xy,labels,20261027,replicates=19)
    assert x["status"]=="BAS_NEST_NN_10M_FIXED_NULL_GEOMETRY_EXPLORATORY"
    assert x["source_species_point_count_after_duplicate_exclusion"]["ADELIE"]==750
    assert x["source_species_point_count_after_duplicate_exclusion"]["CHINSTRAP"]==750
    assert x["primary_local_10m_nests_with_nearest_neighbor_n"]==1500
    assert x["observed_heterospecific_nearest_nest_fraction_10m"]==0
    assert .4<x["positive_conspecific_enrichment_delta_nullminusobserved"]<.6
    assert x["permutation_199_heterospecific_nearest_nest_fraction_null"]["n_randomizations"]==19
    assert x["ecological_island_movement_or_interspecific_competition_causally_identified"] is False


def test_duplicate_nest_centres_source_stop_without_species_order_bias():
    xy,labels=sites()
    xy[:300]=xy[0]
    out=locality_nearest_species_assortativity(xy,labels,20261027,replicates=19)
    assert out["status"]=="STOP_EXCESSIVE_EXACT_COORDINATE_COLLISIONS"
    assert out["ecological_effect_fitted"] is False


def test_source_taxon_is_never_rescued_by_relabelling_low_count_species():
    xy,labels=sites()
    labels[-50:]=2  # 50 individual Gentoo, insufficient original source taxon.
    out=locality_nearest_species_assortativity(xy,labels,20261027,replicates=19)
    assert out["status"]=="STOP_ANY_SOURCE_TAXON_TOO_SMALL_FOR_FROZEN_COHORT"
    assert out["ecological_effect_fitted"] is False


def test_site_level_null_does_not_independently_replicate_Thule():
    xy,lab=sites()
    arrays={}
    for name in ("Ashen_Hills","Bellingshausen","Beach_Point","Hewison_Point"):
        arrays[name+"_xy"]=xy
        arrays[name+"_label"]=lab
    report={"status":"BAS_HART_ORIGINAL_10_SPECIES_NEST_CSV_SOURCE_V20",
            "source_species_original_file_validation":[]}
    for name in ("Ashen_Hills","Bellingshausen","Beach_Point","Hewison_Point"):
        report["source_species_original_file_validation"] += [
            {"source_original_locality":name,"original_row_count":750},
            {"source_original_locality":name,"original_row_count":750}
        ]
    # Test synthetic helper with 19 instead of full 199 via monkeypatch at
    # module level to keep CI fast.
    import analyze_bas_hart_nest_spatial_assortativity_v21 as mod
    original=mod.locality_nearest_species_assortativity
    def quick(arr,lbl,seed):
        return original(arr,lbl,seed,replicates=19)
    mod.locality_nearest_species_assortativity=quick
    try:
        result=analyze_all_point_sources(report,arrays)
    finally:
        mod.locality_nearest_species_assortativity=original
    assert result["original_successful_localities"]==4
    assert result["candidate_island_equal_weight_mean_conspecific_enrichment_delta"]["n_provisional_independent_named_islands"]==3
    assert result["general_Antarctic_island_biogeography_law_confirmed"] is False
