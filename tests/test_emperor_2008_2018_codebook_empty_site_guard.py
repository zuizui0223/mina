"""Public author-codebook guard: No = birds absent OR physical fast ice absent."""
import json
from pathlib import Path

R=json.loads((
    Path(__file__).resolve().parents[1]
    / "results/EMPEROR_2008_2018_SATELLITE_OCCUPANCY_CODEBOOK_GATE_V1.json"
).read_text(encoding="utf8"))


def test_no_does_not_mean_suitable_but_vacant():
    c=R["critical_primary_readme_definitions"]
    assert "OR no fast ice" in c["bpresent_No"]
    assert "not a known available vacant refuge" in R["state_logic"]["negative_composite"]
    assert R["causal_nonidentifiability"]["physically_no_breeding_platform_vs_social_unoccupied_platform_from_bpresent_No_alone"] is False


def test_missing_images_not_biological_zero():
    c=R["critical_primary_readme_definitions"]
    assert "No usable image" in c["bpresent_NA"]
    assert "not a biological zero" in R["state_logic"]["missing_composite"]
    assert "NOT proof" in c["catalog_id_blank_string"]


def test_positive_guano_not_successful_reproduction():
    assert "not necessarily successful breeding" in R["state_logic"]["positive_detected"]
    assert "not pair count" in R["critical_primary_readme_definitions"]["area_m2"]


def test_do_not_claim_new_cause_without_surveyed_ice_state():
    assert "INDEPENDENT_ICE_AND_SURVEY" in R["decision"]
    assert R["new_penguin_occupancy_effect_fitted"] is False
    assert R["frozen_pr189_unchanged"] is True
