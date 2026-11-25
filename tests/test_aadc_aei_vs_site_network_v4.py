"""Model comparison QA for frozen AEI versus site-density diagnostic."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from evaluate_aadc_aei_vs_site_network_v4 import (
    read_source_atlas,eligible_habitat_sample,compare_models
)


def test_habitat_match_keeps_source_nulls_missing_not_zero():
    d=pd.DataFrame({
        "geog_site_id":["A","B","A"],
        "source_programme":["ADELIE","FLYING","ADELIE"],
        "site_id":["A","B","A"]
    })
    # In the model, original_sample IDs are renamed before this join.
    d=d.drop(columns=["site_id"])
    atlas=pd.DataFrame({
        "geog_site_id":["A","B"],
        "source_AEI_habitat_covered":[True,False],
        "log1p_nonanimal_AEI_area_ha_2km":[np.log1p(15),np.nan],
        "nonanimal_AEI_tier2_richness_2km":[2.0,np.nan]
    })
    out,qa=eligible_habitat_sample(d,atlas)
    assert len(out)==2
    assert qa["source_missing_habitat_rows_excluded_not_zero_filled"]==1
    assert np.all(out.nonanimal_AEI_tier2_richness_2km==2)


def test_original_atlas_receipt_checks_source_hash_and_uncovered_cells(tmp_path):
    path=tmp_path/"atlas.csv"
    names=[
        "original_geographic_site_id",
        "nonanimal_mapped_icefree_area_projected_ha",
        "nonanimal_tier2_habitat_richness",
        "independently_mapped_habitat_coverage",
        "outcome_label_linked_pixels_excluded"
    ]
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=names)
        writer.writeheader()
        for i in range(7785):
            writer.writerow({
                "original_geographic_site_id":str(i),
                "nonanimal_mapped_icefree_area_projected_ha":
                    "5.0" if i%2==0 else "",
                "nonanimal_tier2_habitat_richness":
                    "1" if i%2==0 else "",
                "independently_mapped_habitat_coverage":i%2==0,
                "outcome_label_linked_pixels_excluded":0
            })
    rec={
        "status":"AADC_7785_INDEPENDENT_AEI_HABITAT_ATLAS_V3",
        "derived_7785_site_habitat_feature_CSV_SHA256":hashlib.sha256(
            path.read_bytes()).hexdigest(),
        "source_original_AADC_2025_geographic_site_count":7785,
        "original_AEI_raster_MD5":"cde880d73f7f18b44aecf5690aa2dc92",
    }
    receipt=tmp_path/"atlas.json"
    receipt.write_text(json.dumps(rec),encoding="utf-8")
    out,_=read_source_atlas(receipt,path)
    assert len(out)==7785
    assert out.source_AEI_habitat_covered.sum()==3893
    assert out.log1p_nonanimal_AEI_area_ha_2km.isna().sum()==3892
    path.write_bytes(path.read_bytes()+b" ")
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        read_source_atlas(receipt,path)


def toy():
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
                    "log1p_nonanimal_AEI_area_ha_2km":np.log1p(30+15*site),
                    "nonanimal_AEI_tier2_richness_2km":float(site%3+1),
                    "source_AEI_habitat_covered":True,
                })
    return pd.DataFrame(rows)


def test_fixed_four_models_same_cohort_and_independent_spatial_blocks():
    result=compare_models(toy(),"ADELIE")
    assert result["status"]=="EXPLORATORY_AEI_VS_CANDIDATE_SITE_NETWORK_SPATIAL_CV"
    assert result["source_original_sites"]==18
    assert result["source_P_A_rows"]==54
    assert result["eligible_250km_spatial_blocks"]==3
    assert len(result["equal_spatial_block_Brier_by_model"])==4
    assert len(result["Brier_gains"])==4
    assert all(np.isfinite(v) for v in result["equal_spatial_block_Brier_by_model"].values())
    assert result["causal_island_or_phylogenetic_function_effect_identified"] is False
