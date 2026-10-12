"""Synthetic noncausal Ross/off-Ross paired survey coverage tests."""
import importlib.util
from pathlib import Path
import pytest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/audit_ross_2001_2005_matched_offisland_source_v17.py"
spec=importlib.util.spec_from_file_location("ross_off17",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def synthetic():
    cen={
      "cape royds":{"name":"Cape Royds","values":{1999:9,2001:4,2005:6,2024:8}},
      "inexpressible island":{"name":"Inexpressible Island","values":{1999:None,2001:10,2005:15,2024:None}},
      "terra nova bay":{"name":"Terra Nova Bay","values":{1999:None,2001:10,2005:12,2024:None}},
      "franklin island east":{"name":"Franklin Island East","values":{1999:None,2001:1,2005:None,2024:None}},
      "unobserved habitat":{"name":"Unobserved Habitat","values":{1999:None,2001:None,2005:0,2024:None}},
    }
    loc={
      "cape royds":{"site":"Cape Royds","parent_geographic_descriptor":"Ross Island"},
      "inexpressible island":{"site":"Inexpressible Island","parent_geographic_descriptor":"Pennell Coast"},
      "franklin island east":{"site":"Franklin Island East","parent_geographic_descriptor":"Southern Ross Sea"}
    }
    return cen,loc

def test_source_paired_one_ross_one_off_one_unresolved_not_independent_islands():
    cen,loc=synthetic()
    z=m.compare_years(cen,loc)
    assert z["n_actual_numeric_pair_site_matches"]==3
    by=z["geographical_class_stratified_descriptive_pairs"]
    assert by["ROSS_ISLAND"]["n_matched_source_sites"]==1
    assert by["OFF_ROSS_SITE_WITH_SOURCE_GEOGRAPHY"]["n_matched_source_sites"]==1
    assert by["CENSUS_SITE_SOURCE_GEOGRAPHY_UNMATCHED"]["n_matched_source_sites"]==1
    assert by["CENSUS_SITE_SOURCE_GEOGRAPHY_UNMATCHED"]["site_name_roster"]==["Terra Nova Bay"]
    assert z["off_ross_actual_matched_numeric_sites"]==1
    assert z["previous_year_off_ross_1999_control_available_from_same_2026_table"] is False
    assert z["2024_off_ross_control_available_from_same_2026_table"] is False
    assert z["no_causal_new_island_biogeography_result"]

def test_missing_2001_or_2005_stays_absent_from_pair_and_source_zero_is_not_missing():
    cen,loc=synthetic()
    z=m.compare_years(cen,loc)
    assert "Franklin Island East" not in [r["source_site"] for r in z["source_site_detailed_pairs"]]
    assert "Unobserved Habitat" not in [r["source_site"] for r in z["source_site_detailed_pairs"]]

def test_invalid_negative_population_never_used_as_movement():
    cen,loc=synthetic()
    cen["cape royds"]["values"][2005]=-1
    with pytest.raises(ValueError):
        m.compare_years(cen,loc)

def test_source_frozen_before_actual_public_outcome():
    import json
    d=json.loads((Path(__file__).resolve().parents[1]/
        "contracts/ROSS_2001_2005_MATCHED_OFFISLAND_SOURCE_SUPPORT_V17.json").read_text())
    assert d["source_year_support_from_previous_gate"]["2001_numeric_sites"]==14
    assert d["source_year_support_from_previous_gate"]["2005_numeric_sites"]==18
    assert d["no_new_biological_causal_effect"]
    assert d["pr189_frozen"] and d["pr142_frozen"] and d["pr195_untouched"]
