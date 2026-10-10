"""Synthetic publisher location DMS and exact site identity tests."""
import importlib.util
from pathlib import Path
import pytest

SRC=Path(__file__).resolve().parents[1]/"scripts/audit_nz_2026_ross_geographic_parent_support_v16.py"
spec=importlib.util.spec_from_file_location("source_geo_v16",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_original_dms_coordinates_and_publisher_duplicate():
    assert m.dms("77°14'S","latitude")==pytest.approx(-77-14/60)
    assert m.dms("166°25'E","longitude")==pytest.approx(166+25/60)
    assert m.dms("66°39’S","latitude")==pytest.approx(-66-39/60)
    assert m.dms("77°14'E","latitude") is None
    assert m.dms("166°99'E","longitude") is None
    assert m.dms("unknown","longitude") is None

def test_exact_site_keys_keep_geographical_parent_descriptors():
    loc={
      "beaufort island":{"site":"Beaufort Island","parent_geographic_descriptor":"Southern Ross Sea","lat":-76-56/60,"lon":167+3/60},
      "beaufort island north":{"site":"Beaufort Island North","parent_geographic_descriptor":"Southern Ross Sea","lat":-76-56/60,"lon":167+3/60},
      "cape bird middle":{"site":"Cape Bird Middle","parent_geographic_descriptor":"Ross Island","lat":-77-14/60,"lon":166+25/60},
      "site orphan":{"site":"Site Orphan","parent_geographic_descriptor":"Unknown","lat":-75,"lon":168}
    }
    census={
      "beaufort island":{"name":"Beaufort Island","values":{1999:None,2001:123,2005:125,2024:200}},
      "beaufort island north":{"name":"Beaufort Island North","values":{1999:None,2001:None,2005:20,2024:30}},
      "cape bird middle":{"name":"Cape Bird Middle","values":{1999:12,2001:5,2005:40,2024:50}}
    }
    z=m.compare(loc,census)
    assert z["official_location_rows"]==4
    assert z["published_2026_count_sites"]==3
    assert z["literal_name_matched_sites"]==3
    assert z["only_in_location_not_census"]==["Site Orphan"]
    assert z["only_in_census_not_location"]==[]
    assert z["parent_geographic_descriptor_membership"]["Ross Island"]==["Cape Bird Middle"]
    assert z["n_site_pairs_with_valid_both_years"]=={
      "1999_2024":1,"2001_2024":2,"2005_2024":3
    }
    matches=z["distinct_site_labels_with_identical_source_representative_DMS"]
    assert len(matches)==1
    assert matches[0]["site_labels"]==["Beaufort Island","Beaufort Island North"]
    assert z["true_geographic_independent_island_count_confirmed"] is None
    assert z["no_immigration_recruitment_fitness_or_causal_effect_fitted"]

def test_name_only_site_fuzzy_substitution_disallowed():
    assert m.norm(" Cape  Bird North ")=="cape bird north"
    assert m.norm("Bird North")!="cape bird north"
    assert m.norm("Cape Bird Middle")!="cape bird north"

def test_contract_no_fabricated_39_separate_islands():
    import json
    c=json.loads((Path(__file__).resolve().parents[1]/
       "contracts/ROSS_NZ_COLONY_GEO_CROSSWALK_AND_PARENT_UNIT_V16.json").read_text())
    assert c["no_new_model_fit"]
    assert c["source_missing_value_not_zero"]
    assert c["Ecology_PR189_unchanged"]
    assert c["USAP_PR142_unchanged"]
