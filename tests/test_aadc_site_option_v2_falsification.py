"""Synthetic V2 controls: historical geography, site-constant shuffle, block CV."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_aadc_site_option_v2_falsification import (
    cohort,comparison,historical_2021_point_neighbor_counts,
    shuffle_site_fixed_within_source_groups,controls
)


def toy():
    rows=[]
    for blk in ("0_1","1_2","2_3"):
        for sid in range(9):
            for year in range(2):
                rows.append({
                    "site_id":blk+"_"+str(sid),"species":"ADP",
                    "source_programme":"ADELIE","block":blk,
                    "year_scaled":year/10,"latitude":-70-sid/20,
                    "longitude_sin":0.1*sid,
                    "longitude_cos":0.8+0.01*sid,
                    "log_area":1+sid/10,"island":float(sid%2),
                    "log_station_distance":1.0+sid/10,
                    "station_distance_missing":0.0,
                    "vantage_A":float(sid%2),"vantage_S":float((sid+1)%2),
                    "expert_occurrence":1.0,"expert_species":1.0,
                    "expert_site":1.0,
                    "original_site_id_in_2021":float(sid%3==0),
                    "log1p_neighbor_10km":np.log1p(1+sid),
                    "log1p_neighbor_2km":np.log1p(sid),
                    "log1p_neighbor_50km":np.log1p(20+sid),
                    "outcome":int((sid+year)%2==0),
                })
    return pd.DataFrame(rows)


def test_original_cv_cohort_and_lean_exact():
    sample=cohort(toy(),"ADELIE")
    assert sample is not None
    assert sample.site_id.nunique()==27
    assert int(sample.weight.sum())==27
    result=comparison(sample,"log1p_neighbor_10km")
    assert result["spatial_blocks"]==3
    assert np.isfinite(result["B0"]["Brier_equal_block_mean"])
    assert np.isfinite(result["B1"]["Brier_equal_block_mean"])
    lean=comparison(sample,"log1p_neighbor_10km",lean=True)
    assert len(controls(sample,lean=True)) == len(controls(sample))-3
    assert np.isfinite(lean["Brier_improvement_B0_minus_B1"])


def test_historic_density_uses_all_old_reference_points_not_2025_only():
    sites={
        "A":{"lat":-78.0,"lon":150.0},
        "B":{"lat":-78.0,"lon":150.001},
        "OLDONLY":{"lat":-78.0,"lon":150.002},
        "C":{"lat":-75.0,"lon":0.0},
    }
    dens=historical_2021_point_neighbor_counts(sites,{"A","B"})
    assert dens=={"A":2,"B":2}


def test_site_level_shuffle_preserves_block_source_class_and_site_times():
    sample=cohort(toy(),"ADELIE")
    a,qa=shuffle_site_fixed_within_source_groups(
        sample,np.random.default_rng(20261026))
    assert a.site_id.nunique()==sample.site_id.nunique()
    assert qa["sites_in_non_singleton_source_groups"]>0
    assert 0 <= qa["fraction_sites_with_changed_covariate"]<=1
    assert a.groupby("site_id").permuted_10km.nunique().max()==1
    for _,group in a.groupby(["block","island","original_site_id_in_2021"]):
        site_rows=group.drop_duplicates("site_id")
        original=np.sort(site_rows.log1p_neighbor_10km.to_numpy())
        permuted=np.sort(site_rows.permuted_10km.to_numpy())
        np.testing.assert_allclose(original,permuted)
