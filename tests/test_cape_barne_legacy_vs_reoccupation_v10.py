"""Historical source narratives cannot become annual ecological zeros."""
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"scripts/audit_cape_barne_legacy_vs_reoccupation_v10.py"
spec=importlib.util.spec_from_file_location("cape_barne",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def contract():
    return json.loads((ROOT/"contracts/CAPE_BARNE_PERSISTENT_NEST_LEGACY_RECOLONIZATION_V10.json").read_text())

def test_published_event_timeline_has_physical_remnants_but_no_reoccupation():
    report=m.audit(contract())
    assert report["published_evidence_entries"]==6
    assert report["published_contemporary_occupied_nests_in_1988_89"]==5
    assert report["dec2024_physical_pebble_and_guano_remains"]
    assert report["dec2024_source_reports_site_still_abandoned"]
    assert report["chronological_elapsed_year_differences_NOT_absence_duration"]["years_from_1988_observed_nesting_to_2024_remnants"]==36
    assert report["historical_specific_year_zeros_inferred_from_unmonitored_periods"]==0
    assert not report["fitted_effect_size_or_pvalue"]

def test_missing_years_are_unknown_not_absent():
    report=m.audit(contract())
    assert report["site_survey_status_each_unsampled_gap"]["2002"]=="UNKNOWN_NOT_OBSERVED_ABSENT"
    assert report["no_unverified_annual_absence_imputation"]

def test_no_fake_modern_nest_count_or_breeding_success():
    c=contract()
    c["frozen_evidence_before_any_model"][-1]["breeding_pair_count"]=0
    with pytest.raises(ValueError):
        m.audit(c)
    c=contract()
    c["frozen_evidence_before_any_model"][2]["observed_breeding_success"]=True
    with pytest.raises(ValueError):
        m.audit(c)

def test_unconditional_sufficiency_cannot_be_licensed_by_source():
    c=contract()
    c["conclusions_supported"]["physical_remnants_alone_guarantee_breeding_reestablishment"]=True
    with pytest.raises(ValueError):
        m.audit(c)

def test_no_failed_pioneer_fate_or_colonist_causality():
    r=m.audit(contract())
    assert r["no_observed_genuinely_failed_pioneer_vs_never_used_patch_comparison"]
    assert r["no_independent_causal_immigration_or_ice_access_effect"]
    assert r["structural_example_only_not_novel_mechanistic_discovery"]
    assert r["PR189_frozen_unchanged"]
