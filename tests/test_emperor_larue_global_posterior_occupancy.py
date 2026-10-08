"""Non-inferential audit regression tests for published 50×10 posterior table."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "emperor_larue_posterior",
    ROOT / "scripts/audit_larue_2024_global_posterior_occupancy_v1.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

D = json.loads(
    (ROOT / "results/EMPEROR_LARUE_2024_50_BY_10_POSTERIOR_ZERO_AUDIT_V1.json")
    .read_text(encoding="utf-8")
)


def test_retrospective_frozen_author_results_are_not_observed_biological_zero():
    assert D["site_count"] == 50
    assert D["posterior_site_years"] == 500
    assert D["years"] == [2009, 2018]
    assert D["posterior_mean_exact_zero_site_years"] == 15
    assert D["lower_95_bound_zero_site_years"] == 114
    assert D["nonzero_mean_but_lower_95_zero_site_years"] == 99
    assert D["upper_95_bound_zero_site_years"] == 15
    assert D["distinct_sites_with_a_zero_posterior_mean"] == 7
    assert D["exact_posterior_zero_is_verified_yearlong_ice_available_absence"] is False


def test_apparent_turnover_not_evidence_of_recolonization():
    assert D["apparent_mean_zero_to_positive_transitions"] == 9
    assert D["apparent_mean_positive_to_zero_transitions"] == 10
    assert len(D["apparent_zero_to_positive_events"]) == 9
    assert len(D["apparent_positive_to_zero_events"]) == 10
    assert D["mean_transition_is_confirmed_emigration_recolonization"] is False
    assert D["model_occupancy_z_s_t_iid_shared_p_no_lag_or_detection"]


def test_2016_halley_posterior_not_actual_spring_attendance():
    assert 5900 < D["halley_model_2016_posterior_mean"] < 6100
    assert D["halley_model_2016_posterior_lower_95"] == 0
    assert D["umbeashi_model_2018_posterior_mean"] == 0


def test_annual_stats_are_internally_balanced():
    annual = D["annual_support"]
    assert len(annual) == 10
    assert [x["year"] for x in annual] == list(range(2009, 2019))
    assert sum(y["exact_zero_posterior_mean"] for y in annual) == 15
    assert sum(y["zero_lower_95_bound"] for y in annual) == 114
    assert sum(y["zero_upper_95_bound"] for y in annual) == 15


def test_pinned_source_rejects_tampered_csv_and_missing_colony_ids():
    mini = (
        "year,site_id,N_mean,N_q025,N_q975\n"
        "2009,A,0,0,0\n2010,A,20,0,30\n"
    ).encode()
    with pytest.raises(ValueError, match="SHA_MISMATCH"):
        MODULE.read_rows(mini)
    parsed = MODULE.read_rows(mini, strict=False)
    assert parsed[0]["mean"] == 0
    assert parsed[1]["mean"] == 20
    with pytest.raises(ValueError, match="Unexpected supported site count"):
        MODULE.audit(parsed)


def test_no_new_fitted_causal_effect():
    assert D["scientific_effect_fit"] is False
    assert D["new_2022_plus_observational_rows_opened"] == 0
