from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "docs" / "MANUSCRIPT_CROSS_SCALE_CONCENTRATION_V0_1.md"
CONTRACT = ROOT / "contracts" / "CROSS_SCALE_CONCENTRATION_MANUSCRIPT_V0_1.json"
REGIONAL = ROOT / "results" / "MAPPPD_REGIONAL_CONCENTRATION_RECEIPT_V2.json"
PALMER = ROOT / "results" / "PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json"
SIGNY_A = ROOT / "results" / "SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json"
SIGNY_C = ROOT / "results" / "SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def unicode_percent(value: float) -> str:
    return f"{100.0 * value:.1f}%".replace("-", "−")


def test_cross_scale_manuscript_sources_exist_and_claim_is_bounded():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    contract = load(CONTRACT)

    assert "regional monitored site networks" in contract["central_claim"]
    assert "effect magnitude" in contract["central_claim"]
    assert "universal quarter-power law" in contract["prohibited_claims"]
    assert "universal seabird or colonial-breeder law" in contract["prohibited_claims"]

    assert "do not constitute a confirmatory regional hysteresis result" in manuscript
    assert "not treated as a universal scaling constant" in manuscript
    assert "monitored geographic networks, not assumed closed demographic populations" in manuscript


def test_local_primary_numbers_are_present():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    palmer = load(PALMER)
    signy_a = load(SIGNY_A)
    signy_c = load(SIGNY_C)

    assert unicode_percent(palmer["observed"]["COR"]["fractional_change"]) in manuscript
    assert unicode_percent(palmer["observed"]["HUM"]["fractional_change"]) in manuscript
    assert unicode_percent(palmer["observed"]["LIT"]["fractional_change"]) in manuscript
    assert "0.0380" in manuscript

    assert f"{signy_a['decline_eligibility']['first_total']:,.0f}" in manuscript
    assert f"{signy_a['decline_eligibility']['last_total']:,.0f}" in manuscript
    assert "−37.2%" in manuscript

    assert f"{signy_c['decline_eligibility']['first_total']:,.0f}" in manuscript
    assert f"{signy_c['decline_eligibility']['last_total']:,.0f}" in manuscript
    assert "−50.6%" in manuscript


def test_regional_panel_numbers_are_present_and_scope_matches_receipt():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    regional = load(REGIONAL)

    assert regional["support_gate"]["eligible_species_region_networks"] == 7
    assert regional["declining_network_synthesis"]["n"] == 4
    assert regional["declining_network_synthesis"]["positive_null_calibrated_kappa"] == 4
    assert regional["declining_network_synthesis"]["supported_under_both_nulls"] == 2

    declining = [p for p in regional["panels"] if p["direction"] == "decline"]
    assert len(declining) == 4
    assert all(p["delta_kappa_observation_error_null"] > 0 for p in declining)

    south = [p for p in declining if p["region"] == "South Shetland Islands"]
    assert len(south) == 2
    assert all(p["supported"] for p in south)

    increasing = [p for p in regional["panels"] if p["direction"] == "increase"]
    assert len(increasing) == 3
    assert all(p["last_E"] < p["first_E"] for p in increasing)

    assert "Seven passed the coverage-only fixed-roster gate" in manuscript
    assert "All four had positive observation-error-calibrated" in manuscript
    assert "p = 0.0148" in manuscript
    assert "p = 0.0152" in manuscript


def test_no_superseded_static_trait_story_is_reintroduced():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    forbidden = [
        "area × habitat-complex interactions were negative",
        "gamma_AH",
        "transferable static island",
        "MDE80",
    ]
    for phrase in forbidden:
        assert phrase not in manuscript
