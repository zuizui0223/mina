"""Source-frozen six-region descriptive benchmark; no new causal effect."""
from pathlib import Path
import importlib.util
import pytest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"scripts/audit_ross_2026_six_site_recovery_benchmark_v14.py"
spec=importlib.util.spec_from_file_location("ross_six_v14",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def original_source_fixture():
    vals={
      "Cape Bird Middle":(3333,1834,3937),
      "Cape Bird North":(32353,17334,44118),
      "Cape Bird South":(11664,7149,16629),
      "Cape Crozier East":(17055,7944,20494),
      "Cape Crozier West":(139386,59170,222187),
      "Cape Royds":(3620,1367,3058),
    }
    return {
      "status":"SOURCE_XLSX_VALIDATED_AND_STRUCTURAL_COVERAGE_REPORTED",
      "verified_md5":m.source.SOURCE_MD5,
      "focal_Royds_Crozier_CapeBird_source_counts":{
          k:dict(zip(("1999","2001","2024"),v)) for k,v in vals.items()},
      "surveyed_positive_zero_missing_by_year":{"2020":{"MISSING_BLANK":39}},
      "value_classes":{"POSITIVE_NUMERIC_COUNT":522,
                       "EXPLICIT_ZERO_SOURCE":2,"MISSING_BLANK":1192}
    }

def test_actual_source_frozen_six_site_sums_not_zero_filled():
    r=m.derive(original_source_fixture())
    assert r["same_named_site_count"]==6
    assert r["source_six_site_breeding_pair_totals"]=={
       "1999":207411,"2001":94798,"2024":310423}
    assert r["site_results"]["Cape Royds"]["1999_to_2024_fraction_change"]==pytest.approx(3058/3620-1)
    assert r["site_results"]["Cape Bird Middle"]["1999_to_2024_fraction_change"]==pytest.approx(3937/3333-1)
    assert r["source_all_39_site_year_cells"]==1716
    assert r["source_missing_entries"]==1192
    assert r["post_outcome_exploratory_not_confirmation"]
    assert r["no_new_causal_island_effect"]
    assert r["frozen_PR189_unmodified"]

def test_unknown_site_count_must_not_be_zero_filled_or_replaced():
    a=original_source_fixture()
    a["focal_Royds_Crozier_CapeBird_source_counts"]["Cape Royds"].pop("2024")
    with pytest.raises(ValueError,match="real recorded"):
        m.derive(a)

def test_bad_original_md5_must_halt():
    a=original_source_fixture()
    a["verified_md5"]="00000000000000000000000000000000"
    with pytest.raises(ValueError,match="MD5"):
        m.derive(a)

def test_six_risk_sites_are_not_independent_six_islands():
    x=m.derive(original_source_fixture())
    assert x["single_Ross_Island_six_subsites_not_six_independent_islands"]
    assert not x["georeferenced_2024_Cape_Barne_census_observation"]
    assert x["regional_pair_growth_not_individual_migration"]
    assert x["posterior_demographic_nest_recruitment_model_fitted"] is False

def test_source_yearly_coverage_math_must_reconcile():
    a=original_source_fixture()
    a["value_classes"]["MISSING_BLANK"]=1100
    with pytest.raises(ValueError,match="classification"):
        m.derive(a)
