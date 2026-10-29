"""Synthetic data tests for retrospective AADC potential-site ecological model.

Does not use any real biological observation. Independent-sample support gate,
training-only geography holdouts and disallowing NR as absence are tested.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

from evaluate_aadc_site_option_network_p_a_v1 import original_sample,evaluate_programme


def r(site, species, programme, status, season="201920"):
    return {
        "source_study":programme, "geog_site_id":site, "species_code":species,
        "season":season,"occurrence":status,
        "certainty_lookup":"EXACT_CERTAINTY_RULE",
        "occurrence_cert_cat":("5" if status=="P" else "4" if status=="A" else "0"),
        "vantage":"A","source_distance_station":"100",
        "occurrence_expert_validation":"Y","species_expert_validation":"Y",
        "site_expert_validation":"Y",
    }


def test_original_P_A_source_join_never_imputes_NR_or_duplicates():
    surveys=[
        r("Z1","ADP","penguin_original_search","P"),
        r("Z1","SK","flying_seabird_original_search","A"),
        r("Z2","ADP","penguin_original_search","A"),
        r("Z2","ADP","penguin_original_search","P"),
        r("Z3","ADP","penguin_original_search","NR"),
    ]
    geo=[{"geog_site_id":x,"latitude":"-75.0","longitude":"60.0",
          "geog_site_area":"1000","geog_site_feature":"island"}
         for x in ("Z1","Z2","Z3")]
    site_network=[{
        "geog_site_id":x,
        "original_site_id_present_in_2021_edition":True,
        "other_original_potential_site_centres_within_2km":0,
        "other_original_potential_site_centres_within_10km":7,
        "other_original_potential_site_centres_within_50km":44,
    } for x in ("Z1","Z2","Z3")]
    data,qa=original_sample(surveys,geo,site_network)
    assert len(data)==2
    assert qa["original_source_eligible_P_A_records"]==2
    assert set(data.source_programme)=={"ADELIE","FLYING"}
    assert set(data.outcome)=={0,1}
    assert all(np.isfinite(data.log1p_neighbor_10km))
    assert data.log1p_neighbor_10km.tolist()==[np.log(8),np.log(8)]


def mock_frame():
    """Balanced P/A in 3 spatially independent source-region blocks."""
    rows=[]
    for block in ("N","S","W"):
        for site in range(6):
            for year in range(3):
                rows.append({
                    "source_programme":"ADELIE",
                    "site_id":f"{block}-{site}",
                    "species":"ADP",
                    "block":block,
                    "year_scaled":0.05*year,
                    "latitude":-70.0-site/10,
                    "longitude_sin":0.1*(site%3),
                    "longitude_cos":0.9-0.02*site,
                    "log_area":1.0+(site%3)/3,
                    "island":float(site%2),
                    "log_station_distance":1.2+site/10,
                    "station_distance_missing":0.0,
                    "vantage_A":float(site%2),
                    "vantage_S":float((site+1)%2),
                    "expert_occurrence":1.0,
                    "expert_species":1.0,
                    "expert_site":1.0,
                    "original_site_id_in_2021":float(site%2),
                    "log1p_neighbor_10km":np.log1p(2+site%4),
                    "log1p_neighbor_2km":np.log1p(site%3),
                    "log1p_neighbor_50km":np.log1p(8+site),
                    "outcome":(site+year)%2,
                })
    return pd.DataFrame(rows)


def test_all_block_heldout_cv_and_frozen_10km_criterion():
    x=evaluate_programme(mock_frame(),"ADELIE")
    assert x["status"]=="EXPLORATORY_ORIGINAL_SURVEY_SPATIAL_CV_COMPLETED"
    assert x["post_250km_gate_250km_blocks"]==3
    assert x["post_250km_gate_original_sites"]==18
    assert x["post_250km_gate_source_rows"]==54
    assert x["unique_site_species_histories"]==18
    assert set(x["macro_equal_block_site_history_weighted_Brier"])=={
        "B0_source_area_and_effort", "B1_plus_10km_candidate_sites",
        "SENS_plus_2km_candidate_sites", "SENS_plus_50km_candidate_sites"
    }
    assert x["minimum_fixed_primary_support_blocks"]==2
    assert 0<=x["number_primary_blocks_with_Brier_gain"]<=3
    assert x["model_identifies_physical_island_or_sea_barrier_causation"] is False


def test_geographical_support_gate_refuses_one_block():
    data=mock_frame()
    data=data.loc[data.block=="N"]
    z=evaluate_programme(data,"ADELIE")
    assert z["status"]=="STOP_NOT_ENOUGH_ORIGINAL_INDEPENDENT_SPATIAL_SUPPORT"
    assert z["ecological_effect_fitted"] is False
