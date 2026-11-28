"""Published historical posterior mass-balance, not inferred disperser numbers."""
import importlib.util
import json
import math
from pathlib import Path

import pytest

BASE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "emperor_allocation",
    BASE/"scripts/audit_larue_2024_reappearance_mass_allocation_v1.py"
)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
D=json.loads((BASE/"results/EMPEROR_LARUE_PUBLISHED_REAPPEARANCE_GROSS_GAIN_ALLOCATION_V1.json").read_text(encoding="utf8"))


def test_historical_50_times_10_posterior_gross_mass_balance():
    assert D["authors_colony_years"] == 500
    assert D["number_sites"] == 50
    assert len(D["annual"]) == 9
    assert math.isclose(D["sum_gross_positive_posterior_mean_change_across_nine_year_transitions"],129460.42270602578,abs_tol=1e-5)
    assert math.isclose(D["sum_gross_negative_posterior_mean_change_across_nine_year_transitions"],152338.79433130194,abs_tol=1e-5)
    assert math.isclose(D["sum_of_model_zero_to_positive_allocated_mean_abundance"],10120.609144903716,abs_tol=1e-5)
    assert math.isclose(D["share_of_model_gross_positive_change_all_zero_to_positive"],.07817531360827736,abs_tol=1e-10)


def test_source_image_quality_split_constrains_model_reappearances():
    cats=D["image_evidence_categories"]
    a=cats[M.CAT_DATE]
    b=cats[M.CAT_LATE]
    c=cats[M.CAT_MISMATCH]
    assert [a["n"],b["n"],c["n"]] == [5,1,3]
    assert math.isclose(a["positive_mass"],6795.000275200345,abs_tol=1e-5)
    assert math.isclose(b["positive_mass"],2203.99712571883,abs_tol=1e-5)
    assert math.isclose(c["positive_mass"],1121.6117439845398,abs_tol=1e-5)
    assert math.isclose(a["share_of_all_model_gross_positive_change"],.05248708549816954,abs_tol=1e-10)
    assert a["n"]+b["n"]+c["n"]==9


def test_source_image_category_does_not_prove_breeding_or_ice_available():
    assert D["verified_prior_physically_available_but_empty_refuge_events"]==0
    assert D["confirmed_first_time_breeding_in_new_site_from_these_episodes"]==0
    assert D["biological_causal_effect_fitted"] is False
    assert D["previously_locked_PR189_and_external_PRs_unchanged"]


def test_tampered_historical_author_csv_rejected():
    raw=b"year,site_id,N_mean\n2009,A,0\n2010,A,12\n"
    with pytest.raises(ValueError,match="PINNED_PUBLISHED_AUTHOR_MODEL_CSV_BLOB_MISMATCH"):
        M.read_published_csv(raw)
    with pytest.raises(ValueError,match="pinned 50x10 source support changed"):
        M.read_published_csv(raw,enforce_pin=False)


def test_malformed_or_relabelled_model_reappearance_cannot_pass():
    fake={(f"S{i}",y):1. for i in range(50) for y in range(2009,2019)}
    raw=json.loads((BASE/"results/EMPEROR_LARUE_RAW_SATELLITE_TRANSITION_SUPPORT_V1.json").read_text(encoding="utf8"))
    with pytest.raises(ValueError,match="transition raw image receipts inconsistent"):
        M.audit(fake,raw["nine_posterior_transition_image_matches"])
