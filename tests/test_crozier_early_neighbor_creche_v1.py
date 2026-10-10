"""Tests isolate outcome labels, cutoff time, and no causal claims."""
import importlib.util
from pathlib import Path
import pytest

FILE=Path(__file__).resolve().parents[1]/"scripts/screen_crozier_early_neighbor_creche_v1.py"
spec=importlib.util.spec_from_file_location("early_neighbor_screen",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    outcomes=[
        {"nestid":"solo1","breeder":"1","cr_confirm":"1"},
        {"nestid":"solo2","breeder":"1","cr_confirm":"0"},
    ]
    locations=[
        {"nestid":"solo1","dist_nearest_subcol_nest_m":"6",
         "rocksize_cm":"20","area":"M"},
        {"nestid":"solo2","dist_nearest_subcol_nest_m":"8",
         "rocksize_cm":"0","area":"C"}
    ]
    obs=[
        {"nestid":"solo1","date":"11/20/2021","n_neighbors":"0"},
        {"nestid":"solo2","date":"11/20/2021","n_neighbors":"0"},
        {"nestid":"solo1","date":"11/29/2021","n_neighbors":"2"},
        {"nestid":"solo2","date":"12/30/2021","n_neighbors":"5"},
    ]
    return obs,outcomes,locations


def test_2021_early_neighbor_does_not_leak_later_social_observation():
    checks,outcome,locations=fixture()
    d=m.score(checks,outcome,locations,require_original=False)
    early=d["cutoff_comparisons"]["2021-12-01"]
    assert early["pre_cutoff_social_neighbor_detected"]["n_nests"]==1
    assert early["pre_cutoff_social_neighbor_detected"]["n_creche_directly_confirmed"]==1
    assert early["pre_cutoff_social_neighbor_not_detected"]["n_nests"]==1
    assert early["pre_cutoff_social_neighbor_not_detected"]["n_creche_directly_confirmed"]==0
    assert early["no_exposure_observation_after_cutoff_used"] is True
    assert d["no_causal_social_rescue_or_predation_result"]
    assert d["not_a_confirmatory_preregistered_test"]


def test_time_cutoff_november24_before_new_social_neighbor():
    checks,outcome,locations=fixture()
    d=m.score(checks,outcome,locations,require_original=False)
    early=d["cutoff_comparisons"]["2021-11-24"]
    assert early["pre_cutoff_social_neighbor_detected"]["n_nests"]==0
    assert early["pre_cutoff_social_neighbor_not_detected"]["n_nests"]==2


def test_creche_nonconfirmation_not_interpreted_as_certain_death():
    checks,outcome,locations=fixture()
    d=m.score(checks,outcome,locations,require_original=False)
    assert d["outcome_detection_is_imperfect"]
    assert d["neighbor_acquisition_may_be_caused_by_earlier_egg_or_territory_quality"]
    assert d["no_pvalue"] and not d["PR189_frozen"] is False


def test_gps_nest_identity_mismatch_is_fatal():
    checks,outcome,locations=fixture()
    locations[1]["nestid"]="solo3"
    with pytest.raises(ValueError):
        m.score(checks,outcome,locations,require_original=False)
