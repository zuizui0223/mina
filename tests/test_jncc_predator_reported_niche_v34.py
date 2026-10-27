"""No JNCC wildlife outcomes: synthetic tests for first-party predator reporting-niche V34."""
from __future__ import annotations
import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
import model_jncc_predator_reported_niche_v34 as m
import pytest

def make_rows():
    # 20 independent archived source island groups; source-status labels
    # are NOT certified surveyed predator absences.
    rows=[]
    for j in range(20):
        for i in range(12):
            status="1" if i%2==0 else "0"
            rows.append({
                "area_ha":(i+1)*(j+1)*.1,
                "mlws_area_ha":(i+1)*(j+1)*.13,
                "population":i%3,
                "ferry":bool(i%4==0),
                "group":f"archipelago{j}",
                "status":{"American mink":status, "Brown rat":status},
            })
    return rows

def test_model_cannot_be_called_predator_occupancy():
    rows=make_rows()
    fit=m.fit_reported_status(rows,"American mink","confirmed_only")
    assert fit["status"]=="SOURCE_REPORTED_STATUS_NICHE_FIT_DESCRIPTIVE_NOT_OCCUPANCY"
    assert fit["n_original_islands"]==240
    assert fit["original_islands_with_target_report_status"]==120
    assert fit["model_does_not_return_real_predator_occupancy_probability"] is True
    assert len(fit["folds"])==5
    assert all(f["held_out_archipelago_count"]>=1 for f in fit["folds"])

def test_area_bin_original_units_hectares():
    rows=make_rows()
    result=m.tabulate(rows)
    assert result["overall_source_islands"]==240
    assert result["original_source_reported_0_not_surveyed_absence"] is True
    assert sum(b["n"] for b in result["area_bins"])==240
    assert result["original_islands_over_10ha_low_tide_area"] >= result["original_islands_over_10_ha"]
    assert result["over10ha_denominator_tide_definitions_are_distinct"]

def test_exact_lowid_and_not_name_required():
    island={1:{"name":"St_Marys","area_ha":2.1,"mlws_area_ha":2.5,"population":0,"ferry":"","group":"scilly","country":"england","coast":"southwest"}}
    esm={1:{"name":"st marys","statuses":{"American mink":"0","Brown rat":"1"}}}
    rows,r=m.generate_cohort(island,esm)
    assert len(rows)==1 and rows[0]["status"]["American mink"]=="0"
    assert r["exact_original_lowid_overlap_n"]==1
    esm={2:esm[1]}
    with pytest.raises(ValueError,match="LOWID_JOIN_NOT_EXACT"):
        m.generate_cohort(island,esm)

def test_status_table_is_not_true_occupancy():
    rows=make_rows()
    x=m.fit_reported_status(rows,"Brown rat","confirmed_or_probable")
    assert x["class_0_definition"]=="REMAINDER_OF_REPORTED_STATUSES_NOT_SURVEYED_ABSENCE"
    assert x["feature_coefficients_are_reporting_associations_not_invasion_or_predation_causes"] is True

def test_source_contract_fixed_predators_and_predictors():
    assert m.PREDATORS==("American mink","Brown rat")
    assert m.FIXED_FEATURES==(
        "log1p_high_tide_area_ha","log1p_resident_population","any_ferry_service"
    )
    assert m.ESM5_SHA == "3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5"
