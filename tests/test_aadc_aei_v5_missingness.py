"""Synthetic AEI coverage/post-result P/A selection diagnostics, no field-source access."""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_aadc_aei_v5_missingness import (
    classify_source_atlas,audit_missingness,CASES
)


def test_missingness_can_be_outcome_associated_without_being_causal():
    observations=pd.DataFrame([
        {"site_id":"A","source_programme":"ADELIE","outcome":1,
         "island":1.,"original_site_id_in_2021":1.},
        {"site_id":"A","source_programme":"ADELIE","outcome":1,
         "island":1.,"original_site_id_in_2021":1.},
        {"site_id":"B","source_programme":"ADELIE","outcome":0,
         "island":0.,"original_site_id_in_2021":0.},
        {"site_id":"C","source_programme":"FLYING","outcome":1,
         "island":1.,"original_site_id_in_2021":0.},
        {"site_id":"D","source_programme":"FLYING","outcome":0,
         "island":0.,"original_site_id_in_2021":1.},
    ])
    cases={"A":CASES[1],"B":CASES[0],"C":CASES[0],"D":CASES[2]}
    x=audit_missingness(observations,cases)
    ad=x["source_programme_outcome_and_mapping_missingness"]["ADELIE"]
    flying=x["source_programme_outcome_and_mapping_missingness"]["FLYING"]
    assert ad["P"]["AEI_coverage_class_row_counts"][CASES[1]]==2
    assert ad["A"]["fraction_rows_with_independent_AEI_habitat"]==1
    assert ad["P_minus_A_row_coverage_percentage_points"]==-100
    assert flying["P"]["fraction_rows_with_independent_AEI_habitat"]==1
    assert flying["A"]["fraction_rows_with_independent_AEI_habitat"]==0
    assert x["reporting_only_no_new_ecological_model_fitted"] is True
    assert x["P_A_coverage_difference_demonstrates_causal_biotic_island_effect"] is False


def test_original_AEI_classification_is_exact_and_complete(tmp_path):
    path=tmp_path/"features.csv"
    fields=["original_geographic_site_id","all_classified_icefree_pixel_count",
            "independent_nonanimal_mapped_pixel_count",
            "outcome_label_linked_pixels_excluded",
            "independently_mapped_habitat_coverage"]
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for i in range(7785):
            category=i%3
            n,nonanimal,animal=[(1,1,0),(1,0,1),(0,0,0)][category]
            w.writerow({
                "original_geographic_site_id":str(i),
                "all_classified_icefree_pixel_count":n,
                "independent_nonanimal_mapped_pixel_count":nonanimal,
                "outcome_label_linked_pixels_excluded":animal,
                "independently_mapped_habitat_coverage":bool(nonanimal)
            })
    rec={"status":"AADC_7785_INDEPENDENT_AEI_HABITAT_ATLAS_V3",
         "derived_7785_site_habitat_feature_CSV_SHA256":
             hashlib.sha256(path.read_bytes()).hexdigest(),
         "independent_breeding_habitat_summary":{
             "all_2025":{"sites_with_nonanimal_mapped_habitat_pixels":2595}
         }}
    summary=tmp_path/"summary.json"
    summary.write_text(json.dumps(rec),encoding="utf-8")
    status,report=classify_source_atlas(summary,path)
    assert len(status)==7785
    assert all(report["original_geography_only_source_class_case_counts"][k]==2595 for k in CASES)
    assert status["0"]==CASES[0]
    assert status["1"]==CASES[1]
    assert status["2"]==CASES[2]
