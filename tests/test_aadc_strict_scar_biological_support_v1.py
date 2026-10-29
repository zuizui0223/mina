"""Sample-support gates are not new biological effect estimates."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

from audit_aadc_strict_scar_biological_support_v1 import (
    select_unique_source_eligible,support,
)


def r(site="A",species="ADP",study="penguin_original_search",status="P",cat="5"):
    return {
        "source_study":study,
        "geog_site_id":site,
        "species_code":species,
        "occurrence":status,
        "occurrence_cert_cat":cat,
        "certainty_lookup":"EXACT_CERTAINTY_RULE",
        "season":"201920",
    }


def test_original_duplicates_and_NR_cannot_be_saved_by_polygon_filter():
    records=[
        r(),
        r(site="B",species="ADP",status="A",cat="4"),
        r(site="B",species="ADP",status="P",cat="5"),  # duplicate group removed
        r(site="C",species="ADP",status="NR",cat="0"),
        r(site="A",species="SK",study="flying_seabird_original_search",status="A",cat="4"),
        r(site="Z",species="SK",study="flying_seabird_original_search",status="P",cat="5"),
    ]
    chosen=select_unique_source_eligible(records)
    assert len(chosen)==3
    assert set((x["geog_site_id"],x["species_code"]) for x in chosen)=={
        ("A","ADP"),("A","SK"),("Z","SK")}
    assert all(x["occurrence"] in {"P","A"} for x in chosen)


def test_geometry_sample_failure_is_not_a_biological_null():
    surveys=[
        r(),
        r(site="A",species="SK",study="flying_seabird_original_search",status="A",cat="4"),
        r(site="B",species="ADP",status="A",cat="4"),
    ]
    sites={
        "A":{"lat":-70.0,"lon":70.0,"feature":"island"},
        "B":{"lat":-72.0,"lon":71.0,"feature":"continent"}
    }
    matched=[
        {"original_geographic_site_id":"A",
         "site_point_inside_whole_rock_with_same_parent_land":True,
         "point_land_feature_id":11},
        {"original_geographic_site_id":"B",
         "site_point_inside_whole_rock_with_same_parent_land":False,
         "point_land_feature_id":None}
    ]
    result=support(surveys,sites,matched)
    assert result["strict_site_ids_among_all_original_geography"]==1
    assert result["source_programme_strict_geography_support"]["ADELIE"]["distinct_original_source_geographic_sites"]==1
    assert result["source_programme_strict_geography_support"]["FLYING"]["distinct_original_source_geographic_sites"]==1
    assert result["cross_programme_future_sample_gate_passes"] is False
    assert result["scientific_decision"]=="STOP_CROSS_PROGRAMME_STRICT_GEOGRAPHY_SUPPORT"
    assert result["new_biological_effect_fitted"] is False
    assert result["original_source_NR_ever_recoded_to_absence"] is False
