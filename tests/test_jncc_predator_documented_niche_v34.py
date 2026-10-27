"""Synthetic tests: actual 2017 Stanbury data are fetched only in CI source job."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import model_jncc_predator_documented_niche_v34 as m


def _island(i, area, p=0, status="0"):
    return (
        {
            "low_tide_area_h": area,
            "latitude": 50.0+(i//10),
            "longitude": -5.0,
            "human_population": p,
        },
        {"lowid": i, "status_codes": {"American mink": status}},
    )


def test_area_bins_and_honest_sample_denominator():
    assert m.area_bin(10.01) == "(10,50] ha"
    assert m.area_bin(50) == "(10,50] ha"
    assert m.area_bin(60) == "(50,500] ha"
    assert m.area_bin(500) == "(50,500] ha"
    assert m.area_bin(501) == ">500 ha"
    with pytest.raises(ValueError):
        m.area_bin(10)


def test_only_strict_documented_source_0_1_2_modeled_without_forged_absences():
    island_info={}
    status_rows=[]
    for i,(area,code) in enumerate([(15,"1"),(50,"2"),(55,"3"),(7,"0"),(500,"0")]):
        info, rec=_island(i,area,0,code)
        island_info[i]=info
        status_rows.append(rec)
    cohort=m.source_cohort(island_info,status_rows)
    assert len(cohort)==4
    profile=m.cohort_descriptives(cohort,"American mink")
    assert profile["(10,50] ha"]["documented_confirmed_or_probable_n"]==2
    rows,dropped=m.make_model_arrays(cohort,"American mink")
    assert len(rows)==3
    assert dropped["source_status_possible3_or_unresolved"]==1
    assert sorted(r["y"] for r in rows)==[0,1,1]


def test_exact_full_lowid_matching_gate():
    info,rec=_island(1,20,status="1")
    with pytest.raises(ValueError,match="exact full"):
        m.source_cohort({1:info},[{"lowid":2,"status_codes":{"American mink":"1"}}])


def test_source_label_model_spatial_cv_does_not_reuse_geographic_cell():
    rows=[]
    for i in range(100):
        rows.append({
            "y":int(i % 10 < 4),
            "x":[2.5+(i%10)*0.02,50+(i//10),-4.8,0.0 if i%3 else 1.5],
            "group":f"{50+i//10}:-5",
            "lowid":i,"status":"1" if i%10<4 else "0","population":0
        })
    result=m.evaluate_spatial_label_model(rows)
    assert result["status"]=="GEOGRAPHICALLY_CROSSVALIDATED_ORIGINAL_SOURCE_LABEL_PREDICTION_ONLY"
    assert result["original_distinct_1degree_geographic_cells"]==10
    assert len(result["per_fold"])==5
    assert sum(x["islands_n"] for x in result["per_fold"])==100
    assert all(x["source_positive_n"]>=3 for x in result["per_fold"])
    assert "prevalence_null" in result["scores"]
    assert result["not_an_occupancy_probability_niche_model"] is True


def test_cv_stops_if_pos_label_confined_to_one_spatial_block():
    rows=[]
    for i in range(100):
        rows.append({
            "y":int(i<10),
            "x":[3.0,55.0 + i//10, -5.0, 0],
            "group":str(i//10),
        })
    r=m.evaluate_spatial_label_model(rows)
    assert r["status"]=="STOP_SPATIAL_LABEL_SUPPORT" or \
           r["status"]=="STOP_SPATIAL_TEST_FOLD_CLASS_IMBALANCE"
