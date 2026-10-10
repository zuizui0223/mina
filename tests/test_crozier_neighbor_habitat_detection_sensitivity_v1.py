"""Small synthetic fixtures for postpublication habitat/effort controls, not p-values."""
import importlib.util
from pathlib import Path
import pytest

FILE=Path(__file__).resolve().parents[1]/"scripts/audit_crozier_neighbor_habitat_detection_sensitivity_v1.py"
spec=importlib.util.spec_from_file_location("social_negctrl",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def data():
    o=[{"nestid":f"solo{i}","breeder":"1","cr_confirm":c}
       for i,c in ((1,"1"),(2,"0"),(3,"0"),(4,"0"))]
    l=[{"nestid":f"solo{i}","area":area,"rocksize_cm":str(rock),
         "dist_nearest_subcol_nest_m":"5"}
       for i,area,rock in [(1,"M",20),(2,"M",5),(3,"M",5),(4,"P",20)]]
    def v(i,date,n,status="INC"):
        return {"nestid":f"solo{i}","date":date,"n_neighbors":str(n),
                "egg_n":"2","chick_n":"","status":status}
    c=[v(1,"11/20/2021",0),v(1,"11/29/2021",1),
       v(2,"11/20/2021",0),v(2,"11/29/2021",0),
       v(3,"11/20/2021",0),v(3,"11/29/2021",0,"GONE"),
       v(4,"11/20/2021",0),v(4,"12/29/2021",2)]
    return c,o,l

def test_negative_controls_and_one_sided_logical_tipping():
    z=m.source_diagnostic(*data(),strict=False)
    assert z["n_original_breeding_sites"]==4
    assert z["main_counts"]["early_neighbor"]=={
        "n":1,"n_directly_confirmed_creche":1,
        "fraction_confirmation_not_survival":1}
    assert z["main_counts"]["none_detected"]["n"]==3
    assert z["areas_having_both_neighbor_states"]==["M"]
    assert z["explicit_GONE_check_by_cutoff"]=={
        "early_neighbor":0,"none_detected":1}
    assert z["exclude_explicit_GONE_from_source_risk_set_only"]["none_detected"]["n"]==2
    assert z["logical_ascertainment_tipping_min_additional_unconfirmed_creche_positive_no_neighbor"]==3
    assert z["source_cr_confirm_0_not_confirmed_chick_death"]
    assert not z["causal_social_protection_or_founding_claim_permitted"]

def test_post_cutoff_neighborhood_not_backdated():
    c,o,l=data()
    c.append({"nestid":"solo2","date":"12/30/2021","n_neighbors":"9",
              "egg_n":"2","chick_n":"","status":"BR"})
    z=m.source_diagnostic(c,o,l,strict=False)
    assert z["main_counts"]["early_neighbor"]["n"]==1

def test_original_nest_key_must_match_GPS():
    c,o,l=data()
    l[0]["nestid"]="solo5"
    with pytest.raises(ValueError,match="GPS nest identity"):
        m.source_diagnostic(c,o,l,strict=False)

def test_source_rock_outside_numeric_schema_must_hold():
    c,o,l=data()
    l[0]["rocksize_cm"]="NA"
    with pytest.raises(ValueError,match="Missing/invalid"):
        m.source_diagnostic(c,o,l,strict=False)
