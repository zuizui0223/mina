"""Synthetic time-order evidence cannot be promoted into a causal effect."""
import importlib.util
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/"scripts/audit_crozier_neighbor_egg_temporal_order_v1.py"
spec=importlib.util.spec_from_file_location("crozier_order",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sources():
    outcome=[{"nestid":f"solo{i}","breeder":"1","cr_confirm":str(i%2)}
             for i in range(1,5)]
    gps=[{"nestid":f"solo{i}","rocksize_cm":"20","dist_nearest_subcol_nest_m":"4","area":"M"}
         for i in range(1,5)]
    def obs(i,day,n,e="",s=""):
        return {"nestid":f"solo{i}","date":day,"n_neighbors":str(n),"egg_n":e,
                "chick_n":"","status":s}
    checks=[
        obs(1,"11/18/2021",0,"2","INC"),
        obs(1,"11/22/2021",1,"2","INC"),
        obs(2,"11/18/2021",0),
        obs(2,"11/22/2021",1),
        obs(2,"11/26/2021",1,"2","INC"),
        obs(3,"11/18/2021",0),
        obs(3,"11/22/2021",1,"1","INC"),
        obs(4,"11/18/2021",0),
        obs(4,"11/22/2021",0,"2","INC")
    ]
    return checks,outcome,gps


def test_observed_egg_precedence_and_interval_censoring():
    z=m.ordered_source_audit(*sources(),strict=False)
    assert z["n_original_breeders"]==4
    assert z["n_neighbor_positive_before_cutoff"]==3
    assert z["n_neighbor_never_detected_before_cutoff"]==1
    assert z["first_detected_egg_relative_to_first_positive_neighbor"]=={
        "EGG_DETECTED_BEFORE_NEIGHBOR":1,
        "NEIGHBOR_DETECTED_BEFORE_FIRST_EGG_SIGHTING":1,
        "SAME_OBSERVATION_DAY":1
    }
    assert z["n_with_prior_observed_neighbor_zero"]==3
    assert z["n_with_incubation_detected_by_or_before_first_neighbor"]==2
    assert z["status_not_a_social_settlement_effect"]
    assert not z["neighbor_arrival_date_observed_without_interval_censoring"]
    assert not z["first_egg_sighting_equivalent_to_egg_laying_date"]


def test_later_neighbor_cannot_change_early_cutoff_group():
    checks,out,gps=sources()
    checks.append({"nestid":"solo4","date":"12/29/2021",
                   "n_neighbors":"6","egg_n":"2","status":"INC","chick_n":""})
    z=m.ordered_source_audit(checks,out,gps,strict=False)
    assert z["n_neighbor_never_detected_before_cutoff"]==1


def test_noncausal_frozen_safety():
    z=m.ordered_source_audit(*sources(),strict=False)
    assert z["source_result_from_same_already_exposed_cohort"]
    assert z["frozen_PR189_unmodified"]
    assert not z["new_confirmatory_causal_result"]


def test_egg_after_cutoff_must_stay_right_censored_not_counted_as_after_neighbor():
    checks, outcomes, gps = sources()
    # Original early-neighbor nest 2: its first egg is now documented only
    # after the Dec 1 event-time audit cutoff, not prior to egg laying.
    checks[4]["date"]="12/6/2021"
    z=m.ordered_source_audit(checks,outcomes,gps,strict=False)
    bins=z["first_detected_egg_relative_to_first_positive_neighbor"]
    assert bins["EGG_DETECTED_BEFORE_NEIGHBOR"]==1
    assert bins["SAME_OBSERVATION_DAY"]==1
    assert bins["NO_CONFIRMED_EGG_BY_CUTOFF"]==1
    assert "NEIGHBOR_DETECTED_BEFORE_FIRST_EGG_SIGHTING" not in bins
