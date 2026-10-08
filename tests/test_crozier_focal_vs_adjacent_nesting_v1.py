"""Synthetic-only source-unit tests; source cohort already outcome exposed."""
import importlib.util
from pathlib import Path
import pytest

FILE=Path(__file__).resolve().parents[1]/"scripts/audit_crozier_focal_vs_adjacent_nesting_v1.py"
spec=importlib.util.spec_from_file_location("focal_neighbor",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def sample():
    a=[{"nestid":"solo1","breeder":"0"},
       {"nestid":"solo2","breeder":"0"},
       {"nestid":"solo3","breeder":"1"}]
    s=[{"nestid":"solo1"},{"nestid":"solo2"},{"nestid":"solo3"}]
    f=[
        {"nestid":"1","date":"12/05/2022","status":"MT","n_neighbors":"1","notes":"adjacent nest"},
        {"nestid":"2","date":"12/05/2022","status":"INC?","n_neighbors":"2","notes":"uncertain focal"},
        {"nestid":"3","date":"12/05/2022","status":"INC","n_neighbors":"0","notes":"focal active"},
        {"nestid":"1","date":"12/15/2023","status":"INC","n_neighbors":"5","notes":"INVALID FUTURE"}
    ]
    return a,s,f

def test_focal_vs_adjacent_nest_separate_support_and_date():
    v=m.analyze(*sample(),strict=False)
    g=v["groups"]["original_2021_nonbreeders"]
    assert g["n_original_sites"]==2
    assert g["n_sites_with_positive_nearby_nest_count"]==2
    assert g["n_sites_with_strict_focal_occupancy"]==0
    assert g["n_neighbor_positive_without_strict_focal_occupancy"]==2
    assert g["n_stated_empty_focal_site_near_neighbor"]==1
    assert v["groups"]["original_2021_breeders"]["n_sites_with_strict_focal_occupancy"]==1
    assert v["out_of_window_or_unparseable_records"]["DATE_OUTSIDE_2022_2023_SEASON"]==1
    assert not v["new_colony_founder_origin_identified"]
    assert not v["adjacent_nest_success_or_marked_breeder_identified"]

def test_INC_question_is_unknown_not_positive_focal_occupation():
    v=m.analyze(*sample(),strict=False)
    a=v["positive_nearby_nesting_where_original_focal_not_confirmed"]
    assert len(a)==2
    assert {x["nest_id"] for x in a}=={"solo1","solo2"}
    assert v["original_focal_2022_absence_proven_in_ambiguous_INC_question_sites"] is False

def test_orig_focal_roster_mismatch_is_not_silent():
    a,s,f=sample()
    a[0]["nestid"]="solo7"
    with pytest.raises(ValueError,match="GPS"):
        m.analyze(a,s,f,strict=False)
